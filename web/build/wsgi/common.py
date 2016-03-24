import ConfigParser
import os
import sqlite3
import time

def find_indexes(config, search_keys, search_params):
    '''Return the indexes for the given query'''
    indexes = []
    conn = sqlite3.connect(config.get("DATABASE", "name"))
    cursor = conn.cursor()
    # First do the query to get the keys for the ctime with values greater
    # than the input. Then  we get the indexes and create the policy_id
    # and return that list
    for key in search_keys.keys():
        if key not in search_params:
            continue
        if key == 'after' or key == 'before':
            param = convert_time(search_params[key])
            if param is None:
                continue
        else:
            param = search_params[key]

        search_str = "select key from policies where " + \
            search_keys[key][1] % search_keys[key][0]

        indexes = search_for_indexes(cursor, search_str, param, indexes,
                                     search_keys[key][2])
    return indexes

def search_for_indexes(crsr, search_string, param, indexes, data_type):
    '''Search the database for the indexes'''
    results = []
    data_indexes = []
    log_indexes = []
    crsr.execute(search_string, (param,))
    results = crsr.fetchall()
    if len(results) > 0:
        for result in results:
            if data_type == "data":
                data_indexes.append(result[0].split("_")[-1])
            elif data_type == "log":
                sub_index, index = result[0].split("_")[-2:]
                log_indexes.append("%s_%s" % (sub_index, index))
    if len(indexes) > 0:
        indexes = find_common_indexes(indexes, data_indexes, log_indexes)
    else:
        indexes = data_indexes + log_indexes
    return indexes

def find_common_indexes(common_indexes, data_indexes, log_indexes):
    '''Find the common indexes and return the result'''
    output_indexes = []
    for data_index in data_indexes:
        if data_index not in common_indexes:
            for common_index in common_indexes:
                cpts = common_index.split("_")
                if len(cpts) == 2 and cpts[1] == data_index:
                    output_indexes.append(data_index)
                    output_indexes.append(common_index)
                    break
        else:
            output_indexes.append(data_index)
            for common_index in common_indexes:
                cpts = common_index.split("_")
                if len(cpts) == 2 and cpts[1] == data_index:
                    output_indexes.append(common_index)
                    break

    for log_index in log_indexes:
        if log_index not in common_indexes:
            cpts = log_index.split("_")
            for common_index in common_indexes:
                if cpts[1] == common_index:
                    output_indexes.append(log_index)
                    output_indexes.append(common_index)
                    break
        else:
            output_indexes.append(log_index)
            cpts = log_index.split("_")
            for common_index in common_indexes:
                if cpts[1] == common_index:
                    output_indexes.append(common_index)
                    break

    return output_indexes

def get_config():
    '''Return the config file object'''
    config_file = os.path.join(os.path.dirname(__file__), 'policy_cli.cfg')
    top_config = ConfigParser.ConfigParser()
    top_config.read(config_file)

    config = ConfigParser.ConfigParser()
    config.read(top_config.get('POLICY', 'policy_config'))
    return config

def convert_time(input_time):
    '''Convert the input date to seconds'''
    output_time = None
    try:
        output_time = int(time.mktime(time.strptime(input_time, "%Y-%m-%d")))
    except ValueError:
        try:
            output_time = int(time.mktime(time.strptime(input_time,
                                                        "%Y-%m-%dT%H:%M:%S")))
        except ValueError:
            output_time = None
    return output_time
