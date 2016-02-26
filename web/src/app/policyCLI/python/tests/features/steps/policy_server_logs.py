import json
import behave
import wsgi.log

@given(u'valid log information')
def step_impl(context):
    context.good_log_document = context.log_documents[0]

@then(u'the server checks if the log information conforms to the schema')
def step_impl(context):
    schema_ok = wsgi.log.check_schema(context.cfg, context.good_log_document)
    assert schema_ok == True

@then(u'the server loads the information into the database')
def step_impl(context):
    stored_doc = wsgi.log.load_db(context.cfg, context.good_log_document)
    result = json.dumps(stored_doc)
    assert stored_doc == context.good_log_document
