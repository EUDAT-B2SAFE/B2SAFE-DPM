# Data Policy Manager DB #

The XML DB stores the policies defined through the web UI or uploaded through the DB HTTP REST API.
The scripts in the current folder are intended to be executed by the DB administrator user.
Their purpose is the synchroniztion of the policies states among the three kinds of BaseX databases.

## Deployment ##

Just copy the python scripts in a suitable path.

## Configuration ##

Look at the file `conf/config.ini` and fill the missing information.

## Usage ##

In order to create new status document when a new policy is stored in a DB, run:
```$ ./DBCommander.py -c conf/config.ini add```

It searches through all the DBs explicitly listed in the configuration parameter `policiesdbname` or starting with the prefix `policies_prefix`.
Then it creates a new status doc in the related DBs, whose name is composed by the prefix `status_prefix` concatenated with the community name derived by the suffix of the policy DB's name.
For example if the policy POL_Y is stored in the DB POLICIES_COMMUNITY_A, the script will create a new document called POL_Y_status.xml in a DB named STATUS_COMMUNITY_A, where the community name is `A`.

In order to update the status of a policy considering its execution at each site, run:
```$ ./DBCommander.py -c conf/config.ini update```

It searches through all the DBs starting with the prefix `status_site_prefix` using the policy id to collect the status of the executions per site.
Then it add the list of states in the policy status document, like POL_Y_status.xml according to our example.
