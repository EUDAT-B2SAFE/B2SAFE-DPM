import json
import wsgi.common
import wsgi.log
import behave

@given(u'a valid user uploads log information')
def step_impl(context):
    context.response = "JSON does not conform to schema"

@then(u'the user receives a "{text}" message if the log does not conform to the schema')
def step_impl(context, text):
    response = context.flask_app.post("policy/log",
                                      headers={"Content-Type": "application/json"},
                                      data=json.dumps(context.bad_log_documents))
    message = json.loads(json.loads(response.data))
    assert response.status_code == int(text) and message["error"] == context.response

@then(u'the user receives a "201" message and the result of the log upload')
def step_impl(context):
    response = context.flask_app.post("policy/log",
                                      headers={"Content-Type": "application/json"},
                                      data=json.dumps(context.log_documents))
    assert json.loads(response.data) == context.log_documents
