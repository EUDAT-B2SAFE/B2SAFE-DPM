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
import xml.etree.ElementTree


def usage():
    '''Function describing the script usage
    '''
    print 'Configure the Data Policy Manager.'
    print 'Usage: configure_dpm.py [-h]'
    print ''
    print 'Options:'
    print '-h, --help              Print this help'
    print ''


def create_tables(conn, config, dbtype):
    '''Function to create the db tables
    '''
    cur = conn.cursor()
    if (dbtype == 'resource'):
        cur.execute(config.get("CREATE", "systems"))
        cur.execute(config.get("CREATE", "resources"))
        cur.execute(config.get("CREATE", "storage"))
        cur.execute(config.get("CREATE", "sites"))
    elif (dbtype == 'action'):
        cur.execute(config.get("CREATE", "trigger"))
        cur.execute(config.get("CREATE", "type"))
        cur.execute(config.get("CREATE", "operation"))
        cur.execute(config.get("CREATE", "persistentid"))
        cur.execute(config.get("CREATE", "locationtype"))
        cur.execute(config.get("CREATE", "organisation"))
        cur.execute(config.get("CREATE", "action"))
    elif (dbtype == 'profile'):
        cur.execute(config.get("CREATE", "dpm_page"))
        cur.execute(config.get("CREATE", "roles"))
        cur.execute(config.get("CREATE", "status"))
        cur.execute(config.get("CREATE", "community"))
        cur.execute(config.get("CREATE", "user"))
        cur.execute(config.get("CREATE", "user_community"))
        cur.execute(config.get("CREATE", "dpm_date"))
    conn.commit()


def get_next_profile_indexes(conn, config):
    '''Function to get the ntext unused indexes for the profile tables
    '''
    cur = conn.cursor()
    next_indexes = {}
    next_indexes['dpm_page'] = 0
    next_indexes['roles'] = 0
    next_indexes['status'] = 0
    next_indexes['community'] = 0

    cur.execute(config.get("QUERY", "max_dpm_page"))
    max_dpm_page = cur.fetchall()
    if (len(max_dpm_page) > 0):
        next_indexes["dpm_page"] = max_dpm_page[0][0] + 1

    cur.execute(config.get("QUERY", "max_community"))
    max_community = cur.fetchall()
    if (len(max_community) > 0):
        next_indexes["community"] = max_community[0][0] + 1

    cur.execute(config.get("QUERY", "max_roles"))
    max_role = cur.fetchall()
    if (len(max_role) > 0):
        next_indexes["roles"] = max_role[0][0] + 1

    cur.execute(config.get("QUERY", "max_status"))
    max_status = cur.fetchall()
    if (len(max_status) > 0):
        next_indexes["status"] = max_status[0][0] + 1

    return next_indexes


def get_next_actions_indexes(conn, config):
    '''Function to get the next unused indexes for the actions tables
    '''
    cur = conn.cursor()
    next_indexes = {}
    next_indexes['type'] = 0
    next_indexes['trigger'] = 0
    next_indexes['operation'] = 0
    next_indexes['persistentid'] = 0
    next_indexes['organisation'] = 0
    next_indexes['locationtype'] = 0
    next_indexes['action'] = 0

    cur.execute(config.get("QUERY", "max_trigger"))
    max_triggers = cur.fetchall()
    if (len(max_triggers) > 0):
        next_indexes['triggers'] = max_triggers[0][0] + 1

    cur.execute(config.get("QUERY", "max_operation"))
    max_operation = cur.fetchall()
    if (len(max_operation) > 0):
        next_indexes['operation'] = max_operation[0][0] + 1

    cur.execute(config.get("QUERY", "max_type"))
    max_type = cur.fetchall()
    if (len(max_type) > 0):
        next_indexes['type'] = max_type[0][0] + 1

    cur.execute(config.get("QUERY", "max_persistentid"))
    max_persistentID = cur.fetchall()
    if (len(max_persistentID) > 0):
        next_indexes['persistentid'] = max_persistentID[0][0] + 1

    cur.execute(config.get("QUERY", "max_locationtype"))
    max_location = cur.fetchall()
    if (len(max_location) > 0):
        next_indexes['locationtype'] = max_location[0][0] + 1

    cur.execute(config.get("QUERY", "max_organisation"))
    max_organisation = cur.fetchall()
    if (len(max_organisation) > 0):
        next_indexes['organisation'] = max_organisation[0][0] + 1

    cur.execute(config.get("QUERY", "max_action"))
    max_action = cur.fetchall()
    if (len(max_action) > 0):
        next_indexes['action'] = max_action[0][0] + 1

    return next_indexes


