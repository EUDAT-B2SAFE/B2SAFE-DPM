#!/usr/bin/env python
import json
import sys
import ConfigParser
import StringIO
import hashlib
import time
import os
import sqlite3
import requests

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))
import policy_irods_sub
import policy_irods_lib
import policy_lib


class Policy(object):
    '''policy class'''
    def __init__(self, config, form_data):
        '''initialiser'''
        self.uuid = None
        self.policy = {}
        self.form_data = form_data
        self.config = config
        self.trigger_time = False
        self.irods_system = 'iRODS'
        self.irods_namespace = "irodsns:coordinates"
        # Check the database exists - if not create it
        conn = sqlite3.connect(config.get("DATABASE", "name").strip())
        cur = conn.cursor()
        cur.execute('''create table if not exists policies (key text, value
                    text)''')
        conn.commit()

    def process_form(self):
        '''process the form data and fill the object attributes
        '''
        trigger_val = ''
        periodic_type = 'date/time'
        run_now = 'immediately'

        self.policy[self.config.get("ACTIONS_SCHEMA",
                                    "policy_id").strip()] = \
            self.form_data['policy_action_id']
        self.policy[self.config.get('POLICY_SCHEMA',
                                    'ctime').strip()] = int(time.time())

        self.policy[self.config.get('POLICY_SCHEMA',
                                    'removed').strip()] = 'false'
        self.policy[self.config.get('POLICY_SCHEMA',
                                    'community').strip()] = \
            self.form_data['community']
        self.policy[self.config.get('POLICY_SCHEMA',
                                    'uniqueid').strip()] = \
            self.form_data['uuid']
        self.policy[self.config.get('POLICY_SCHEMA',
                                    'id').strip()] = self.form_data['id']
        self.policy[self.config.get('POLICY_SCHEMA',
                                    'name').strip()] = self.form_data['name']
        self.policy[self.config.get('POLICY_SCHEMA',
                                    'version').strip()] = \
            self.form_data['version']
        self.policy[self.config.get('POLICY_SCHEMA',
                                    'author').strip()] = \
            self.form_data['author']
        self.policy[self.config.get('ACTIONS_SCHEMA',
                                    'type').strip()] = \
            self.form_data['type']['name']
        self.policy['family'] = self.form_data['family']

        if self.form_data['trigger']['name'] == periodic_type:
            trigger_val = self.form_data['trigger_period']['name']
            self.trigger_time = True
        elif self.form_data['trigger']['name'] == run_now:
            self.trigger_time = False

        self.policy[self.config.get('ACTIONS_SCHEMA',
                                    'trigger').strip()] = trigger_val
        self.policy[self.config.get('ACTIONS_SCHEMA',
                                    'trigger_type').strip()] = \
            self.form_data['trigger']['name'].strip()

        self.__fill_colls(self.form_data['sources'], 'SOURCES_SCHEMA')
        self.__fill_colls(self.form_data['targets'], 'TARGETS_SCHEMA')

    def __fill_colls(self, form_colls, schema):
        '''Fill the collection attributes for the policy
        '''
        col_idx = 0
        col_idx2 = 0
        for acoll in form_colls:
            key_hostname = "%s_%s" % (self.config.get(schema,
                                                      'hostname'),
                                      col_idx2)
            key_resource = "%s_%s" % (self.config.get(schema,
                                                      'resource'),
                                      col_idx2)
            if acoll['type']['name'] == 'pid':
                key_type = "%s_%s" %\
                    (self.config.get(schema, 'type').strip(), col_idx)
                key_identifier = "%s_%s" %\
                    (self.config.get(schema, 'identifier').strip(),
                     col_idx)
                self.policy[key_type] = acoll['type']['name']
                self.policy[key_identifier] = acoll['identifier']['name']
                col_idx += 1
            elif acoll['type']['name'] == 'collection':
                key_type = "%s_%s" %\
                    (self.config.get(schema, 'type').strip(), col_idx)
                key_identifier = "%s_%s" %\
                    (self.config.get(schema, 'identifier').strip(),
                     col_idx)
                key_hostname = "%s_%s" %\
                    (self.config.get(schema, 'hostname'), col_idx)
                key_resource = "%s_%s" %\
                    (self.config.get(schema, 'resource'), col_idx)
                self.policy[key_hostname] = acoll['hostname']['name']
                self.policy[key_resource] = acoll['resource']['name']
                self.policy[key_identifier] = acoll['identifier']['name']
                self.policy[key_type] = acoll['type']['name']
                col_idx += 1
 
    def new_version(self, family):
        '''Return the new version number which is just largest number for the family
        incremented by one'''
        baseX_url = config.get("XMLDATABASE", "name").strip()
        query_url = base_url + "_%s?query=//*:policy[@family='%s']/@version" % \
                (self.policy[self.config.get("POLICY_SCHEMA",
                    "community").strip()],
                 self.policy["family"])
        resp = request.get(query_url,
                auth=(config.get("XMLDATABASE", "user"),
                      config.get("XMLDATABASE", "pass")))
        if resp.status_code != 200:
            print "Problem querying the XML database: ",\
                    resp.status_code
            print resp.text
            sys.exit(-101)
        versions = resp.text.split()
        version_numbers = [int(ver.split("=")[-1].strip('"')) for ver in versions]
        version_numbers.sort()
        version = version_numbers[-1] + 1
        return version

    def create_xml(self, formdata):
        '''Method to create an XML policy
        '''
        # Create instances of the classes generated from the schema
        # and fill the attributes and values. Need to start from the
        # inner node to the outer node

        # Build the dataset node
        xml_dataset = policy_lib.datasetType2()
        xml_dataset.collection = self.__create_colls()

        # Build the action nodes
        xml_actions = policy_lib.actionsType()
        xml_actions.action = self.__create_actions()

        version = self.new_version(formdata['family'])

        # Build the policy node
        xml_pol = policy_lib.policy()
        xml_pol.uniqueid = formdata['uuid']
        xml_pol.version = version
        xml_pol.name = formdata['name']
        xml_pol.author = formdata['author']
        xml_pol.community = formdata['community']
        xml_pol.family = self.policy['family']
        xml_pol.created = self.policy[self.config.get('POLICY_SCHEMA',
                                                      'ctime').strip()]
        xml_pol.dataset = xml_dataset
        xml_pol.actions = xml_actions

        # Output XML and store in key-value
        output = StringIO.StringIO()
        xml_pol.export(output, 0, namespacedef_=self.config.get(
            "XML_NAMESPACE", "namespacedef"))

        self.policy[self.config.get('POLICY_SCHEMA', 'object').strip()] = \
            output.getvalue()

    def __create_action_type(self):
        '''Private method to build the action type node
        '''
        action_key = self.config.get('ACTIONS_SCHEMA', 'type')
        action_policy_key = self.config.get('ACTIONS_SCHEMA', 'policy_id')
        xml_action_type = policy_lib.actionType()
        if len(self.policy[action_policy_key]['name']) > 0:
            xml_action_type.policyID = self.policy[action_policy_key]['name']
        xml_action_type.valueOf_ = self.policy[action_key]
        return xml_action_type

    def __create_trigger(self):
        '''Private method to build the trigger node
        '''
        xml_trigger = policy_lib.triggerType()
        # xml_trigger_action = policy_lib.actionType()

        # Process the form data according to the type selected
        # trigger_key = self.config.get('ACTIONS_SCHEMA', 'trigger_type')
        trigger_date_key = self.config.get('ACTIONS_SCHEMA', 'trigger')

        if self.trigger_time:
            xml_trigger.time = self.policy[trigger_date_key]
        else:
            runonce = policy_lib.runonceType()
            xml_trigger.runonce = runonce
            # xml_trigger_action.valueOf_ = self.policy[trigger_date_key]
            # xml_trigger.action = xml_trigger_action
        return xml_trigger

    def __create_actions(self):
        '''Private method to build the action nodes
        '''
        xml_actions = []
        # We could potentially have many actions so will need to
        # loop in the future
        xml_action = policy_lib.actionType1()
        xml_action.trigger = self.__create_trigger()
        xml_action.type_ = self.__create_action_type()

        xml_targets = policy_lib.targetsType()
        xml_targets.target = self.__create_targets()
        xml_action.targets = xml_targets
        # xml_action.name = formdata['action']['name']
        xml_actions.append(xml_action)
        return xml_actions

    def __create_tgt_location(self, index):
        '''Private method to build the location node
        '''
        xml_location = policy_irods_sub.coordinatesSub()
        xml_location.site = self.__create_site(index, 'TARGETS_SCHEMA')
        xml_location.resource = ''
        identifier_key = '%s%s' % (self.config.get('TARGETS_SCHEMA',
                                                   'identifier'), index)
        xml_location.path = self.policy[identifier_key]
        # Needed as the default location is abstract
        xml_location.extensiontype_ = self.irods_namespace
        return xml_location

    def __create_src_location(self, index):
        '''Private method to build the location node
        '''
        xml_location = policy_irods_sub.coordinatesSub()
        xml_location.site = self.__create_site(index, 'SOURCES_SCHEMA')
        xml_location.resource = ''
        identifier_key = "%s%s" % (self.config.get('SOURCES_SCHEMA',
                                                   'identifier'), index)
        xml_location.path = self.policy[identifier_key]
        # Needed as the default location is abstract
        xml_location.extensiontype_ = self.irods_namespace
        return xml_location

    def __create_site(self, index, schema):
        '''Private method to build the site node
        '''
        xml_site = policy_irods_sub.siteType2Sub()
        xml_site.type_ = 'EUDAT'
        site_key = '%s%s' % (self.config.get(schema, 'hostname'), index)
        xml_site.valueOf_ = self.policy[site_key]
        return xml_site

    def __create_targets(self):
        '''Private method to build the target nodes
        '''
        xml_targets = []
        for key in self.policy.keys():
            if self.config.get('TARGETS_SCHEMA', 'type') in key:
                xml_target = policy_lib.locationPoint()
                index = key.split(self.config.get('TARGETS_SCHEMA', 'type'))[1]

                if self.policy[key] == 'pid':
                    identifier_key = '%s%s' % \
                        (self.config.get('TARGETS_SCHEMA', 'identifier'),
                         index)
                    xml_persistent_identifier = \
                        policy_lib.persistentIdentifierType7()
                    xml_persistent_identifier.valueOf_ = \
                        self.policy[identifier_key]
                    xml_persistent_identifier.type_ = self.policy[key]
                    xml_target.persistentIdentifier = xml_persistent_identifier
                elif self.policy[key] == 'collection':
                    xml_target_location = self.__create_tgt_location(index)
                    xml_target.location = xml_target_location

                xml_target.id = int(index.split('_')[1])
                xml_targets.append(xml_target)
        return xml_targets

    def __create_colls(self):
        '''Private method to fill the collections
        '''
        xml_collections = []
        for key in self.policy.keys():
            if self.config.get('SOURCES_SCHEMA', 'type') in key:
                xml_collection = policy_lib.locationPoint()
                index = key.split(self.config.get('SOURCES_SCHEMA', 'type'))[1]

                if self.policy[key] == 'pid':
                    identifier_key = "%s%s" % \
                        (self.config.get('SOURCES_SCHEMA', 'identifier'),
                         index)
                    xml_persistent_identifier = \
                        policy_lib.persistentIdentifierType7()
                    xml_persistent_identifier.valueOf_ = \
                        self.policy[identifier_key]
                    xml_persistent_identifier.type_ = self.policy[key]
                    xml_collection.persistentIdentifier = \
                        xml_persistent_identifier
                elif self.policy[key] == 'collection':
                    xml_source_location = self.__create_src_location(index)
                    xml_collection.location = xml_source_location

                xml_collection.id = int(index.split('_')[1])
                xml_collections.append(xml_collection)
        return xml_collections

    def setmd5(self, md5):
        '''Method to store the md5 hash
        '''
        self.policy[self.config.get("POLICY_SCHEMA", "md5").strip()] =\
            md5

    def settime(self, ctime):
        '''Method to set the create time
        '''
        self.policy[self.config.get("POLICY_SCHEMA", "ctime").strip()] = \
            ctime


