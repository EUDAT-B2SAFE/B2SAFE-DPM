Feature: Search for policies

  Scenario: User searches for policies after a valid date
    Given a valid user submits a valid after date
    Then the user receives a "200" response from the server for the after date query
    Then the user receives the list of policy objects created after that date

  Scenario: Server searches for policies after a valid date
    Given a valid after date
    Then the server searches the database for policy identifiers created after the date
    Then the server uses the identifiers to create the policy object for each identifier after the given date

  Scenario: User searches for policies before a valid date
    Given a valid before date
    Then the user receives a "200" response from the server for the before date query
    Then the user receives the list of policy objects created before this date

  Scenario: Server searches for policies before a valid date
    Given a valid before date
    Then the server searches the database for policy identifiers created before the date
    Then the server uses the identifiers to create the policy object for each identifier before the given date

  Scenario: User searches for policies for a given community
    Given a valid user submits a valid community
    Then the user receives a "200" response from the server for the community query
    Then the user receives the list of policy objects belonging to the given community

  Scenario: Server searches for policies for a given community
    Given a valid community
    Then the server searches for policy identifiers created by the community
    Then the server returns the list of policy objects belonging to the community

  Scenario: User searches for removed policies
    Given a valid user submits a search for removed policies
    Then the user receives a "200" response from the server for the removed query
    Then the user receives a list of policy objects that have been removed

    Scenario: Server searches for removed policies
      Given a removed flag
      Then the server searches for policy identifiers with the removed flag
      Then the server returns the list of policy objects with a removed flag

  Scenario: User searches for policies by target hostname
    Given a valid user submits a search for policies with a given target hostname
    Then the user receives a "200" response from the server for the target hostname query
    Then the user receives a list of policy objects matching the target hostname

    Scenario: Server searches for policies by target hostname
      Given a valid target hostname
      Then the server searches for policy identifiers with the target hostname
      Then the server returns the list of policies matching the target hostname

  Scenario: User searches for policies by action
    Given a valid user submits a search for policies with a specified action
    Then the user receives a "200" response from the server for the action query
    Then the user receives a list of policy objects matching the specified action

    Scenario: Server searches for policies by action
      Given a valid action
      Then the server searches for policy identifiers with the action
      Then the server returns the list of policies matching the action

  Scenario: User searches for policies by source identifier
    Given a valid user submits a search for policies with a given source identifier
    Then the user receives a "200" response from the server for the source identifier query
    Then the user receives the policy object with that source identifier

    Scenario: Server searches for policies by source identifier
      Given a valid source identifier
      Then the server searches for policy identifiers with the source identifier
      Then the server returns the list of policies matching the source identifier

  Scenario: User searches for policies by author
    Given a valid user submits a search for policies by a specific author
    Then the user receives a "200" response from the server for the author query
    Then the user receives a list of policy objects belonging to that author

    Scenario: Server searches for policies by author
      Given a valid author
      Then the server searches for policy identifiers with the author
      Then the server returns the list of policies matching the author

  Scenario: User searches for policies by author, community, before date, hostname
    Given a valid user submits a search with a valid combination of query parameters
    Then the user receives a "200" response from the server for the combination of query parameters
    Then the user receives a list of policy objects that match the search criteria

    Scenario: Server searches for policies by author, community, before date, hostname
      Given a valid combination of query parameters
      Then the server searches for policy identifiers satisfying the query parameters
      Then the server returns the list of policies matching the query parameters

  Scenario: User searches for policies with invalid query parameter
    Given a valid user submits a search with an invalid query parameter
    Then the user receives a "400" response from the server
    Then the user receives a message indicating the parameters are incorrect
