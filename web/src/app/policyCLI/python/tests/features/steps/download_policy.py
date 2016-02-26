#!/usr/bin/env python
import behave
import json
import os
import wsgi.policy
import wsgi.policy_server

@behave.given('a valid user submits a valid policy identifier')
def step_impl(context):
    policy_file = os.path.join(context.env_dir, 'policy.txt')
    with file(policy_file, 'r') as fin:
        data = fin.read(-1)
        fin.close()
        md5, policy = data.split('|')
        context.policy = policy
        context.md5 = md5

    context.identifier = 'a5e4907e-83a4-49f6-81ae-143d443af60e'

@behave.then('the user gets a "{text}" response')
def step_impl(context, text):
    '''Test the response from the server to the request'''
    response = context.flask_app.get('/getPolicy?identifier=%s' %\
                                     context.identifier)
    assert response.status_code == int(text)

@behave.then('the user receives the policy object that matches the identifier')
def step_impl(context):
    '''Test the returned policy object'''
    response = context.flask_app.get('/getPolicy?identifier=%s' %\
                                     context.identifier)
    policy_obj = json.loads(response.data)
    assert context.identifier == policy_obj['identifier'] and \
           context.md5 == policy_obj['md5'] and \
           context.policy == policy_obj['policy']

@behave.then('the user does not receive an empty policy object')
def step_impl(context):
    '''Test an invalid policy identifier'''
    identifier = '12345678-1234-1234-1234-123456789012'
    response = context.flask_app.get('/getPolicy?identifier=%s' %\
                                     identifier)
    policy_obj = json.loads(response.data)
    assert policy_obj == {}
