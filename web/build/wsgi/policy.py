'''Module to interact with policies stored in the database'''
import sqlite3
import json
import os
import ConfigParser

def get_policy_keys(dbase, cfg, identifier):
    '''Get the policy and md5 key for a given policy identifier'''

    index = -1
    policy_key = ''
    policy_md5_key = ''
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    cursor.execute('''select key from policies where value = ? and
                   key like 'policy_id%' ''', (identifier,))
    results = cursor.fetchall()

    if len(results) > 1 or len(results) == 0:
        index = -1
    else:
        key = results[0][0]
        index = key.split("_")[-1]
        policy_key = '%s_%s' % (cfg.get('POLICY_SCHEMA', 'object'), index)
        policy_md5_key = '%s_%s' % (cfg.get('POLICY_SCHEMA', 'md5'), index)

    return policy_key, policy_md5_key

def get_policy(dbase, key):
    '''Get the policy from the database'''

    policy = ''
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    cursor.execute('''select value from policies where key = ?''',
                   (key,))
    results = cursor.fetchall()
    if len(results) > 1:
        policy = ''
    else:
        policy = results[0][0]
    return policy

def get_config():
    '''Return the config file object'''

    config_file = os.path.join(os.path.dirname(__file__), 'policy_cli.cfg')
    top_config = ConfigParser.ConfigParser()
    top_config.read(config_file)

    config = ConfigParser.ConfigParser()
    config.read(top_config.get('POLICY', 'policy_config'))
    return config

def get_policy_md5(dbase, key):
    '''Get the md5 value for the policy from the database'''
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    cursor.execute('''select value from policies where key = ?''',
                   (key,))
    results = cursor.fetchall()
    if len(results) > 1:
        policy_md5 = ''
    else:
        policy_md5 = results[0][0]
    return policy_md5

def download(identifier):
    '''get the policy from the database and send to the user'''

    config = get_config()
    response = json.dumps({})
    # Open the database
    dbfile = config.get('DATABASE', 'name').strip()
    if not dbfile:
        response = "Server database error", 500
        return response

    policy_key, policy_md5_key = get_policy_keys(dbfile, config, identifier)
    if len(policy_key) != 0 and len(policy_md5_key) != 0:
        policy = get_policy(dbfile, policy_key)
        policy_md5 = get_policy_md5(dbfile, policy_md5_key)

        # create the JSON and send to the user
        json_policy = {'policy': policy, 'md5': policy_md5,
                       'identifier': identifier}
        response = json.dumps(json_policy)
    return response
