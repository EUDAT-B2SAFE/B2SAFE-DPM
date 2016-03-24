#!/usr/bin/env python
import time
import json
import flask
import flask.ext.httpauth
import policy
import common
import log
import log_search
import user

CONFIG_OBJECT = common.get_config()

auth = flask.ext.httpauth.HTTPBasicAuth()

policy_app = flask.Flask(__name__)
policy_app.config.from_object(__name__)

@auth.verify_password
def verify_password(user_id, password):
    '''Verify the user account'''
    user_acct = {}
    user_acct = user.verify_auth_token(user_id,
                                       policy_app.config["CONFIG_OBJECT"])
    if not user_acct:
        user_valid = user.verify_password(user_id, password,
                                          policy_app.config["CONFIG_OBJECT"])
        if not user_valid:
            return False
        else:
            user_acct = {}
            user_acct["name"] = user_id
    flask.g.user_acct = user_acct
    return True

@policy_app.route('/')
@auth.login_required
def root_url():
    return ""

@policy_app.route('/token')
@auth.login_required
def get_auth_token():
    '''Get the token for authorised users'''
    expiry = 600
    utc_time = time.gmtime()
    response = user.generate_auth_token(flask.g.user_acct["name"], expiry)
    json_output = {}
    json_output['token'] =  response.decode('ascii')
    json_output['created'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", utc_time)
    json_output['expiry'] = expiry
    return flask.jsonify(json_output)


@policy_app.route('/policy')
@auth.login_required
def get_policy():
    '''Get the policy for the given identifier'''
    response = "Unrecognised request", 400
    input_args = flask.request.args
    if 'identifier' in input_args:
        response = policy.download(flask.g.user_acct["communities"],
                                   input_args['identifier'],
                                   policy_app.config["CONFIG_OBJECT"])
    return response

@policy_app.route('/search/policy')
@auth.login_required
def search_policy():
    '''Search for policies'''
    valid_params = ["before", "after", "community", "author",
                    "source_identifier", "target_identifier",
                    "source_hostname", "target_hostname", "action", "removed"]
    response = "Unrecognised request", 400
    input_args = flask.request.args
    args_ok = False
    for input_arg in input_args:
        if input_arg in valid_params:
            args_ok = True
    if args_ok:
        response = policy.search(flask.g.user_acct["communities"], input_args,
                                 policy_app.config["CONFIG_OBJECT"])
    return response

@policy_app.route('/policy/log', methods=["GET", "POST"])
@auth.login_required
def load_log():
    '''Load the log entry into the database'''
    if flask.request.method == "GET":
        log_info = flask.request.args
    elif flask.request.method == "POST":
        log_info = flask.request.json
    result = log.upload(flask.g.user_acct["communities"],
                        policy_app.config["CONFIG_OBJECT"], log_info)
    if len(result["data"]) == 0:
        response = json.dumps(result["message"]), result["return_code"]
    else:
        response = json.dumps(result["data"]), result["return_code"]

    return response

@policy_app.route("/policy/log/search/state", methods=["GET"])
@auth.login_required
def get_state():
    '''Get the available states for the logs'''
    response = log_search.get_states(flask.g.user_acct["communities"],
                                     policy_app.config["CONFIG_OBJECT"])
    return response

@policy_app.route("/policy/log/search", methods=["GET", "POST"])
@auth.login_required
def search_logs():
    '''Search the log documents'''
    valid_params = ["before", "after", "community", "hostname",
                    "identifier", "action", "state"]
    response = "Unrecognised request", 400
    input_args = flask.request.args
    args_ok = False
    for input_arg in input_args:
        if input_arg in valid_params:
            args_ok = True
    if args_ok:
        response = log_search.search(flask.g.user_acct["communities"],
                                     input_args,
                                     policy_app.config["CONFIG_OBJECT"])
    return response

if __name__ == '__main__':
    policy_app.run(debug=True)
