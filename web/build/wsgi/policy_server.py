#!/usr/bin/env python
import flask
import json
import policy
import common
import log
import log_search

CONFIG_OBJECT = common.get_config()

policy_app = flask.Flask(__name__)
policy_app.config.from_object(__name__)

@policy_app.route('/policy')
def get_policy():
    '''Get the policy for the given identifier'''
    response = "Unrecognised request", 400
    input_args = flask.request.args
    if 'identifier' in input_args:
        response = policy.download(input_args['identifier'],
                                   policy_app.config["CONFIG_OBJECT"])
    return response

@policy_app.route('/search/policy')
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
        response = policy.search(input_args, policy_app.config["CONFIG_OBJECT"])
    return response

@policy_app.route('/policy/log', methods=["GET", "POST"])
def load_log():
    '''Load the log entry into the database'''
    if flask.request.method == "GET":
        log_info = flask.request.args
    elif flask.request.method == "POST":
        log_info = flask.request.json
    result = log.upload(policy_app.config["CONFIG_OBJECT"], log_info)
    if len(result["data"]) == 0:
        response = json.dumps(result["message"]), result["return_code"]
    else:
        response = json.dumps(result["data"]), result["return_code"]

    return response

@policy_app.route("/policy/log/search/state", methods=["GET"])
def get_state():
    '''Get the available states for the logs'''
    response = log_search.get_states(policy_app.config["CONFIG_OBJECT"])
    return response

@policy_app.route("/policy/log/search", methods=["GET", "POST"])
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
        response = log_search.search(input_args, policy_app.config["CONFIG_OBJECT"])
    return response

if __name__ == '__main__':
    policy_app.run(debug=True)
