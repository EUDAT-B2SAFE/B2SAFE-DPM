#!/usr/bin/env python
# Script to configure the DPM
#
import getopt
import sys
import os
import ConfigParser
import sqlite3
import subprocess
import string
import shutil
import xml.etree.ElementTree


def usage():
    '''Function describing the script usage
    '''
    print 'Configure the Data Policy Manager.'
    print 'Usage: configure_dpm.py [-h][-f][-c <config>]'
    print ''
    print 'Options:'
    print '-h, --help                 Print this help'
    print '-f, --force                Forces the repopulation of the databases'
    print '-c, --config=<configfile>  A config file containing the input'
    print '                           parameters.'
    print ''


def create_tables(conn, cfg, dbtype):
    '''Function to create the db tables
    '''
    cur = conn.cursor()
    if dbtype == 'resource':
        cur.execute(cfg.get("CREATE", "systems"))
        cur.execute(cfg.get("CREATE", "resources"))
        cur.execute(cfg.get("CREATE", "storage"))
        cur.execute(cfg.get("CREATE", "sites"))
    elif dbtype == 'action':
        cur.execute(cfg.get("CREATE", "trigger"))
        cur.execute(cfg.get("CREATE", "type"))
        cur.execute(cfg.get("CREATE", "persistentid"))
        cur.execute(cfg.get("CREATE", "organisation"))
        cur.execute(cfg.get("CREATE", "trigger_date"))
    elif dbtype == 'profile':
        cur.execute(cfg.get("CREATE", "dpm_page"))
        cur.execute(cfg.get("CREATE", "roles"))
        cur.execute(cfg.get("CREATE", "status"))
        cur.execute(cfg.get("CREATE", "community"))
        cur.execute(cfg.get("CREATE", "user"))
        cur.execute(cfg.get("CREATE", "user_community"))
        cur.execute(cfg.get("CREATE", "dpm_date"))
    conn.commit()