def policyExists(pol, config):
    '''Function to check if the policy exists in the database by comparing
    checksums
    '''
    exists = False

    polmd5 = pol[config.get("POLICY_SCHEMA", "md5")]
    dbfile = config.get("DATABASE", "name").strip()

    if (not os.path.isfile(dbfile)):
        sys.stderr.write("Unable to open the database: %s" % dbfile)
        sys.exit(-100)

    # Open the database
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    md5_str = "%s%%" % (config.get("POLICY_SCHEMA", "md5"))
    cur.execute("select key from policies where key like ? and value=?",
                (md5_str, polmd5))
    results = cur.fetchall()
    if (len(results) > 0):
        exists = True
    return exists


def dump_to_xml_store(pol, config):
    '''Store the policy in the XML database'''
    baseX_url = config.get("XMLDATABASE", "name").strip()

    # Store the policy in the XML database. We assume the database exists
    # beforehand
    policy_url = baseX_url.strip() + "_%s/policy_%s.xml" %\
        (pol[config.get("POLICY_SCHEMA", "community")],
         pol[config.get("POLICY_SCHEMA", "uniqueid")])
    resp = requests.put(policy_url,
                        data=pol[config.get("POLICY_SCHEMA", "object")],
                        auth=(config.get("XMLDATABASE", "user"),
                              config.get("XMLDATABASE", "pass")))
    if resp.status_code != 201:
        print "Problem storing the policy in the XML database: ",\
            resp.status_code
        print resp.text
        sys.exit(-100)


def runStore():
    # Get the schema used for the key-value pair database
    config = ConfigParser.ConfigParser()
    config.read("./config/policy.cfg")
    policy_exists = False

    # Read in the form data
    aform = json.load(sys.stdin)

    print "Content-Type: application/json\n"

    # Process the form data and create policy
    aPolicy = Policy(config, aform)
    aPolicy.process_form()
    aPolicy.create_xml(aform)

    # Compute md5 for policy and the create time
    md5 = hashlib.md5()
    md5.update(aPolicy.policy["policy_object"])
    md5sum = md5.hexdigest()
    aPolicy.setmd5(md5sum)
    aPolicy.settime(int(time.time()))

    # Check if the policy exists in the database
    if (policyExists(aPolicy.policy, config)):
        policy_exists = True
    else:
        # Write the policy to a database
        dump_to_xml_store(aPolicy.policy, config)

    #print "Input:"
    # print aform
    print ""
    #print aPolicy.policy["policy_object"]
    print json.dumps({'policy_exists': policy_exists})

if __name__ == '__main__':
    runStore()
