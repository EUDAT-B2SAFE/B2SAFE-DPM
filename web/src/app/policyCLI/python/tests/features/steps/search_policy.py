import json
import behave
import wsgi.policy

@given(u'a valid user submits a valid after date')
def step_impl(context):
    context.after = "2016-01-20T08:58:10"
    context.policy_objects = [{'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               'ctime': u'1453300290'}]

@then(u'the user receives a "{text}" response from the server for the after date query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?after=%s" % context.after)
    assert response.status_code == int(text)

@then(u'the user receives the list of policy objects created after that date')
def step_impl(context):
    response = context.flask_app.get("search/policy?after=%s" % context.after)
    policy_objects = json.loads(response.data)
    assert policy_objects == context.policy_objects

@given(u'a valid user submits a valid before date')
def step_impl(context):
    context.before = "2016-01-20T08:58:00"
    context.policy_objects = [{'checksum': u'1234b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-1234-49f6-81ae-143d443af60e',
                               'ctime': u'1453100000'},
                              {'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                              'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                              'ctime': u'1453200290'},
                              {'checksum': u'9876b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-9876-49f6-81ae-143d443af60e',
                               'ctime': u'1453010290'}]

@then(u'the user receives a "{text}" response from the server for the before date query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?before=%s" % context.before)
    assert response.status_code == int(text)

@then(u'the user receives the list of policy objects created before this date')
def step_impl(context):
    response = context.flask_app.get("search/policy?before=%s" % context.before)
    policy_objects = json.loads(response.data)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid user submits a valid community')
def step_impl(context):
    context.community = "clarin"
    context.policy_objects = [{u'checksum': u'1234b9f8e41b443d2cc7bda75cb1d181',
                               u'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-1234-49f6-81ae-143d443af60e',
                               u'ctime': u'1453100000'},
                              {u'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               u'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               u'ctime': u'1453300290'},
                              {u'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                               u'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                               u'ctime': u'1453200290'},
                              {u'checksum': u'9876b9f8e41b443d2cc7bda75cb1d181',
                               u'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-9876-49f6-81ae-143d443af60e',
                               u'ctime': u'1453010290'}]

@then(u'the user receives a "{text}" response from the server for the community query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?community=%s" % context.community)
    assert response.status_code == int(text)

@then(u'the user receives the list of policy objects belonging to the given community')
def step_impl(context):
    response = context.flask_app.get("search/policy?community=%s" % context.community)
    policy_objects = json.loads(response.data)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid user submits a search for removed policies')
def step_impl(context):
    context.removed = 'true'
    context.policy_objects = [{"checksum":"8344b9f8e41b443d2cc7bda75cb1d181",
                               "identifier":"http://example.org/getPolicy?identifier=a5e4907e-8344-49f6-81ae-143d443af60e",
                               "ctime": "1453280290"}]

@then(u'the user receives a "{text}" response from the server for the removed query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?community=%s" % context.removed)
    assert response.status_code == int(text)

@then(u'the user receives a list of policy objects that have been removed')
def step_impl(context):
    response = context.flask_app.get("search/policy?removed=%s" % context.removed)
    policy_objects = json.loads(response.data)
    assert policy_objects == context.policy_objects

@given(u'a valid user submits a search for policies with a given target hostname')
def step_impl(context):
    context.target_hostname = 'data.repo.cineca.it'
    context.policy_objects = [{'checksum': u'1234b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-1234-49f6-81ae-143d443af60e',
                               'ctime': u'1453100000'},
                              {'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               'ctime': u'1453300290'},
                              {'checksum': u'9876b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-9876-49f6-81ae-143d443af60e',
                               'ctime': u'1453010290'},
                              {'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                               'ctime': u'1453200290'}]

@then(u'the user receives a "{text}" response from the server for the target hostname query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?target_hostname=%s" % context.target_hostname)
    assert response.status_code == int(text)

@then(u'the user receives a list of policy objects matching the target hostname')
def step_impl(context):
    response = context.flask_app.get("search/policy?target_hostname=%s" % context.target_hostname)
    policy_objects = json.loads(response.data)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid user submits a search for policies with a specified action')
def step_impl(context):
    context.action = "replicate"
    context.policy_objects = [{'checksum': u'1234b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-1234-49f6-81ae-143d443af60e',
                               'ctime': u'1453100000'},
                              {'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               'ctime': u'1453300290'},
                              {'checksum': u'9876b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-9876-49f6-81ae-143d443af60e',
                               'ctime': u'1453010290'},
                              {'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                               'ctime': u'1453200290'}]

@then(u'the user receives a "{text}" response from the server for the action query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?action=%s" % context.action)
    assert response.status_code == int(text)

@then(u'the user receives a list of policy objects matching the specified action')
def step_impl(context):
    response = context.flask_app.get("search/policy?action=%s" % context.action)
    policy_objects = json.loads(response.data)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid user submits a search for policies with a given source identifier')
def step_impl(context):
    context.source_identifier = "12312323"
    context.policy_objects = [{'checksum': u'1234b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-1234-49f6-81ae-143d443af60e',
                               'ctime': u'1453100000'},
                              {'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               'ctime': u'1453300290'},
                              {'checksum': u'9876b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-9876-49f6-81ae-143d443af60e',
                               'ctime': u'1453010290'},
                              {'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                               'ctime': u'1453200290'}]

@then(u'the user receives a "{text}" response from the server for the source identifier query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?source_identifier=%s" % context.source_identifier)
    assert response.status_code == int(text)

@then(u'the user receives the policy object with that source identifier')
def step_impl(context):
    response = context.flask_app.get("search/policy?source_identifier=%s" % context.source_identifier)
    policy_objects = json.loads(response.data)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid user submits a search with a valid combination of query parameters')
def step_impl(context):
    context.after = "2016-01-19T10:00:00"
    context.author = "dpmadmin"
    context.community = "clarin"
    context.policy_objects = [{'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                               'ctime': u'1453200290'},
                              {'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               'ctime': u'1453300290'}]


@then(u'the user receives a "{text}" response from the server for the combination of query parameters')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?after=%s&author=%s&community=%s" %\
                                     (context.after, context.author, context.community))
    assert response.status_code == int(text)

@then(u'the user receives a list of policy objects that match the search criteria')
def step_impl(context):
    response = context.flask_app.get("search/policy?after=%s&author=%s&community=%s" %\
                                     (context.after, context.author, context.community))
    policy_objects = json.loads(response.data)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid user submits a search with an invalid query parameter')
def step_impl(context):
    context.query = "test"
    context.result = "Unrecognised request"

@then(u'the user receives a "{text}" response from the server')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?dummy=%s" % context.query)
    assert response.status_code == int(text)

@then(u'the user receives a message indicating the parameters are incorrect')
def step_impl(context):
    response = context.flask_app.get("search/policy?dummy=%s" % context.query)
    assert response.data == context.result

@given(u'a valid user submits a search for policies by a specific author')
def step_impl(context):
    context.author = "dpmadmin"
    context.policy_objects = [{'checksum': u'1234b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-1234-49f6-81ae-143d443af60e',
                               'ctime': u'1453100000'},
                              {'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               'ctime': u'1453300290'},
                              {'checksum': u'9876b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-9876-49f6-81ae-143d443af60e',
                               'ctime': u'1453010290'},
                              {'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                               'ctime': u'1453200290'}]

@then(u'the user receives a "{text}" response from the server for the author query')
def step_impl(context, text):
    response = context.flask_app.get("search/policy?author=%s" % context.author)
    assert response.status_code == int(text)

@then(u'the user receives a list of policy objects belonging to that author')
def step_impl(context):
    response = context.flask_app.get("search/policy?author=%s" % context.author)
    policy_objects = json.loads(response.data)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match
