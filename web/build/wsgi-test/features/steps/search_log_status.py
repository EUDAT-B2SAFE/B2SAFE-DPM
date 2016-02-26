import json
import behave
import wsgi.common
import wsgi.log_search

@given(u'a valid request')
def step_impl(context):
    context.states = ["start", "end"]

@then(u'the server returns the list of states for available logs')
def step_impl(context):
    states = wsgi.log_search.find_states(context.cfg)
    assert states == context.states

@given('a valid user submits a valid query')
def step_impl(context):
    context.status = ['start', 'end']

@then('the user receives a "{text}" response')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search/state")
    assert int(text) == response.status_code

@then('the user receives the list of log states')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search/state")
    assert context.status == json.loads(response.data)
