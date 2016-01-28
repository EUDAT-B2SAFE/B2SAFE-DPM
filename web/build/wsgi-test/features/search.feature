Feature: Search for policies

  Scenario: User searches for policies after a valid date
    Given a valid user submits a valid date
    Then the user receives a "200" response from the server
    Then the user receives the list of policy objects created after that date

  Scenario: Server searches for policies after a valid date
    Given a valid date
    Then the server searches the database for policy identifiers created after the date
    Then the server uses the identifiers to create the policy object for each identifier
    Then the server returns to the user the list of policy objects

  Scenario: User searches for policies before a valid date
    Given a valid user submits a valid date
    Then the user receives a "200" response from the server
    Then the user receives the list of policy objects created before this date

  Scenario: User searches for policies for a given community
    Given a valid user submits a valid community
    Then the user receives a "200" response from the server
    Then the user receives the list of policy objects belonging to the given community

  Scenario: User searches for removed policies
    Given a valid user submits a search for removed policies
    Then the user receives a "200" response from the server
    Then the user receives a list of policy objects that have been removed

  Scenario: User searches for policies by hostname
    Given a valid user submits a search for policies with a given hostname
    Then the user receives a "200" response from the server
    Then the user receives a list of policy objects matching the hostname

  Scenario: User searches for policies by action
    Given a valid user submits a search for policies with a specified action
    Then the user receives a "200" response from the server
    Then the user receives a list of policy objects matching the specified action

  Scenario: User searches for policies by identifier
    Given a valid user submits a search for policies with a given identifier
    Then the user receives a "200" response from the server
    Then the user receives the policy object with that identifier

  Scenario: User searches for policies by author
    Given a valid user submits a search for policies by a specific author
    Then the user receives a "200" response from the server
    Then the user receives a list of policy objects belonging to that author

  Scenario: User searches for policies by any of author, community, date, hostname, removed
    Given a valid user submits a search with a valid combination of query parameters
    Then the user receives a "200" response from the server
    Then the user receives a list of policy objects that match the search criteria

  Scenario: User searches for policies with invalid query parameter
    Given a valid user submits a search with an invalid query parameter
    Then the user receives a "400" response from the server
    Then the user receives a message indicating the parameters are incorrect
