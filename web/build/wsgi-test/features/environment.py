import sqlite3
import os
import json
import wsgi.policy

def before_scenario(context, scenario):
    '''prepare the scenario'''

    context.flask_app = None
    context.identifier = ''
    context.policy_key = ''
    context.policy = ''
    context.md5 = ''
    context.cfg = wsgi.policy.get_config()
    context.env_dir = os.path.dirname(__file__)

    # Read in the policy data and load into a test database. This just needs
    # to be done once
    context.dbfile = os.path.join(os.path.dirname(__file__), 'test_policies.db')

    if not os.path.isfile(context.dbfile):
        con = sqlite3.connect(context.dbfile)
        cur = con.cursor()
        cur.execute('''create table policies(key text, value text)''')
        con.commit()

        data = os.path.join(os.path.dirname(__file__), 'testData.json')
        with file(data, 'r') as fin:
            con = sqlite3.connect(context.dbfile)
            cur = con.cursor()
            policy = json.load(fin)
            for key in policy.keys():
                cur.execute('''insert into policies values(?,?)''',
                            (key, policy[key]))
            con.commit()
