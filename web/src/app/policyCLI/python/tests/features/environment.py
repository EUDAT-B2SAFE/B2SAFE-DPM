import sqlite3
import os
import json
import ConfigParser
import wsgi.policy
import wsgi.common
import wsgi.policy_server

def load_db(config):
    '''Load the database'''

    if not os.path.isfile(config.get("DATABASE", "name")):
        con = sqlite3.connect(config.get("DATABASE", "name"))
        cur = con.cursor()
        cur.execute('''create table policies(key text, value text)''')
        con.commit()

        data = os.path.join(os.path.dirname(__file__), 'testData.json')
        with file(data, 'r') as fin:
            con = sqlite3.connect(config.get("DATABASE", "name"))
            cur = con.cursor()
            policies = json.load(fin)
            for policy in policies:
                for key in policy.keys():
                    cur.execute('''insert into policies values(?,?)''',
                                (key, policy[key]))
            con.commit()

def remove_db(config):
    '''Delete the database'''
    os.unlink(config.get("DATABASE", "name"))

def prepare_wsgi(config):
    '''Prepare the wsgi server configuration'''
    wsgi.policy_server.policy_app.config["CONFIG_OBJECT"] = config
    wsgi.policy_server.policy_app.config["TESTING"] = True
    flask_app = wsgi.policy_server.policy_app.test_client()
    return flask_app

def set_config():
    '''Set the test config file'''
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "policy_test.cfg"))
    config.set("DATABASE", "name", os.path.join(os.path.dirname(__file__),
                                                "policy_test.db"))
    config.set("DATABASE", "fetch_string",
               "http://example.org/getPolicy?identifier")
    return config

def load_logs(log_file):
    '''Load the log information from json file into list of dicts'''
    with file(os.path.join(os.path.dirname(__file__), log_file), "r") as fin:
        log_documents = json.load(fin)
        fin.close()
    return log_documents

def load_db_logs(config):
    '''Load the database with log information'''

    con = sqlite3.connect(config.get("DATABASE", "name"))
    cur = con.cursor()
    log_infos = load_logs("testLog.json")
    count = 1
    for log_info in log_infos:
        cur.execute("insert into policies(key, value) values(?, ?)",
                    ("log_policy_identifier_0_%s" % count, log_info["identifier"]))
        if "comment" in log_info:
            cur.execute("insert into policies(key, value) values(?, ?)",
                        ("log_comment_0_%s" % count, log_info["comment"]))
        cur.execute("insert into policies(key, value) values(?, ?)",
                    ("log_state_0_%s" % count, log_info["state"]))
        cur.execute("insert into policies(key, value) values(?, ?)",
                    ("log_timestamp_0_%s" % count, log_info["timestamp"]))
        cur.execute("insert into policies(key, value) values(?, ?)",
                    ("log_hostname_0_%s" % count, log_info["hostname"]))
        count += 1
    cur.execute("insert into policies(key, value) values(?, ?)",
                ("log_last_index_%s" % count, 0))
    con.commit()

def before_scenario(context, scenario):
    '''prepare the scenario'''

    context.identifier = ''
    context.policy_key = ''
    context.policy = ''
    context.md5 = ''
    context.after = ''
    context.before = ''
    context.flask_app = None
    context.cfg = wsgi.common.get_config()
    context.env_dir = os.path.dirname(__file__)

    context.cfg = set_config()
    load_db(context.cfg)
    context.flask_app = prepare_wsgi(context.cfg)
    context.log_documents = load_logs("testLog.json")
    context.bad_log_documents = load_logs("testBadLog.json")
    if (scenario.name == "Server returns log states" or
        scenario.name == "A valid user searches for the valid log states"):
        load_db(context.cfg)
        load_db_logs(context.cfg)

def before_feature(context, feature):
    '''Setup before the feature'''
    context.cfg = set_config()
    if feature.name == "Search for log documents":
        load_db(context.cfg)
        load_db_logs(context.cfg)
        context.log_tests = True
    else:
        context.log_tests = False

def after_feature(context, feature):
    '''Tear-down the feature'''
    if feature.name == "Search for log documents":
        remove_db(context.cfg)

def after_scenario(context, scenario):
    '''tear-down the environment for the scenario'''
    if (not context.log_tests):
        remove_db(context.cfg)