def get_next_resources_indexes(conn, config):
    '''Function to get the next unused indexes for the resources tables
    '''
    cur = conn.cursor()
    next_indexes = {}
    next_indexes['system'] = 0
    next_indexes['resource'] = 0
    next_indexes['site'] = 0
    next_indexes['storage'] = 0

    cur.execute(config.get("QUERY", "max_systems"))
    max_systems = cur.fetchall()
    if (len(max_systems) > 0):
        next_indexes['system'] = max_systems[0][0] + 1

    cur.execute(config.get("QUERY", "max_sites"))
    max_sites = cur.fetchall()
    if (len(max_sites) > 0):
        next_indexes['site'] = max_sites[0][0] + 1

    cur.execute(config.get("QUERY", "max_resources"))
    max_resources = cur.fetchall()
    if (len(max_resources) > 0):
        next_indexes['resource'] = max_resources[0][0] + 1

    cur.execute(config.get("QUERY", "max_storage"))
    max_storage = cur.fetchall()
    if (len(max_storage) > 0):
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
    rc = proc.poll()
    if rc:
        print "Error: Unable to wget information from the gocdb %s" %\
            (data["resource_data"])
        print "return code: ", rc
        if (len(output) > 0):
            print "Message: \n"
            print output
        if (len(error) > 0):
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
                if (elem.tag == "HOSTNAME"):
                    print "host ", elem.text
                    host = elem.text
                if (elem.tag == "EXTENSIONS"):
                    irods_details = elem.getchildren()
                    if (len(irods_details) > 0):
                        for irods_elem in irods_details:
                            t_irods_path = get_irods_elem(irods_elem,
                                                          "irods_path")
                            if (len(t_irods_path) > 0):
                                irods_path = t_irods_path

                            t_irods_zone = get_irods_elem(irods_elem,
                                                          "irods_zone")

                            if (len(t_irods_zone) > 0):
                                irods_zone = t_irods_zone

                            t_irods_resc = get_irods_elem(irods_elem,
                                                          "irods_resource")
                            if (len(t_irods_resc) > 0):
                                irods_resc = t_irods_resc

                        if (len(irods_resc) > 0 and len(irods_zone) > 0):
                            data_str = "iRODS|%s|%s|%s|%s" % \
                                (host, irods_resc, irods_zone, irods_path)
                        out_data.append(data_str)
    return out_data


def get_irods_elem(root_elem, key):
    '''return the value for the root element'''
    elem_ok = False
    elem_value = ""
    for elem in root_elem.getchildren():
        if (elem.tag == "KEY" and elem.text == key):
            elem_ok = True
        if (elem.tag == "VALUE" and elem_ok):
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
        if (system_IOK):
            next_indexes['system'] = system_count

        site_IOK, site_count = fill_table(cur, config,
                                          "sites",
                                          next_indexes['site'], site)
        if (site_IOK):
            next_indexes['site'] = site_count

        storage_IOK, storage_count = fill_table(cur, config,
                                                "storage",
                                                next_indexes['storage'],
                                                store, path)
        if (storage_IOK):
            next_indexes['storage'] = storage_count

        cur.execute(config.get("QUERY", "resources"),
                    (system_count-1, site_count-1, storage_count-1))
        resources = cur.fetchall()
        res_id = 'resource'
        if (len(resources) == 0):
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
    insertOK = False
    cur.execute(config.get("QUERY", table), (val,))
    vals = cur.fetchall()
    if (len(vals) == 0):
        if (len(values) == 0):
            cur.execute(config.get("INSERT", table),
                        (idx, val))
        else:
            params = []
            params.append(idx)
            params.append(val)
            params = params + list(values)
            cur.execute(config.get("INSERT", table), params)
        insertOK = True
        idx += 1
    else:
        idx = int(vals[0][0]) + 1

    return (insertOK, idx)


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
        if (community_OK):
            next_indexes["community"] = community_count

    # Fill the dpm_page
    for row in file(data["profile_page"], "r"):
        dpm_page, name = row.split('|')
        cur.execute(config.get("QUERY", "dpm_page"),
                    (next_indexes["dpm_page"],))
        vals = cur.fetchall()
        if (len(vals) == 0):
            cur.execute(config.get("INSERT", "dpm_page"),
                        (next_indexes["dpm_page"], dpm_page.strip(),
                         name.strip()))
            next_indexes["dpm_page"] = next_indexes["dpm_page"] + 1

    # Fill the status
    for row in file(data["profile_status"], "r"):
        status = row.strip()
        status_OK, status_count = fill_table(cur, config, "status",
                                             next_indexes["status"], status)
        if (status_OK):
            next_indexes["status"] = status_count

    # Fill the roles
    for row in file(data["profile_role"], "r"):
        role = row.strip()
        role_OK, role_count = fill_table(cur, config, "roles",
                                         next_indexes["roles"], role)
        if (role_OK):
            next_indexes["roles"] = role_count

    conn.commit()


