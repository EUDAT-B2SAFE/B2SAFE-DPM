import behave
import wsgi.policy
import os

@behave.given('a correct policy identifier')
def step_impl(context):
    '''Set up the environment for this scenario'''
    context.identifier = 'a5e4907e-83a4-49f6-81ae-143d443af60e'
    context.policy_id = 'policy_object_10'
    context.policy_md5_id = 'policy_md5_10'
    policy_file = os.path.join(context.env_dir, 'policy.txt')
    with file(policy_file, 'r') as fin:
        data = fin.read(-1)
        fin.close()
        md5, policy = data.split('|')
        context.policy = policy
        context.md5 = md5

@behave.then('the server looks up the database index for the policy identifier')
def step_impl(context):
    '''Test the policy identifier search'''
    policy_key, policy_md5_key = wsgi.policy.get_policy_keys(context.dbfile, context.cfg,
                                                             context.identifier)
    assert policy_key == context.policy_id and policy_md5_key == context.policy_md5_id

@behave.then('the server uses the index to find the policy object')
def step_impl(context):
    '''Test the policy search'''
    policy = wsgi.policy.get_policy(context.dbfile, context.policy_id)
    assert policy == context.policy

@behave.then('the server uses the index to find the md5 for the policy')
def step_impl(context):
    md5 = wsgi.policy.get_policy_md5(context.dbfile, context.policy_md5_id)
    print('md5 is ', md5)
    print('context md5 ', context.md5)
    assert md5 == context.md5

@behave.then('the server returns the policy and the md5')
def step_impl(context):
    assert False