def get_next_profile_indexes(conn, cfg):
    '''Function to get the next unused indexes for the profile tables
    '''
    cur = conn.cursor()
    next_indexes = {}
    next_indexes['dpm_page'] = 0
    next_indexes['roles'] = 0
    next_indexes['status'] = 0
    next_indexes['community'] = 0

    cur.execute(cfg.get("QUERY", "max_dpm_page"))
    max_dpm_page = cur.fetchall()
    if max_dpm_page:
        next_indexes["dpm_page"] = max_dpm_page[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_community"))
    max_community = cur.fetchall()
    if max_community:
        next_indexes["community"] = max_community[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_roles"))
    max_role = cur.fetchall()
    if max_role:
        next_indexes["roles"] = max_role[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_status"))
    max_status = cur.fetchall()
    if max_status:
        next_indexes["status"] = max_status[0][0] + 1

    return next_indexes


def get_next_actions_indexes(conn, cfg):
    '''Function to get the next unused indexes for the actions tables
    '''
    cur = conn.cursor()
    next_indexes = {}
    next_indexes['type'] = 0
    next_indexes['trigger'] = 0
    next_indexes['trigger_date'] = 0
    next_indexes['persistentid'] = 0
    next_indexes['organisation'] = 0

    cur.execute(cfg.get("QUERY", "max_trigger_date"))
    max_trigger_date = cur.fetchall()
    if max_trigger_date:
        next_indexes['trigger_date'] = max_trigger_date[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_trigger"))
    max_triggers = cur.fetchall()
    if max_triggers:
        next_indexes['triggers'] = max_triggers[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_type"))
    max_type = cur.fetchall()
    if max_type:
        next_indexes['type'] = max_type[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_persistentid"))
    max_persistent_id = cur.fetchall()
    if max_persistent_id:
        next_indexes['persistentid'] = max_persistent_id[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_organisation"))
    max_organisation = cur.fetchall()
    if max_organisation:
        next_indexes['organisation'] = max_organisation[0][0] + 1

    return next_indexes


def get_next_resources_indexes(conn, cfg):
    '''Function to get the next unused indexes for the resources tables
    '''
    cur = conn.cursor()
    next_indexes = {}
    next_indexes['system'] = 0
    next_indexes['resource'] = 0
    next_indexes['site'] = 0
    next_indexes['storage'] = 0

    cur.execute(cfg.get("QUERY", "max_systems"))
    max_systems = cur.fetchall()
    if max_systems:
        next_indexes['system'] = max_systems[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_sites"))
    max_sites = cur.fetchall()
    if max_sites:
        next_indexes['site'] = max_sites[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_resources"))
    max_resources = cur.fetchall()
    if max_resources:
        next_indexes['resource'] = max_resources[0][0] + 1

    cur.execute(cfg.get("QUERY", "max_storage"))
    max_storage = cur.fetchall()
    if max_storage:
        next_indexes['storage'] = max_storage[0][0] + 1

    return next_indexes


def get_goc_info(data):
    '''Get the resource information from the GOCDB'''

    out_data = []

    # get the data and put the information into a xml object
    command = ["curl", data["resource_data"]]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, error = proc.communicate()
    return_code = proc.poll()
    if return_code:
        print "Error: Unable to wget information from the gocdb %s" %\
            (data["resource_data"])
        print "return code: ", return_code
        if output:
            print "Message: \n"
            print output
        if error:
            print "Error: \n"
            print error
    else:
        goc_root = xml.etree.ElementTree.fromstring(output)
        for spoint in goc_root.getchildren():
            irods_path = ""
            irods_zone = ""
            irods_resc = ""
            host = ""
            for elem in spoint.getchildren():
                if elem.tag == "HOSTNAME":
                    # print "host ", elem.text
                    host = elem.text
                if elem.tag == "EXTENSIONS":
                    irods_details = elem.getchildren()
                    if irods_details:
                        for irods_elem in irods_details:
                            t_irods_path = get_irods_elem(irods_elem,
                                                          "irods_path")
                            if t_irods_path:
                                irods_path = t_irods_path

                            t_irods_zone = get_irods_elem(irods_elem,
                                                          "irods_zone")

                            if t_irods_zone:
                                irods_zone = t_irods_zone

                            t_irods_resc = get_irods_elem(irods_elem,
                                                          "irods_resource")
                            if t_irods_resc:
                                irods_resc = t_irods_resc

                        if irods_resc and irods_zone:
                            data_str = "iRODS|%s|%s|%s|%s" % \
                                (host, irods_resc, irods_zone, irods_path)
                        out_data.append(data_str)
    return out_data


def get_irods_elem(root_elem, key):
    '''return the value for the root element'''
    elem_ok = False
    elem_value = ""
    for elem in root_elem.getchildren():
        if elem.tag == "KEY" and elem.text == key:
            elem_ok = True
        if elem.tag == "VALUE" and elem_ok:
            elem_value = elem.text
    return elem_value


def fill_resource(conn, config, next_indexes, data):
    '''Fill the resource database
    '''

    # Get the resource data from the GOCDB
    data = get_goc_info(data)

    site_count = 0
    system_count = 0
    storage_count = 0
    resource_count = 0
    cur = conn.cursor()
    for row in data:
        system, site, store, zone, path = row.split('|')
        system = system.strip()
        site = site.strip()
        store = store.strip()
        system_IOK, system_count = fill_table(cur, config,
                                              "systems",
                                              next_indexes['system'],
                                              system)
        if system_IOK:
            next_indexes['system'] = system_count

        site_IOK, site_count = fill_table(cur, config,
                                          "sites",
                                          next_indexes['site'], site)
        if site_IOK:
            next_indexes['site'] = site_count

        storage_IOK, storage_count = fill_table(cur, config,
                                                "storage",
                                                next_indexes['storage'],
                                                store, path)
        if storage_IOK:
            next_indexes['storage'] = storage_count

        cur.execute(config.get("QUERY", "resources"),
                    (system_count-1, site_count-1, storage_count-1))
        resources = cur.fetchall()
        res_id = 'resource'
        if not resources:
            cur.execute(config.get("INSERT", "resources"),
                        (next_indexes[res_id], site_count-1, storage_count-1,
                         system_count-1))
            resource_count = next_indexes[res_id]
            resource_count += 1
            next_indexes[res_id] = resource_count
        else:
            resource_count = int(resources[0][0]) + 1

    conn.commit()


def fill_table(cur, config, table, idx, val, *values):
    '''Fill the table
    '''
    insert_ok = False
    cur.execute(config.get("QUERY", table), (val,))
    vals = cur.fetchall()
    if not vals:
        if not values:
            cur.execute(config.get("INSERT", table),
                        (idx, val))
        else:
            params = []
            params.append(idx)
            params.append(val)
            params = params + list(values)
            cur.execute(config.get("INSERT", table), params)
        insert_ok = True
        idx += 1
    else:
        idx = int(vals[0][0]) + 1

    return (insert_ok, idx)


def fill_profile(conn, config, next_indexes, data):
    '''Fill the profile database
    '''
    cur = conn.cursor()

    # Fill the community
    for row in file(data["profile_community"], "r"):
        community = row.strip()
        community_OK, community_count = fill_table(cur, config,
                                                   "community",
                                                   next_indexes["community"],
                                                   community)
        if community_OK:
            next_indexes["community"] = community_count

    # Fill the dpm_page
    for row in file(data["profile_page"], "r"):
        dpm_page, name = row.split('|')
        cur.execute(config.get("QUERY", "dpm_page"),
                    (next_indexes["dpm_page"],))
        vals = cur.fetchall()
        if not vals:
            cur.execute(config.get("INSERT", "dpm_page"),
                        (next_indexes["dpm_page"], dpm_page.strip(),
                         name.strip()))
            next_indexes["dpm_page"] = next_indexes["dpm_page"] + 1

    # Fill the status
    for row in file(data["profile_status"], "r"):
        status = row.strip()
        status_OK, status_count = fill_table(cur, config, "status",
                                             next_indexes["status"], status)
        if status_OK:
            next_indexes["status"] = status_count

    # Fill the roles
    for row in file(data["profile_role"], "r"):
        role = row.strip()
        role_OK, role_count = fill_table(cur, config, "roles",
                                         next_indexes["roles"], role)
        if role_OK:
            next_indexes["roles"] = role_count

    conn.commit()


def fill_action(conn, config, next_indexes, data):
    '''Fill the action database
    '''
    cur = conn.cursor()
    atype_count = 0
    atrigger_count = 0

    # Fill the action type table table from the ascii file
    for row in file(data["action_action_data"], "r"):
        atype = row.strip()
        atype_IOK, atype_count = fill_table(cur, config, "type",
                                            next_indexes["type"], atype)
        if atype_IOK:
            next_indexes['type'] = atype_count

    # Fill the action trigger table from the ascii file
    for row in file(data['action_trigger_data'], 'r'):
        if ('##' in row):
            print 'we are skipping row ', row
            continue
        atrigger = row.strip()
        atrigger_IOK, atrigger_count = fill_table(cur, config,
                                                  "trigger",
                                                  next_indexes["trigger"],
                                                  atrigger)
        if atrigger_IOK:
            next_indexes['trigger'] = atrigger_count

    conn.commit()

    # Fill the action date table from the ascii file
    cur = conn.cursor()
    for row in file(data['action_date_data'], 'r'):
        entries = row.split('|')
        if len(entries) == 2:
            adate = entries[0].strip()
            avalue = entries[1].strip()
        else:
            adate = entries[0].strip()
        adate_IOK, adate_count = fill_table(cur, config, "trigger_date",
                                            next_indexes["trigger_date"],
                                            adate, avalue)
        if adate_IOK:
            next_indexes['trigger_date'] = adate_count
    conn.commit()

    # Now do the organisation and persistent id tables
    cur = conn.cursor()
    org_count = 0
    pid_count = 0
    for row in file(data["action_org_data"], "r"):
        org, pid = row.split('|')
        org = org.strip()
        pid = pid.strip()
        org_IOK, org_count = fill_table(cur, config,
                                        "organisation",
                                        next_indexes["organisation"], org)
        if org_IOK:
            next_indexes['organisation'] = org_count

        pid_IOK, pid_count = fill_table(cur, config,
                                        "persistentID",
                                        next_indexes["persistentid"], pid)
        if pid_IOK:
            next_indexes['persistentid'] = pid_count

    conn.commit()


def populate(dbfile, dbschema, dbdata, dbtype, force_flag):
    '''Populate the databases
    '''
    print "the dbfile is ", dbfile
    if os.path.isfile(dbfile):
        if force_flag is True:
            print 'Repopulating database %s.' % dbfile
        else:
            return
    else:
        print 'Uploading data to the %s database' % dbtype
        if not os.path.isdir(os.path.dirname(dbfile)):
            os.makedirs(os.path.dirname(dbfile))

    # Get the resource information from the GOCDB

    # Open the database
    # print "database ", dbfile
    conn = sqlite3.connect(dbfile)

    # read in the schema config
    config = ConfigParser.ConfigParser()
    config.read(dbschema)

    # Create the database tables
    create_tables(conn, config, dbtype)

    # Get the next unused indexes for the tables
    next_indexes = {}
    if dbtype == 'resource':
        next_indexes = get_next_resources_indexes(conn, config)
    elif dbtype == 'action':
        next_indexes = get_next_actions_indexes(conn, config)
    elif dbtype == 'profile':
        next_indexes = get_next_profile_indexes(conn, config)

    # Fill the databases
    if dbtype == 'resource':
        fill_resource(conn, config, next_indexes, dbdata)
    elif dbtype == 'action':
        fill_action(conn, config, next_indexes, dbdata)
    elif dbtype == 'profile':
        fill_profile(conn, config, next_indexes, dbdata)


def read_local_config(local_cfg):
    '''Read in the local config file'''
    cfg = {}
    local_conf = ConfigParser.RawConfigParser()
    local_conf.read(local_cfg)
    cfg['cgi_url'] = local_conf.get("DEFAULT", "CGI_URL")
    cfg['cgi_path'] = local_conf.get("DEFAULT", "CGI_PATH")
    cfg['xml_url'] = local_conf.get("DEFAULT", "XML_URL")
    cfg['auth'] = local_conf.get("DEFAULT", "AUTH_TYPE")
    cfg['admin_name'] = local_conf.get("DEFAULT", "ADMIN_NAME")
    cfg['admin_user'] = local_conf.get("DEFAULT", "ADMIN_USER")
    cfg['admin_email'] = local_conf.get("DEFAULT", "ADMIN_EMAIL")
    cfg['root_url'] = local_conf.get("DEFAULT", "ROOT_URL")
    cfg['xml_user'] = local_conf.get("DEFAULT", "XML_USER")
    cfg['xml_pass'] = local_conf.get("DEFAULT", "XML_PASS")
    return cfg


def read_input(local_cfg):
    '''Read the input from the command line'''
    cgi_url = ''
    xml_url = ''
    xml_user = ''
    xml_pass = ''
    cgi_path = ''
    admin_user = ''
    admin_name = ''
    admin_email = ''
    auth = '1'
    root_url = ''
    old_cfg = {'cgi_url': '', 'root_url': '', 'cgi_path': '',
               'xml_url': '', 'xml_user': '', 'xml_pass': '', 'auth': '1',
               'admin_user': 'dpmadmin', 'admin_name': '', 'admin_email': ''}

    if os.path.isfile(local_cfg):
        old_cfg = read_local_config(local_cfg)

    print "Configuring the policy config file. Enter 'q' to quit."

    while 1:
        print "Base URI for the CGI scripts: [%s]" % old_cfg['cgi_url']
        cgi_url = raw_input()
        if cgi_url == 'q':
            sys.exit()
        elif cgi_url == '':
            if not old_cfg['cgi_url']:
                print "You must supply a URI or 'q' to quit."
            else:
                cgi_url = old_cfg['cgi_url']
                break
        else:
            break

    while 1:
        print "Base PATH for the CGI scripts [%s]" % old_cfg['cgi_path']
        cgi_path = raw_input()
        if cgi_path == 'q':
            sys.exit()
        elif cgi_path == '':
            if not old_cfg['cgi_path']:
                print "You must supply a path or 'q' to quit."
            else:
                cgi_path = old_cfg['cgi_path']
                break
        else:
            break

    while 1:
        print "Base URI for the XML database server: [%s]" % old_cfg['xml_url']
        xml_url = raw_input()
        if xml_url == 'q':
            sys.exit()
        elif xml_url == '':
            xml_url = old_cfg['xml_url']
            break
        else:
            break

    while 1:
        print "Username for access to XML database: [%s]" % old_cfg['xml_user']
        xml_user = raw_input()
        if xml_user == 'q':
            sys.exit()
        elif xml_user == '':
            xml_user = old_cfg['xml_user']
            break
        else:
            break

    while 1:
        print "Password for access to XML database: [%s]" % old_cfg['xml_pass']
        xml_pass = raw_input()
        if xml_pass == 'q':
            sys.exit()
        elif xml_pass == '':
            xml_pass = old_cfg['xml_pass']
            break
        else:
            break

    while 1:
        print "Authentication method type: 1=AAI, 2=Standalone [%s]:" %\
            old_cfg['auth']
        auth = raw_input()
        if auth == "1":
            auth_type = "AAI"
            break
        elif auth == "2":
            auth_type = "STANDALONE"
            break
        elif auth == "q":
            sys.exit()
        else:
            if not auth:
                if old_cfg['auth'] and old_cfg['auth'] == "1":
                    auth_type = "AAI"
                    auth = "1"
                    break
                elif old_cfg['auth'] and old_cfg['auth'] == "2":
                    auth_type = "STANDALONE"
                    auth = "2"
                    break

    while 1:
        print "Admin name (firstname lastname) [%s]:" % old_cfg['admin_name']
        admin_name = raw_input()
        if admin_name == 'q':
            sys.exit()
        if admin_name == '':
            if not old_cfg['admin_name']:
                print "You must supply a name or 'q' to quit."
            else:
                admin_name = old_cfg['admin_name']
                break
        else:
            break

    if auth_type == "AAI" and old_cfg['auth'] != auth:
        old_cfg['admin_user'] = ''

    while 1:
        print "Admin username [%s]:" % old_cfg['admin_user']
        if auth_type == "AAI":
            print "Note: this username should be the AAI identifier for the" +\
                " admin user."
        admin_user = raw_input()
        if admin_user == 'q':
            sys.exit()
        if not admin_user:
            if auth_type == 'STANDALONE':
                if not old_cfg['admin_user']:
                    admin_user = "dpmadmin"
                else:
                    admin_user = old_cfg['admin_user']
                break
            elif auth_type == 'AAI':
                if not old_cfg['admin_user'] and admin_user:
                    print "You must supply the AAI identifier or 'q' to quit"
                else:
                    if not admin_user:
                        admin_user = old_cfg['admin_user']
                    break
        elif admin_user == "q":
            sys.exit()
        else:
            break

    while 1:
        print "Admin email address [%s]:" % old_cfg['admin_email']
        admin_email = raw_input()
        if admin_email == 'q':
            sys.exit()
        if admin_email == '':
            if not old_cfg['admin_email']:
                print "You must supply an email address or q to quit."
            else:
                admin_email = old_cfg['admin_email']
                break
        else:
            break

    while 1:
        print "Root url for DPM web pages [%s]:" % old_cfg['root_url']
        root_url = raw_input()
        if root_url == 'q':
            sys.exit()
        if root_url == '':
            if not old_cfg['root_url']:
                print "You must supply a path or 'q' to quit."
            else:
                root_url = old_cfg['root_url']
                break
        else:
            break

    # Write out the new default file
    with file(local_cfg, "w") as fout:
        fout.write("[DEFAULT]\n")
        fout.write("CGI_URL=%s\n" % cgi_url)
        fout.write("CGI_PATH=%s\n" % cgi_path)
        fout.write("XML_URL=%s\n" % xml_url)
        fout.write("XML_USER=%s\n" % xml_user)
        fout.write("XML_PASS=%s\n" % xml_pass)
        fout.write("ADMIN_USER=%s\n" % admin_user)
        fout.write("ADMIN_NAME=%s\n" % admin_name)
        fout.write("ADMIN_EMAIL=%s\n" % admin_email)
        fout.write("AUTH_TYPE=%s\n" % auth)
        fout.write("ROOT_URL=%s\n" % root_url)
        fout.close()
    out_args = {'cgi_url': cgi_url, 'root_url': root_url,
                'xml_url': xml_url, 'xml_user': xml_user, 'xml_pass': xml_pass,
                'cgi_path': cgi_path, 'admin_user': admin_user,
                'admin_name': admin_name, 'admin_email': admin_email,
                'auth_type': auth_type}
    return out_args


def read_config(local_cfg):
    '''Read in the input configuration from the input file'''
    cfgs = {}
    cfgs = read_local_config(local_cfg)
    if cfgs['auth'] == '1':
        cfgs['auth_type'] = "STANDALONE"
    elif cfgs['auth'] == '2':
        cfgs['auth_type'] = 'AAI'
    return cfgs


def configure_files(cfgfile_tmpl, cfgfile, clifile_tmpl, clifile, adminfile,
                    local_cfg, deploy_dir, use_config):
    '''Configure the config, admin and javascript files'''

    lines = []
    jsfiles = ["dpm_app.js.template", "frontPageApp.js.template",
               "register_app.js.template", "errorUtils.js.template",
               "admin_profile_app.js.template"]

    in_args = {}

    # Read in the command line input or read from the config file
    if not use_config:
        in_args = read_input(local_cfg)
    else:
        in_args = read_config(local_cfg)

    # Update the config file
    with file(cfgfile_tmpl, "r") as fin:
        lines = fin.readlines()
        fin.close()
    with file(cfgfile, "w") as fout:
        for line in lines:
            if "CGI_PATH" in line:
                can = string.Template(line)
                line = can.substitute(CGI_PATH=in_args['cgi_path'])
            if "CGI_URL" in line:
                can = string.Template(line)
                line = can.substitute(CGI_URL=in_args['cgi_url'])
            if "XML_PATH" in line:
                can = string.Template(line)
                line = can.substitute(XML_PATH=in_args['xml_url'])
            if "XML_USER" in line:
                can = string.Template(line)
                line = can.substitute(XML_USER=in_args['xml_user'])
            if "XML_PASS" in line:
                can = string.Template(line)
                line = can.substitute(XML_PASS=in_args['xml_pass'])
            if "HTMLUSER" in line:
                can = string.Template(line)
                line = can.substitute(HTMLUSER=in_args['admin_user'])
            if "AUTHTYPE" in line:
                can = string.Template(line)
                line = can.substitute(AUTHTYPE=in_args['auth_type'])
            fout.write("%s" % line)
        fout.close()

    with file(clifile_tmpl, 'r') as fin:
        cli_lines = fin.readlines()
        fin.close()
    with file(clifile, 'w') as fout:
        for line in cli_lines:
            if "CGI_PATH" in line:
                can = string.Template(line)
                line = can.substitute(CGI_PATH=in_args['cgi_path'])
            fout.write("%s" % line)
        fout.close()

        # Update the admin file
        with file(adminfile, "w") as fout:
            fout.write('"%s", %s, %s' % (in_args['admin_name'],
                                         in_args['admin_user'],
                                         in_args['admin_email']))
            fout.close()

        # Update the javascript files
        for afile in jsfiles:
            jfile = afile.split(".template")[0]
            jsfile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  afile))
            with file(jsfile, "r") as fin:
                lines = fin.readlines()
                fin.close()
            jsout = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "%s/html/js/%s" %
                (deploy_dir, jfile)))
            if not os.path.isdir(os.path.dirname(jsout)):
                os.mkdir(os.path.dirname(jsout))
            with file(jsout, "w") as fout:
                for line in lines:
                    if "CGI_URL" in line:
                        can = string.Template(line)
                        line = can.safe_substitute(CGI_URL=in_args['cgi_url'])
                    fout.write(line)
                fout.close()
    return (in_args['cgi_url'], in_args['cgi_path'],
            in_args['root_url'])


def configure_timeout_section(config, deploy_dir, root_url):
    '''Configure the timeout section'''
    with file('dpm.html.template', 'r') as fin:
        lines = fin.readlines()
        fin.close()

    dpm_file = os.path.abspath(os.path.join(deploy_dir,
                                            config.get("HTML", "dpm_page")))
    dpm_dir = os.path.dirname(dpm_file)
    if not os.path.isdir(dpm_dir):
        os.makedirs(dpm_dir)

    with file(dpm_file, "w") as fout:
        for line in lines:
            if "ROOT_URL" in line:
                can = string.Template(line)
                line = can.substitute(ROOT_URL=root_url)
            fout.write(line)
        fout.close()


def configure_dbase(config, root_url):
    '''Configure the pages database file before loading'''

    lines = []

    dbfile_template =\
        os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     config.get("DATABASE_LOADING",
                                                "profile_page_template")))
    dbfile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          config.get("DATABASE_LOADING",
                                                     "profile_page")))

    with file(dbfile_template, "r") as fin:
        lines = fin.readlines()
        fin.close()

    with file(dbfile, "w") as fout:
        for line in lines:
            if "ROOT_URL" in line:
                can = string.Template(line)
                line = can.substitute(ROOT_URL=root_url)
            fout.write(line)
        fout.close()
    return root_url


def copy_files(target_dir, source_dirs):
    '''Copy all the files from the source directory to the target directory'''

    skipfiles = ['policy.cfg.template', 'policy_cli.cfg.template',
                 'dpm.html.template']

    for key in source_dirs.keys():
        sdir = source_dirs[key]
        for adir, dirs, files in os.walk(sdir):
            tdir = adir.replace('..', target_dir)
            if not os.path.isdir(tdir):
                try:
                    os.makedirs(tdir)
                except Exception as err:
                    print "problem creating directory %s" % tdir
                    print err
                    sys.exit(-5)
            for afile in files:
                if afile in skipfiles:
                    continue
                sfile = os.path.abspath(os.path.join(adir, afile))
                tfile = os.path.abspath(os.path.join(tdir, afile))
                try:
                    shutil.copyfile(sfile, tfile)
                    shutil.copymode(sfile, tfile)
                except Exception as err:
                    print "problem copying file %s to %s" % (sfile, tfile)
                    print err
                    sys.exit(-10)


def create_virtualenv(deploy_dir, indirs):
    '''Create the virtualenv for the WSGI server for CLI access'''
    # Create the virtualenv
    wsgi_dir = indirs['wsgi'].replace('..', deploy_dir)
    command = ['virtualenv', '%s/python_env' % wsgi_dir]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, error = proc.communicate()
    return_code = proc.poll()
    if return_code != 0:
        print 'Error: problem creating the virtualenv, rc: ', return_code
        print output
        print error
        sys.exit(return_code)

    # load in the requirements and then we are done
    proc = subprocess.Popen(['/bin/bash'], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True)
    proc.stdin.write('. %s/python_env/bin/activate\n' % wsgi_dir)
    proc.stdin.write('pip install -r %s/requirements.txt\n' % wsgi_dir)
    proc.stdin.write('deactivate\n')
    output, error = proc.communicate()
    return_code = proc.poll()
    if return_code != 0:
        print 'Error: problem configuring the python virtualenv, rc: ',\
            return_code
        print output
        print error
        sys.exit(return_code)


def print_done(deploy_dir, indirs, data_dir, root_url, cgi_url):
    '''Print out some help upon completion'''

    data_url = os.path.join(cgi_url, data_dir)
    html_dir = indirs['html'].replace('..', deploy_dir)
    cgi_dir = indirs['cgi'].replace('..', deploy_dir)
    wsgi_dir = indirs['wsgi'].replace('..', deploy_dir)

    print ""
    print "Configuration Completed"

if __name__ == '__main__':
    dbase_types = ["resource", "action", "profile"]
    data_tag = []
    dbdata = {}
    force_flag = False
    use_config = False
    local_cfg = ".dpm.cfg"
    deploy_dir = '../../deploy'
    data_dir = 'config/data'
    build_dirs = {'cgi': '../cgi', 'html': '../html',
                  'wsgi': '../wsgi',
                  'wsgi-test': '../wsgi-test'}

    opts, args = getopt.getopt(sys.argv[1:], 'hfc:', ['help', 'force',
                                                      'config='])
    for opt, val in opts:
        if opt == '-h' or opt == '--help':
            usage()
            sys.exit(0)
        if opt == '-f' or opt == '--force':
            force_flag = True
        if opt == '-c' or opt == '--config':
            use_config = True
            local_cfg = val.strip()
    
    # Copy all the build scripts to the deploy area
    copy_files(deploy_dir, build_dirs)

    cfgfile_tmpl = \
        os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'policy.cfg.template'))

    clifile_tmpl = \
        os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'policy_cli.cfg.template'))

    cfgfile = \
        os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     '%s/cgi/config/policy.cfg' %
                                     deploy_dir))
    clifile = \
        os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     '%s/wsgi/policy_cli.cfg' % deploy_dir))
    adminfile = \
        os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     '%s/cgi/config/dpm_admin.txt' %
                                     deploy_dir))

    # Configure the data files
    cgi_url, cgi_path, root_url = configure_files(cfgfile_tmpl,
                                                           cfgfile,
                                                           clifile_tmpl,
                                                           clifile,
                                                           adminfile,
                                                           local_cfg,
                                                           deploy_dir,
                                                           use_config)

    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    configure_timeout_section(config, deploy_dir, root_url)
    html_path = configure_dbase(config, root_url)

    # Loop over the database types and fill the databases
    # and configure the files
    for dbase in dbase_types:
        db_name_tag = "%s_name" % dbase.strip()
        db_schema_tag = "%s_schema" % dbase.strip()

        if dbase == 'action':
            data_tag.append("%s_action_data" % dbase.strip())
            data_tag.append("%s_trigger_data" % dbase.strip())
            data_tag.append("%s_org_data" % dbase.strip())
            data_tag.append("%s_date_data" % dbase.strip())
        elif dbase == 'profile':
            data_tag.append("%s_community" % dbase.strip())
            data_tag.append("%s_page" % dbase.strip())
            data_tag.append("%s_role" % dbase.strip())
            data_tag.append("%s_status" % dbase.strip())
        elif dbase == 'resource':
            data_tag.append("%s_data" % dbase.strip())

        dbfile_t = config.get('DATABASE', db_name_tag).split('%s/' %
                                                             cgi_path)[1]

        dbfile = \
            os.path.abspath(os.path.join(os.path.join(
                os.path.dirname(__file__),
                "%s/cgi/%s" % (deploy_dir, dbfile_t))))
        if not os.path.isdir(os.path.dirname(dbfile)):
            os.makedirs(os.path.dirname(dbfile))

        dbschema = config.get("DATABASE_LOADING", db_schema_tag)
        for tag in data_tag:
            dbdata[tag] = config.get("DATABASE_LOADING", tag)

        populate(dbfile, dbschema, dbdata, dbase, force_flag)

    create_virtualenv(deploy_dir, build_dirs)

    print_done(deploy_dir, build_dirs, data_dir, root_url, cgi_url)
