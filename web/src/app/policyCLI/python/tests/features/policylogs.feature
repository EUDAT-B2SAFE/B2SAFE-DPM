Feature: Load log for policy execution

Scenario: Server loads log information into the store
Given valid log information
Then the server checks if the log information conforms to the schema
Then the server loads the information into the database

Scenario: User uploads log information to the store
Given a valid user uploads log information
Then the user receives a "400" message if the log does not conform to the schema
Then the user receives a "201" message and the result of the log upload
