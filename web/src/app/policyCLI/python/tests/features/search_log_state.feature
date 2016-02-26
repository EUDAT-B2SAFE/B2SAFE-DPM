Feature: Get the all available status for logs

Scenario: Server returns log states
Given a valid request
Then the server returns the list of states for available logs

Scenario: A valid user searches for the valid log states
Given a valid user submits a valid query
Then the user receives a "200" response
Then the user receives the list of log states
