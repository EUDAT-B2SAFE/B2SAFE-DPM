import json
import behave
import wsgi.log_search

@given(u'an after date')
def step_impl(context):
    context.after = "2016-02-22T10:00:00"
    context.bad_after = "2016/01/30"
    context.indexes = ["0_2"]
    context.log_documents = [{'timestamp': u'1456149606', 'state': u'end',
                              'comment': 'null',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the server reports an error if the after date is invalid')
def step_impl(context):
    result = wsgi.common.convert_time(context.bad_after)
    assert result == None

@then(u'the server searches for the indexes for the log documents matching the after date')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                         search_params={"after": context.after})
    assert indexes == context.indexes

@then(u'the server returns the list of log documents matching the after date')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    assert log_documents == context.log_documents

@given(u'a before date')
def step_impl(context):
    context.before = "2016-02-22T10:00:00"
    context.bad_before = "2016/02/28"
    context.indexes = ["0_1"]
    context.log_documents = [{'comment': u'test comment',
                              'timestamp': u'1456057774', 'state': u'start',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the server reports an error if the before date is invalid')
def step_impl(context):
    result = wsgi.common.convert_time(context.bad_before)
    assert result == None

@then(u'the server searches for the indexes for the log documents matching the before date')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                         search_params={"before": context.before})
    assert indexes == context.indexes

@then(u'the server returns the list of log documents matching the before date')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    assert log_documents == context.log_documents

@given(u'a state')
def step_impl(context):
    context.state = "start"
    context.indexes = ["0_1"]
    context.log_documents = [{'comment': u'test comment',
                              'timestamp': u'1456057774', 'state': u'start',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the server searches for the indexes for the log documents matching the state')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                          search_params={"state": context.state})
    assert indexes == context.indexes

@then(u'the server returns the log documents matching the state')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    assert log_documents == context.log_documents

@given(u'a hostname')
def step_impl(context):
    context.hostname = "data.repo.cineca.it"
    context.indexes = ["0_1", "0_2"]
    context.log_documents = [{'timestamp': u'1456149606', 'state': u'end',
                              'hostname': u'data.repo.cineca.it',
                              'comment': u'null',
                              'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'},
                             {'comment': u'test comment',
                              'timestamp': u'1456057774', 'state': u'start',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the server searches for the indexes for the log documents matching the hostname')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                          search_params={"hostname": context.hostname})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the log documents matching the hostname')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    match = True
    for log_document in log_documents:
        if log_document not in context.log_documents:
            match = False
            break
    assert match

@given(u'an identifier')
def step_impl(context):
    context.identifier = "a5e4907e-1234-49f6-81ae-143d443af60e"
    context.indexes = ["0_1"]
    context.log_documents = [{'comment': u'test comment',
                              'timestamp': u'1456057774', 'state': u'start',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the server searches for the indexes for the log documents matching the identifier')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                          search_params={"identifier":
                                                         context.identifier})
    assert indexes == context.indexes

@then(u'the server returns the log documents matching the identifier')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    assert log_documents == context.log_documents

@given(u'a community')
def step_impl(context):
    context.community = "clarin"
    context.indexes = ["1", "2", "3", "10", "11"]
    context.log_documents = [{'comment': u'test comment',
                              'timestamp': u'1456057774', 'state': u'start',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'},
                             {'comment': 'null', 'timestamp': u'1456149606',
                              'state': u'end',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the server searches for the indexes for the log documents matching the community')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                          search_params={"community":
                                                         context.community})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the log documents matching the community')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    match = True
    for log_document in log_documents:
        if log_document not in context.log_documents:
            match = False
            break
    assert match

@given(u'an action')
def step_impl(context):
    context.action = "replicate"
    context.indexes = ["1","2","3","10","11"]
    context.log_documents = [{'comment': u'test comment',
                              'timestamp': u'1456057774', 'state': u'start',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'},
                             {'comment': 'null', 'timestamp': u'1456149606',
                              'state': u'end', 'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the server searches for the indexes for the log documents matching the action')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                          search_params={"action":
                                                         context.action})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the log documents matching the action')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    match = True
    for log_document in log_documents:
        if log_document not in context.log_documents:
            match = False
            break
    assert match

@given(u'a compound query')
def step_impl(context):
    context.action = "replicate"
    context.before = "2016-02-22T00:00:00"
    context.state = "start"
    context.indexes = [u'1', u'0_1']
    context.log_documents = [{'comment': u'test comment',
                              'timestamp': u'1456057774', 'state': u'start',
                              'hostname': u'data.repo.cineca.it',
                              'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the server searches for the indexes for the log documents matching the compound query')
def step_impl(context):
    indexes = wsgi.log_search.get_indexes(context.cfg,
                                          search_params={"action":
                                                         context.action,
                                                         "before":
                                                         context.before,
                                                         "state":
                                                         context.state})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the log documents matching the compound query')
def step_impl(context):
    log_documents = wsgi.log_search.get_documents(context.cfg, context.indexes)
    match = True
    for log_document in log_documents:
        if log_document not in context.log_documents:
            match = False
            break
    assert match

@given(u'a user supplies an after date query')
def step_impl(context):
    context.after = "2016-02-22T00:00:00"
    context.bad_after = "2016/02/20"
    context.log_documents = [{u'comment': u'null', u'timestamp': u'1456149606',
                              u'state': u'end', u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response if the after date is invalid')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?after=%s" %
                                     context.bad_after)
    assert response.status_code == int(text)

@then(u'the user receives a "{text}" response if the after date is valid')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?after=%s" %
                                     context.after)
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the after date')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search?after=%s" %
                                     context.after)
    log_documents = json.loads(response.data)
    assert log_documents == context.log_documents

@given(u'a user supplies an before date query')
def step_impl(context):
    context.before = "2016-02-22T00:00:00"
    context.log_documents = [{u'comment': u'test comment',
                              u'timestamp': u'1456057774', u'state': u'start',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response if the before date is valid')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?before=%s" %
                                     context.before)
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the before date')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search?before=%s" %
                                     context.before)
    log_documents = json.loads(response.data)
    assert log_documents == context.log_documents

@given(u'a user supplies a state query')
def step_impl(context):
    context.state = "start"
    context.log_documents = [{u'comment': u'test comment',
                              u'timestamp': u'1456057774', u'state': u'start',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response for the state query')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?state=%s" %
                                     context.state)
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the state query')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search?state=%s" %
                                     context.state)
    log_documents = json.loads(response.data)
    assert log_documents == context.log_documents

@given(u'a user supplies a hostname query')
def step_impl(context):
    context.hostname = "data.repo.cineca.it"
    context.log_documents = [{u'comment': u'test comment',
                              u'timestamp': u'1456057774', u'state': u'start',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'},
                             {u'comment': u'null', u'timestamp': u'1456149606',
                              u'state': u'end',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response for the hostname query')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?hostname=%s" %
                                     context.hostname)
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the hostname query')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search?hostname=%s" %
                                     context.hostname)
    log_documents = json.loads(response.data)
    assert log_documents == context.log_documents

@given(u'a user supplies a identifier query')
def step_impl(context):
    context.identifier = "a5e4907e-1234-49f6-81ae-143d443af60e"
    context.log_documents = [{u'comment': u'test comment',
                              u'timestamp': u'1456057774', u'state': u'start',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response for the identifier query')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?identifier=%s" %
                                     context.identifier)
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the identifier query')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search?identifier=%s" %
                                     context.identifier)
    log_documents = json.loads(response.data)
    print("log_documents ", log_documents)
    assert log_documents == context.log_documents

@given(u'a user supplies a action query')
def step_impl(context):
    context.action = "replicate"
    context.log_documents = [{u'comment': u'test comment',
                              u'timestamp': u'1456057774', u'state': u'start',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'},
                             {u'comment': u'null', u'timestamp': u'1456149606',
                              u'state': u'end',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response for the action query')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?action=%s" %
                                     context.action)
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the action query')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search?action=%s" %
                                     context.action)
    log_documents = json.loads(response.data)
    assert log_documents == context.log_documents

@given(u'a user supplies a community query')
def step_impl(context):
    context.community = "clarin"
    context.log_documents = [{u'comment': u'test comment',
                             u'timestamp': u'1456057774', u'state': u'start',
                             u'hostname': u'data.repo.cineca.it',
                             u'identifier': u'a5e4907e-1234-49f6-81ae-143d443af60e'},
                            {u'comment': u'null', u'timestamp': u'1456149606',
                             u'state': u'end',
                             u'hostname': u'data.repo.cineca.it',
                             u'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response for the community query')
def step_impl(context, text):
    response = context.flask_app.get("/policy/log/search?community=%s" %
                                     context.community)
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the community query')
def step_impl(context):
    response = context.flask_app.get("/policy/log/search?community=%s" %
                                     context.community)
    log_documents = json.loads(response.data)
    assert log_documents == context.log_documents

@given(u'a user supplies a compound query')
def step_impl(context):
    context.author = "dpmadmin"
    context.hostname = "data.repo.cineca.it"
    context.after = "2016-02-22"
    context.state = "end"
    context.log_documents = [{u'comment': u'null', u'timestamp': u'1456149606',
                              u'state': u'end',
                              u'hostname': u'data.repo.cineca.it',
                              u'identifier': u'a5e4907e-9876-49f6-81ae-143d443af60e'}]

@then(u'the user receives a "{text}" response for the compound query')
def step_impl(context, text):
    query = "/policy/log/search?author=%s&hostname=%s&after=%s&state=%s"
    response = context.flask_app.get(query % (context.author, context.hostname,
                                              context.after, context.state))
    assert response.status_code == int(text)

@then(u'the user receives a list of log documents that match the compound query')
def step_impl(context):
    query = "/policy/log/search?author=%s&hostname=%s&after=%s&state=%s"
    response = context.flask_app.get(query % (context.author, context.hostname,
                                              context.after, context.state))
    log_documents = json.loads(response.data)
    assert log_documents == context.log_documents
