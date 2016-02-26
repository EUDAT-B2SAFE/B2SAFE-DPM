Feature: Search for log documents

Scenario: Server returns log documents after a given date
Given an after date
Then the server reports an error if the after date is invalid
Then the server searches for the indexes for the log documents matching the after date
Then the server returns the list of log documents matching the after date

Scenario: Server returns log documents before a given date
Given a before date
Then the server reports an error if the before date is invalid
Then the server searches for the indexes for the log documents matching the before date
Then the server returns the list of log documents matching the before date

Scenario: Server returns log documents for a given state
Given a state
Then the server searches for the indexes for the log documents matching the state
Then the server returns the log documents matching the state

Scenario: Server returns log documents for a given hostname
Given a hostname
Then the server searches for the indexes for the log documents matching the hostname
Then the server returns the log documents matching the hostname

Scenario: Server returns log documents for a given identifier
Given an identifier
Then the server searches for the indexes for the log documents matching the identifier
Then the server returns the log documents matching the identifier

Scenario: Server returns log documents for a given community
Given a community
Then the server searches for the indexes for the log documents matching the community
Then the server returns the log documents matching the community

Scenario: Server returns log documents for a given action
Given an action
Then the server searches for the indexes for the log documents matching the action
Then the server returns the log documents matching the action

Scenario: Server returns log documents for a given date range, state, hostname1, hostname2
Given a compound query
Then the server searches for the indexes for the log documents matching the compound query
Then the server returns the log documents matching the compound query

Scenario: User requests log documents after a given date
Given a user supplies an after date query
Then the user receives a "400" response if the after date is invalid
Then the user receives a "200" response if the after date is valid
Then the user receives a list of log documents that match the after date

Scenario: User requests log documents before a given date
Given a user supplies an before date query
Then the user receives a "200" response if the before date is valid
Then the user receives a list of log documents that match the before date

Scenario: User requests log documents for a given state
Given a user supplies a state query
Then the user receives a "200" response for the state query
Then the user receives a list of log documents that match the state query

Scenario: User requests log documents for a given hostname
Given a user supplies a hostname query
Then the user receives a "200" response for the hostname query
Then the user receives a list of log documents that match the hostname query

Scenario: User requests log documents for a given identifier
Given a user supplies a identifier query
Then the user receives a "200" response for the identifier query
Then the user receives a list of log documents that match the identifier query

Scenario: User requests log documents for a given action
Given a user supplies a action query
Then the user receives a "200" response for the action query
Then the user receives a list of log documents that match the action query

Scenario: User requests log documents for a given community
Given a user supplies a community query
Then the user receives a "200" response for the community query
Then the user receives a list of log documents that match the community query

Scenario: User requests log documents for a given date range, state, hostname1, hostname2
Given a user supplies a compound query
Then the user receives a "200" response for the compound query
Then the user receives a list of log documents that match the compound query
