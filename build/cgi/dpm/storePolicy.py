#!/usr/bin/env python
import json
import sys
import ConfigParser
import StringIO
import hashlib
import time
import os

import kyotocabinet

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))
import policy_irods_sub
import policy_irods_lib
import policy_lib

class Policy():
    '''policy class'''
    def __init__(self, config):
        '''initialiser'''
        self.uuid = None 
        self.policy = {}
        self.config = config
        self.dateType = 'date'
        self.periodicType = 'period'
        self.irodsSystem = 'iRODS'
        self.irodsNamespace = "irodsns:coordinates"

    def processForm(self, formdata):
        '''process the form data and fill the obect attributes
        '''
        trigger_val = ''
        self.policy[self.config.get('POLICY_SCHEMA',
            'community').strip()] = formdata['community']
        self.policy[self.config.get('POLICY_SCHEMA', 
            'uniqueid').strip()] = formdata['uuid']
        self.policy[self.config.get('POLICY_SCHEMA', 
            'name').strip()] = formdata['name']
        self.policy[self.config.get('POLICY_SCHEMA', 
            'version').strip()] = formdata['version']
        self.policy[self.config.get('POLICY_SCHEMA', 
            'author').strip()] = formdata['author']
        self.policy[self.config.get('ACTIONS_SCHEMA', 
            'type').strip()] = formdata['type']['name']
        if (formdata['trigger']['name'] == self.dateType):
            trigger_val = formdata['trigger_date']
        elif (formdata['trigger']['name'] == self.periodicType):
            trigger_val = "%s %s %s %s %s" %\
                    (formdata['trigger_period']['minute']['name'],
                            formdata['trigger_period']['hour']['name'],
                            formdata['trigger_period']['day']['name'],
                            formdata['trigger_period']['month']['name'],
                            formdata['trigger_period']['weekday']['name'])
        self.policy[self.config.get('ACTIONS_SCHEMA', 
            'trigger').strip()] = trigger_val
        self.policy[self.config.get('ACTIONS_SCHEMA', 
            'name').strip()] = formdata['action']['name']
        col_idx = 0
        for acoll in formdata['collections']:
            akeypid = "%s_%s" % (self.config.get('DATASETS_SCHEMA',
                'pid').strip(), col_idx)
            akeytype = "%s_%s" % (self.config.get('DATASETS_SCHEMA',
                'type').strip(), col_idx)
            self.policy[akeypid] = acoll['name']
            self.policy[akeytype] = acoll['type']['name']
            col_idx += 1

        self.policy[self.config.get('TARGETS_SCHEMA', 
            'path').strip()] = formdata['target']['path']
        self.policy[self.config.get('TARGETS_SCHEMA', 'site').strip()] = \
                formdata['target']['site']['name']
        self.policy[self.config.get('TARGETS_SCHEMA', 
            'resource').strip()] = \
                formdata['target']['resource']['name']
        self.policy[self.config.get('TARGETS_SCHEMA', 'type').strip()] = \
                formdata['target']['organisation']['name']

    def createXML(self, formdata):
        '''Method to create an XML policy
        '''
        # Create instances of the classes generated from the schema
        # and fill the attributes and values. Need to start from the
        # inner node to the outer node
        
        # Build the dataset node
        xml_dataset = policy_lib.datasetType2()
        xml_dataset.collection = self.__createColls(formdata) 

        # Build the action nodes
        xml_actions = policy_lib.actionsType()
        xml_actions.action = self.__createActions(formdata)

        # Build the policy node
        xml_pol = policy_lib.policy()
        xml_pol.uniqueid = formdata['uuid']
        xml_pol.version = formdata['version']
        xml_pol.name = formdata['name']
        xml_pol.author = formdata['author']
        xml_pol.dataset = xml_dataset
        xml_pol.actions = xml_actions

        # Output XML and store in key-value
        output = StringIO.StringIO()
        xml_pol.export(output, 0, 
                namespacedef_=self.config.get("XML_NAMESPACE", 
                    "namespacedef"))

        self.policy[self.config.get('POLICY_SCHEMA', 'object').strip()] = \
                output.getvalue() 

    def __createActionType(self, formdata):
        '''Private method to build the action type node
        '''
        xml_action_type = policy_lib.actionType()
        # xml_action_type.policyID = formdata[]
        xml_action_type.valueOf_ = formdata['type']['name']
        return xml_action_type

    def __createTrigger(self, formdata):
        '''Private method to build the trigger node
        '''
        trigger_val = ''
        dateSpecified = False
        xml_trigger = policy_lib.triggerType()
        xml_trigger_action = policy_lib.actionType()
        
        # Process the form data according to the type selected
        if (formdata['trigger']['name'] == self.dateType):
            # The date is in the wrong format according to XML schema
            # it should be: secs mins hours day month year
            trigger_tmp = formdata['trigger_date'].split("-")
            trigger_val = "0 0 0 %s %s %s" % (trigger_tmp[2],
                    trigger_tmp[1], trigger_tmp[0])
            dateSpecified = True
        elif (formdata['trigger']['name'] == self.periodicType):
            trigger_val = 0
            dateSpecified = True
 
        if (dateSpecified):
            xml_trigger.time = trigger_val
        else:
            xml_trigger_action.valueOf_ = trigger_val
            xml_trigger.action = xml_trigger_action
        return xml_trigger

    def __createActions(self, formdata):
        '''Private method to build the action nodes
        '''
        xml_actions = []
        # We could potentially have many actions so will need to
        # loop in the future
        xml_action = policy_lib.actionType1()
        xml_action.trigger = self.__createTrigger(formdata)
        xml_action.type_ = self.__createActionType(formdata)
        
        xml_targets = policy_lib.targetsType()
        xml_targets.target = self.__createTargets(formdata)
        xml_action.targets = xml_targets
        xml_action.name = formdata['action']['name']
        xml_actions.append(xml_action)
        return xml_actions

    def __createLocation(self, formdata):
        '''Private method to build the location node
        '''
        xml_location = policy_irods_sub.coordinatesSub()
        xml_location.site = self.__createSite(formdata)
        xml_location.resource = formdata['target']['resource']['name']
        xml_location.path = formdata['target']['path']
        # Needed as the default location is abstract
        if (formdata['target']['system']['name'] == self.irodsSystem):
            xml_location.extensiontype_ = self.irodsNamespace 
        return xml_location

    def __createSite(self, formdata):
        '''Private method to build the site node
        '''
        xml_site = policy_irods_sub.siteType2Sub()
        xml_site.type_ = formdata['target']['organisation']['name']
        xml_site.valueOf_ = formdata['target']['site']['name']
        return xml_site

    def __createTargets(self, formdata):
        '''Private method to build the target nodes
        '''
        xml_targets = []
        tgt_idx = 0
        # Currently we don't have more than one target so we just
        # use that. 
        xml_target = policy_lib.locationPoint()
        xml_target.location = self.__createLocation(formdata)
        xml_targets.append(xml_target)
        return xml_targets

    def __createColls(self, formdata):
        '''Private method to fill the collections
        '''
        xml_collections = []
        col_idx = 0
        for acoll in formdata['collections']:
            xml_collection = policy_lib.locationPoint()
            xml_persistentIdentifier = policy_lib.persistentIdentifierType7()
            xml_persistentIdentifier.valueOf_ = acoll['name']
            xml_persistentIdentifier.type_ = acoll['type']['name']
            xml_collection.id = col_idx
            xml_collection.persistentIdentifier = xml_persistentIdentifier
            xml_collections.append(xml_collection)
            col_idx += 1
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
    db = kyotocabinet.DB()
 
    # Open the database
    if (not db.open(dbfile, 
        kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE)):
        sys.stderr.write("open error: " + str(db.error()))

    cur = db.cursor()
    cur.jump()
    while True:
        rec = cur.get(True)
        if not rec:
            break
        if ("md5" in rec[0] and rec[1] == polmd5):
            exists = True
            break
    return exists
            
