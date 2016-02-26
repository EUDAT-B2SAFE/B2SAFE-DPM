Feature: Download a policy

  Scenario: User downloads a valid policy
    Given a valid user submits a valid policy identifier
    Then the user gets a "200" response
    Then the user receives the policy object that matches the identifier
    Then the user does not receive an empty policy object

  Scenario: Server returns a policy for a given correct policy identifier
    Given a correct policy identifier
    Then the server looks up the database index for the policy identifier
    Then the server uses the index to find the policy object
    Then the server uses the index to find the md5 for the policy