def fill_action(conn, config, next_indexes, data):
    '''Fill the action database
    '''
    cur = conn.cursor()
    atype_count = 0
    atrigger_count = 0
    aoperation_count = 0
    alocation_count = 0
    action_count = 0

    # Fill the action tables from the ascii file
    for row in file(data["action_action_data"], "r"):
        atype, atrigger, aoperation, alocation = row.split('|')
        atype = atype.strip()
        atrigger = atrigger.strip()
        aoperation = aoperation.strip()
        alocation = alocation.strip()

        atype_IOK, atype_count = fill_table(cur, config, "type",
                                            next_indexes["type"], atype)
        if (atype_IOK):
            next_indexes['type'] = atype_count

        atrigger_IOK, atrigger_count = fill_table(cur, config,
                                                  "trigger",
                                                  next_indexes["trigger"],
                                                  atrigger)
        if (atrigger_IOK):
            next_indexes['trigger'] = atrigger_count

        aoperation_IOK, aoperation_count = \
            fill_table(cur, config, "operation", next_indexes["operation"],
                       aoperation)
        if (aoperation_IOK):
            next_indexes['operation'] = aoperation_count

        alocation_IOK, alocation_count = \
            fill_table(cur, config, "locationtype",
                       next_indexes["locationtype"], alocation)
        if (alocation_IOK):
            next_indexes['locationtype'] = alocation_count

        cur.execute(config.get("QUERY", "action"),
                    (atype_count-1, atrigger_count-1,
                    aoperation_count-1, alocation_count-1))
        actions = cur.fetchall()
        if (len(actions) == 0):
            cur.execute(config.get("INSERT", "action"),
                        (next_indexes['action'], atype_count-1,
                        atrigger_count-1,
                        aoperation_count-1, alocation_count-1))
            action_count = next_indexes['action']
            action_count += 1
            next_indexes['action'] = action_count
        else:
            action_count = int(actions[0][0]) + 1

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
        if (org_IOK):
            next_indexes['organisation'] = org_count

        pid_IOK, pid_count = fill_table(cur, config,
                                        "persistentID",
                                        next_indexes["persistentid"], pid)
        if (pid_IOK):
            next_indexes['persistentid'] = pid_count

    conn.commit()


def populate(dbfile, dbschema, dbdata, dbtype):
    '''Populate the database
    '''
    if (os.path.isfile(dbfile)):
        print 'Warning: database file %s exists' % dbfile
        print 'Will update this database.'
        cont = raw_input('Ok to continue? [y/n]')
        if (cont != 'y' and cont != 'Y'):
            print 'Exiting'
            sys.exit(0)
        else:
            print 'Uploading data to the %s database' % dbtype
    else:
        print 'Uploading data to the %s database' % dbtype

    # Get the resource information from the GOCDB

    # Open the database
    print "database ", dbfile
    conn = sqlite3.connect(dbfile)

    # read in the schema config
    config = ConfigParser.ConfigParser()
    config.read(dbschema)

    # Create the database tables
    create_tables(conn, config, dbtype)

    # Get the next unused indexes for the tables
    next_indexes = {}
    if (dbtype == 'resource'):
        next_indexes = get_next_resources_indexes(conn, config)
    elif (dbtype == 'action'):
        next_indexes = get_next_actions_indexes(conn, config)
    elif (dbtype == 'profile'):
        next_indexes = get_next_profile_indexes(conn, config)

    # Fill the databases
    if (dbtype == 'resource'):
        fill_resource(conn, config, next_indexes, dbdata)
    elif (dbtype == 'action'):
        fill_action(conn, config, next_indexes, dbdata)
    elif (dbtype == 'profile'):
        fill_profile(conn, config, next_indexes, dbdata)


