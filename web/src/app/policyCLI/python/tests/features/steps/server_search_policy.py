import behave
import wsgi.policy

@behave.given('A valid after date')
def step_impl(context):
    '''Setup the environment for the after date search'''
    context.after = "2016-01-20T08:58:10"
    context.after_indexes = ["10"]
    context.policy_objects = [{'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                               'ctime': u'1453300290'}]

@behave.then('the server searches the database for policy identifiers created after the date')
def step_impl(context):
    '''Test the search for policy identifiers after a given date'''
    indexes = wsgi.policy.get_indexes(context.cfg, search_params={"after":context.after})
    assert indexes == context.after_indexes

@behave.then('the server uses the identifiers to create the policy object for each identifier after the given date')
def step_impl(context):
    '''Test the returned list of policies'''
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.after_indexes)
    assert policy_objects == context.policy_objects

@behave.given('A valid before date')
def step_impl(context):
    '''Setup the environment for the before date search'''
    context.before = "2016-01-20T08:58:00"
    context.before_indexes = ["1", "11", "2"]
    context.policy_objects = [{'checksum': u'1234b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-1234-49f6-81ae-143d443af60e',
                               'ctime': u'1453100000'},
                              {'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                              'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                              'ctime': u'1453200290'},
                              {'checksum': u'9876b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-9876-49f6-81ae-143d443af60e',
                               'ctime': u'1453010290'}]

@behave.then('the server searches the database for policy identifiers created before the date')
def step_impl(context):
    '''Test the search for policy identifiers before a given date'''
    indexes = wsgi.policy.get_indexes(context.cfg, search_params={"before":context.before})
    assert set(indexes) == set(context.before_indexes)

@behave.then('the server uses the identifiers to create the policy object for each identifier before the given date')
def step_impl(context):
    '''Test the returned list of policies'''
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.before_indexes)
    match = True
    for policy in policy_objects:
        if (policy not in context.policy_objects):
            match = False
            break
    assert match

@given(u'a valid community')
def step_impl(context):
    context.community = "clarin"
    context.indexes = ["1","2","10","11"]
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

@then(u'the server searches for policy identifiers created by the community')
def step_impl(context):
    indexes =wsgi.policy.get_indexes(context.cfg,
                                     search_params={"community":context.community})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the list of policy objects belonging to the community')
def step_impl(context):
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.indexes)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a removed flag')
def step_impl(context):
    context.removed = 'removed'
    context.indexes = ["3"]
    context.policy_objects = [{"checksum":"8344b9f8e41b443d2cc7bda75cb1d181",
                               "identifier":"http://example.org/getPolicy?identifier=a5e4907e-8344-49f6-81ae-143d443af60e",
                               "ctime": "1453280290"}]

@then(u'the server searches for policy identifiers with the removed flag')
def step_impl(context):
    indexes = wsgi.policy.get_indexes(context.cfg,
                                      search_params={"removed":"true"})
    assert indexes == context.indexes

@then(u'the server returns the list of policy objects with a removed flag')
def step_impl(context):
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.indexes)
    assert policy_objects == context.policy_objects

@given(u'a valid target hostname')
def step_impl(context):
    context.target_hostname = 'data.repo.cineca.it'
    context.indexes = ["1", "2", "10", "11"]
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

@then(u'the server searches for policy identifiers with the target hostname')
def step_impl(context):
    indexes = wsgi.policy.get_indexes(context.cfg,
                                      search_params={"target_hostname":context.target_hostname})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the list of policies matching the target hostname')
def step_impl(context):
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.indexes)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid action')
def step_impl(context):
    context.action = "replicate"
    context.indexes = ["1", "2", "10", "11"]
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


@then(u'the server searches for policy identifiers with the action')
def step_impl(context):
    indexes = wsgi.policy.get_indexes(context.cfg,
                                      search_params={"action":context.action})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the list of policies matching the action')
def step_impl(context):
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.indexes)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid source identifier')
def step_impl(context):
    context.source_identifier = "12312323"
    context.indexes = ["1", "2", "10", "11"]
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

@then(u'the server searches for policy identifiers with the source identifier')
def step_impl(context):
    indexes = wsgi.policy.get_indexes(context.cfg,
                                      search_params={"source_identifier":context.source_identifier})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the list of policies matching the source identifier')
def step_impl(context):
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.indexes)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid author')
def step_impl(context):
    context.indexes = ["1", "2", "10", "11"]
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

@then(u'the server searches for policy identifiers with the author')
def step_impl(context):
    indexes = wsgi.policy.get_indexes(context.cfg,
                                      search_params={"author":context.author})
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the list of policies matching the author')
def step_impl(context):
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.indexes)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match

@given(u'a valid combination of query parameters')
def step_impl(context):
    context.after = "2016-01-19T10:00:00"
    context.author = "dpmadmin"
    context.community = "clarin"
    context.indexes = ["10", "11"]
    context.policy_objects = [{'checksum': u'f8d8b9f8e41b443d2cc7bda75cb1d181',
                               'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-83a4-49f6-81ae-143d443af60e',
                               'ctime': u'1453200290'},
                              {'checksum': u'4567b9f8e41b443d2cc7bda75cb1d181',
                              'identifier': u'http://example.org/getPolicy?identifier=a5e4907e-4567-49f6-81ae-143d443af60e',
                              'ctime': u'1453300290'}]

@then(u'the server searches for policy identifiers satisfying the query parameters')
def step_impl(context):
    indexes = wsgi.policy.get_indexes(context.cfg,
                                      search_params={"after":context.after,
                                                     "community":context.community,
                                                     "author":context.author})
    print("indexes ", indexes)
    assert set(indexes) == set(context.indexes)

@then(u'the server returns the list of policies matching the query parameters')
def step_impl(context):
    policy_objects = wsgi.policy.get_policy_objects(context.cfg, context.indexes)
    match = True
    for policy in policy_objects:
        if policy not in context.policy_objects:
            match = False
            break
    assert match
