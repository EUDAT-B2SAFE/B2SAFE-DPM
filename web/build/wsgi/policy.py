'''Module to interact with policies stored in the database'''
import sqlite3
import json
import time
import common

def get_policy_objects(cfg, indexes):
    '''Return the list of policy objects for the indexes'''

    policy_objects = []
    policy_keys = {"policy_id":"identifier", "policy_md5":"checksum",
                   "policy_ctime":"ctime"}

    conn = sqlite3.connect(cfg.get("DATABASE", "name"))
    cursor = conn.cursor()
    for index in indexes:
        policy_object = {}
        for key in policy_keys.keys():
            key_str = "%s_%s" % (key, index)
            cursor.execute('''select value from policies where key = ?''',
                           (key_str,))
            results = cursor.fetchall()
            if len(results) == 1:
                if key == "policy_id":
                    policy_object[policy_keys[key]] = "%s=%s" %\
                    (cfg.get("DATABASE", "fetch_string"), results[0][0])
                else:
                    policy_object[policy_keys[key]] = results[0][0]
        policy_objects.append(policy_object)

    return policy_objects

def filter_removed(cursor, indexes):
    '''Filter out the policies that have been removed'''
    result = None
    out_indexes = []
    for index in indexes:
        key = "policy_removed_%s" % index
        search_str = "select value from policies where key = ?"
        cursor.execute(search_str, (key,))
        result = cursor.fetchone()
        if result[0] == "false":
            out_indexes.append(index)
    return out_indexes

def get_indexes(config, search_params=None, log_flag=False):
    '''Get the policy identifier keys for all policies satisfying the search
    criteria'''
    indexes = []
    search_str = ""
    search_keys = {"after": ["policy_ctime_", "value > ? and key like '%s%%'",
                             "data"],
                   "before": ["policy_ctime_", "value <= ? and key like '%s%%'",
                              "data"],
                   "community": ["policy_community_",
                                 "value = ? and key like '%s%%'", "data"],
                    "source_hostname": ["src_hostname_",
                                        "value = ? and key like '%s%%'", "data"],
                    "target_hostname": ["tgt_hostname_",
                                        "value = ? and key like '%s%%'", "data"],
                    "action": ["action_type_",
                               "value = ? and key like '%s%%'", "data"],
                    "source_identifier": ["src_identifier_",
                                          "value = ? and key like '%s%%'",
                                          "data"],
                    "target_identifier": ["tgt_identifier_",
                                          "value = ? and key like '%s%%'",
                                          "data"],
                    "author": ["policy_author_",
                               "value = ? and key like '%s%%'", "data"]}

    indexes = common.find_indexes(config, search_keys, search_params)

    conn = sqlite3.connect(config.get("DATABASE", "name"))
    cursor = conn.cursor()

    if 'removed' in search_params:
        search_key = "policy_removed_"
        search_str = "select key from policies where value = ? and " +\
                     "key like '%s%%'" % search_key
        indexes = common.search_for_indexes(cursor, search_str,
                                            search_params['removed'],
                                            indexes, "data")
    else:
        indexes = filter_removed(cursor, indexes)
    return indexes

def get_policy_keys(cfg, identifier):
    '''Get the policy and md5 key for a given policy identifier'''

    index = -1
    policy_key = ''
    policy_md5_key = ''
    conn = sqlite3.connect(cfg.get("DATABASE", "name"))
    cursor = conn.cursor()
    cursor.execute('''select key from policies where value = ? and
                   key like 'policy_id%' ''', (identifier.strip(),))
    results = cursor.fetchall()

    if len(results) > 1 or len(results) == 0:
        index = -1
    else:
        key = results[0][0]
        index = key.split("_")[-1]
        policy_key = '%s_%s' % (cfg.get('POLICY_SCHEMA', 'object'), index)
        policy_md5_key = '%s_%s' % (cfg.get('POLICY_SCHEMA', 'md5'), index)

    return policy_key, policy_md5_key

def get_policy(cfg, key):
    '''Get the policy from the database'''

    policy = ''
    conn = sqlite3.connect(cfg.get("DATABASE", "name"))
    cursor = conn.cursor()
    cursor.execute('''select value from policies where key = ?''',
                   (key,))
    results = cursor.fetchall()
    if len(results) > 1:
        policy = ''
    else:
        policy = results[0][0]
    return policy

def get_policy_md5(cfg, key):
    '''Get the md5 value for the policy from the database'''
    conn = sqlite3.connect(cfg.get("DATABASE", "name"))
    cursor = conn.cursor()
    cursor.execute('''select value from policies where key = ?''',
                   (key,))
    results = cursor.fetchall()
    if len(results) > 1:
        policy_md5 = ''
    else:
        policy_md5 = results[0][0]
    return policy_md5

def download(identifier, config):
    '''get the policy from the database and send to the user'''
    dbfile = None
    response = json.dumps({})
    # Open the database
    dbfile = config.get('DATABASE', 'name').strip()
    if not dbfile:
        response = "Server database error", 500
        return response

    policy_key, policy_md5_key = get_policy_keys(config, identifier)

    if len(policy_key) != 0 and len(policy_md5_key) != 0:
        policy = get_policy(config, policy_key)
        policy_md5 = get_policy_md5(config, policy_md5_key)

        # create the JSON and send to the user
        json_policy = {'policy': policy, 'md5': policy_md5,
                       'identifier': identifier}
        response = json.dumps(json_policy)
    return response

def search(params, config):
    '''search for the policy objects'''
    response = json.dumps([])
    search_params = {}
    for key in params.keys():
        search_params[key] = params[key]
    indexes = get_indexes(config, search_params)
    policy_objects = get_policy_objects(config, indexes)
    response = json.dumps(policy_objects)
    return response