def configure_files(cfgfile_tmpl, cfgfile, adminfile, local_cfg):
    '''Configure the config, admin and javascript files'''
    cgi_url = ""
    old_cgi_url = ""
    admin_user = ""
    old_admin_user = "dpmadmin"
    old_admin_name = ""
    old_admin_email = ""
    admin_name = ""
    admin_email = ""
    auth = "1"
    old_auth = "1"
    root_url = ""
    old_root_url = ""

    lines = []
    jsfiles = ["dpm_app.js.template", "frontPageApp.js.template",
               "register_app.js.template", "errorUtils.js.template",
               "admin_profile_app.js.template"]

    local_conf = ConfigParser.RawConfigParser()
    if (os.path.isfile(local_cfg)):
        local_conf.read(local_cfg)
        old_cgi_url = local_conf.get("DEFAULT", "CGI_URL")
        old_auth = local_conf.get("DEFAULT", "AUTH_TYPE")
        old_admin_name = local_conf.get("DEFAULT", "ADMIN_NAME")
        old_admin_user = local_conf.get("DEFAULT", "ADMIN_USER")
        old_admin_email = local_conf.get("DEFAULT", "ADMIN_EMAIL")
        old_root_url = local_conf.get("DEFAULT", "ROOT_URL")

    print "Configuring the policy config file. Enter 'q' to quit."

    while (1):
        print "Base URI for the CGI scripts: [%s]" % old_cgi_url
        cgi_url = raw_input()
        if (cgi_url == 'q'):
            sys.exit()
        elif (len(cgi_url) == 0):
            if (len(old_cgi_url) == 0):
                print "You must supply a path or 'q' to quit."
            else:
                cgi_url = old_cgi_url
                break
        else:
            break

    while (1):
        print "Authentication method type: 1=AAI, 2=Standalone [%s]:" %\
            old_auth
        auth = raw_input()
        if (auth == "1"):
            auth_type = "AAI"
            break
        elif (auth == "2"):
            auth_type = "STANDALONE"
            break
        elif (auth == "q"):
            sys.exit()
        else:
            if (len(auth) == 0):
                if (len(old_auth) == 0 or old_auth == "1"):
                    auth_type = "AAI"
                    auth = "1"
                    break
                elif (old_auth == "2"):
                    auth_type = "STANDALONE"
                    auth = "2"
                    break

    while (1):
        print "Admin name (firstname lastname) [%s]:" % old_admin_name
        admin_name = raw_input()
        if (len(admin_name) == 0):
            if (len(old_admin_name) == 0):
                print "You must supply a name or 'q' to quit."
            else:
                admin_name = old_admin_name
                break
        else:
            break

    print "Admin username [%s]:" % old_admin_user
    admin_user = raw_input()
    if (len(admin_user) == 0):
        if (len(old_admin_user) == 0):
            admin_user = "dpmadmin"
        else:
            admin_user = old_admin_user
    elif (admin_user == "q"):
        sys.exit()

    while (1):
        print "Admin email address [%s]:" % old_admin_email
        admin_email = raw_input()
        if (len(admin_email) == 0):
            if (len(old_admin_email) == 0):
                print "You must supply an email address"
            else:
                admin_email = old_admin_email
                break
        else:
            break

    while (1):
        print "Root url for DPM web pages [%s]:" % old_root_url
        root_url = raw_input()
        if (len(root_url) == 0):
            if (len(old_root_url) == 0):
                print "You must supply a path or 'q' to quit."
            else:
                root_url = old_root_url
                break
        else:
            break

    # Write out the new default file
    with file(local_cfg, "w") as fout:
        fout.write("[DEFAULT]\n")
        fout.write("CGI_URL=%s\n" % cgi_url)
        fout.write("ADMIN_USER=%s\n" % admin_user)
        fout.write("ADMIN_NAME=%s\n" % admin_name)
        fout.write("ADMIN_EMAIL=%s\n" % admin_email)
        fout.write("AUTH_TYPE=%s\n" % auth)
        fout.write("ROOT_URL=%s\n" % root_url)
        fout.close()

    # Update the config file
    with file(cfgfile_tmpl, "r") as fin:
        lines = fin.readlines()
        fin.close()
    with file(cfgfile, "w") as fout:
        for line in lines:
            if ("CGI_URL" in line):
                can = string.Template(line)
                line = can.substitute(CGI_URL=cgi_url)
            elif ("HTMLUSER" in line):
                can = string.Template(line)
                line = can.substitute(HTMLUSER=admin_user)
            elif ("AUTHTYPE" in line):
                can = string.Template(line)
                line = can.substitute(AUTHTYPE=auth_type)
            fout.write("%s" % line)
        fout.close()

        # Update the admin file
        with file(adminfile, "w") as fout:
            fout.write('"%s", %s, %s' % (admin_name, admin_user, admin_email))
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
                os.path.dirname(__file__), "../html/deploy/js/%s" % jfile))
            if (not os.path.isdir(os.path.dirname(jsout))):
                os.mkdir(os.path.dirname(jsout))
            with file(jsout, "w") as fout:
                for line in lines:
                    if ("CGI_URL" in line):
                        can = string.Template(line)
                        line = can.safe_substitute(CGI_URL=cgi_url)
                    fout.write(line)
                fout.close()
    return (cgi_url, root_url)