def dumpToKVDb(pol, config):
    '''Function to dump the policy to a key-value pair database
    '''
    dbfile = config.get("DATABASE", "name").strip()
    db = kyotocabinet.DB()

    # Open the database
    if (not db.open(dbfile, 
        kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE)):
        sys.stderr.write("open error: " + str(db.error()))
    
    # get the last index from the database
    last_index = config.get("DATABASE", "last_index").strip()
    result = db.get(last_index)
    if result:
        next_index = int(result) + 1
    else:
        next_index = 0

    # Write the key-value pairs to the db
    for akey in pol.keys():
        key = "%s_%s" %(akey, next_index)
        if (not db.set(key, pol[akey])):
                sys.stderr.write("unable to write to db: " + str(db.error()))
    # update the last index
    if (not db.set("last_index", next_index)):
        sys.stderr.write("unable to write last index to db: " + str(db.error()))
    # Close the db
    if (not db.close()):
        sys.stderr.write("unable to close the db: " + str(db.error()))

def runStore():
    # Get the schema used for the key-value pair database
    config = ConfigParser.ConfigParser()
    config.read("./config/policy_schema.cfg")
    policy_exists = False

    # Read in the form data
    aform = json.load(sys.stdin)
    
    print "Content-Type: application/json\n"
    
    # Process the form data and create policy
    aPolicy = Policy(config)
    aPolicy.processForm(aform)
    aPolicy.createXML(aform)
 
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
        dumpToKVDb(aPolicy.policy, config)

    #print "Input:"
    # print aform
    print ""
    #print aPolicy.policy["policy_object"]
    print json.dumps({'policy_exists': policy_exists})

if __name__ == '__main__':
    runStore()
