import json
import sqlite3
import common

def find_states(communities, config):
    '''Get the states for all the log entries'''
    states = []
    conn = sqlite3.connect(config.get("DATABASE", "name"))
    cursor = conn.cursor()
    cursor.execute("select key, value from policies where key like 'log_state_%'")
    results = cursor.fetchall()
    for result in results:
        index = result[1].split("_")[-2]
        if check_allowed(index, communities, config):
            states.append(result[0])
    return states

def check_allowed(index, communities, config):
    '''Check if the user is allowed to view the log entry'''
    allowed = False
    conn = sqlite3.connect(config.get("DATABASE", "name"))
    cursor = conn.cursor()
    community_key = "%s_%s" % (config.get("POLICY_SCHEMA", "community"), index)
    cursor.execute("select value from policies where key = ?", (community_key,))
    results = cursor.fetchall()
    if len(results) == 1:
        if results[0][0] in communities:
            allowed = True
    return allowed

def get_states(communities, config):
    '''Return the list of states'''
    states = json.dumps(find_states(communities, config))
    return states, 200

def get_indexes(config, communities, search_params=None):
    '''Return the indexes for the matching log documents'''

    search_keys = {"after": ["log_timestamp_",
                             "key like '%s%%' and value > ?", "log"],
                   "before": ["log_timestamp_",
                              "key like '%s%%' and value <= ?", "log"],
                   "state": ["log_state_",
                             "key like '%s%%' and value = ?", "log"],
                   "hostname": ["log_hostname_",
                                "key like '%s%%' and value = ?", "log"],
                   "identifier": ["log_policy_identifier_",
                                  "key like '%s%%' and value = ?", "log"],
                   "community": ["policy_community_",
                                 "key like '%s%%' and value = ?", "data"],
                   "action": ["action_type_",
                              "key like '%s%%' and value = ?", "data"],
                   "author": ["policy_author_",
                              "key like '%s%%' and value = ?", "data"]}

    indexes = common.find_indexes(config, search_keys, search_params)
    output = []
    for index in indexes:
        if check_allowed(index, communities, config):
            output.append(index)
    indexes = output
    return indexes

def get_documents(config, indexes):
    '''Return the log documents corresponding to the list of indexes'''
    log_documents = []
    conn = sqlite3.connect(config.get("DATABASE", "name"))
    cursor = conn.cursor()
    for index in indexes:
        log_document = {}
        query = "select value from policies where key = ?"
        if len(index.split("_")) == 1:
            index = "%%_%s" % index
            query = "select value from policies where key like ?"

        for item in config.items("LOG_SCHEMA"):
            if "last_index" in  item[0]:
                continue

            db_key = "%s_%s" % (item[1], index)
            cursor.execute(query, (db_key,))
            results = cursor.fetchall()

            if len(results) == 0:
                log_document[item[0]] = "null"
            else:
                log_document[item[0]] = results[0][0]

        log_exists = False
        bad_log = False
        for log_key in log_document.keys():
            if log_document[log_key] != "null":
                log_exists = True
            if log_document[log_key] == "null" and log_key != "comment":
                bad_log = True

        if log_exists and bad_log:
            log_documents = [{"error":
                              "Log information incomplete in database"}]
            break
        else:
            if log_exists and not log_doc_exists(log_documents, log_document):
                log_documents.append(log_document)

    return log_documents

def log_doc_exists(logs, new_log):
    '''Compare if the log document already exists in the list'''
    match = True
    if len(logs) == 0:
        match = False
    else:
        for log in logs:
            for key in log.keys():
                if key in new_log:
                    if new_log[key] != log[key]:
                        match = False
                        break
                else:
                    match = False
                    break
    return match

def search(communities, params, cfg):
    '''Return the log documents matching the search criteria'''
    search_params = {}
    results = []
    response = None
    bad_format = False
    for key in params.keys():
        search_params[key] = params[key]
        if key == "before" or key == "after":
            timestamp = common.convert_time(params[key])
            if timestamp is None:
                bad_format = True
                break
    if not bad_format:
        indexes = get_indexes(cfg, communities, search_params)
        results = get_documents(cfg, indexes)
        response = json.dumps(results), 200
    else:
        response = json.dumps({"error": "Incorrect format for timestamp"}), 400
    return response