def configure_dbase(config, root_url):
    '''Configure the pages database file before loading'''

    lines = []

    dbfile_template = os.path.abspath(os.path.join(os.path.dirname(__file__),
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
            if ("ROOT_URL" in line):
                can = string.Template(line)
                line = can.substitute(ROOT_URL=root_url)
            fout.write(line)
        fout.close()
    return root_url

if __name__ == '__main__':
    dbase_types = ["resource", "action", "profile"]
    data_tag = []
    dbdata = {}
    local_cfg = ".dpm.cfg"

    opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    for opt, val in opts:
        if (opt == '-h' or opt == '--help'):
            usage()
            sys.exit(0)

    cfgfile_tmpl = \
        os.path.abspath(os.path.join(
                        os.path.dirname(__file__),
                        '../cgi/deploy/config/policy.cfg.template'))

    cfgfile = \
        os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     '../cgi/deploy/config/policy.cfg'))
    adminfile = \
        os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     '../cgi/deploy/config/dpm_admin.txt'))

    cgi_url, root_url = configure_files(cfgfile_tmpl, cfgfile, adminfile,
                                        local_cfg)

    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    html_path = configure_dbase(config, root_url)

    # Loop over the database types and fill the databases
    # and configure the files
    for dbase in dbase_types:
        db_name_tag = "%s_name" % dbase.strip()
        db_schema_tag = "%s_schema" % dbase.strip()

        if (dbase == 'action'):
            data_tag.append("%s_action_data" % dbase.strip())
            data_tag.append("%s_org_data" % dbase.strip())
        elif (dbase == 'profile'):
            data_tag.append("%s_community" % dbase.strip())
            data_tag.append("%s_page" % dbase.strip())
            data_tag.append("%s_role" % dbase.strip())
            data_tag.append("%s_status" % dbase.strip())
        elif (dbase == 'resource'):
            data_tag.append("%s_data" % dbase.strip())

        dbfile = \
            os.path.abspath(os.path.join(os.path.join(
                os.path.dirname(__file__),
                "../cgi/deploy/%s" % config.get("DATABASE", db_name_tag))))
        if (not os.path.isdir(os.path.dirname(dbfile))):
            os.makedirs(os.path.dirname(dbfile))

        dbschema = config.get("DATABASE_LOADING", db_schema_tag)
        for tag in data_tag:
            dbdata[tag] = config.get("DATABASE_LOADING", tag)

        populate(dbfile, dbschema, dbdata, dbase)
