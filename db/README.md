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
Before the update:  
```
<ns0:policy xmlns:ns0="http://eudat.eu/2016/policy-status" uniqueid="245d8fe3-23fa-47b7-bd99-cdc34b8d2c22">
  <ns0:name>MCP</ns0:name>
  <ns0:version>1.0</ns0:version>
  <ns0:checksum method="MD5">7dcc6ede40b6322b67a4fa0ad893cbf0</ns0:checksum>
  <ns0:status>
    <ns0:overall>NEW</ns0:overall>
  </ns0:status>
  <ns0:timestamp>2017-02-06T10:26:17Z</ns0:timestamp>
</ns0:policy>
```  
After:
```
<ns0:policy xmlns:ns0="http://eudat.eu/2016/policy-status" uniqueid="245d8fe3-23fa-47b7-bd99-cdc34b8d2c22">
  <ns0:name>MCP</ns0:name>
  <ns0:version>1.0</ns0:version>
  <ns0:checksum method="MD5">7dcc6ede40b6322b67a4fa0ad893cbf0</ns0:checksum>
  <ns0:status>
    <ns0:overall>QUEUED</ns0:overall>
    <ns0:details>
      <ns0:site name="status_site_1">QUEUED</ns0:site>
      <ns0:site name="status_site_2">QUEUED</ns0:site>
    </ns0:details>
  </ns0:status>
  <ns0:timestamp>2017-02-08T16:42:33Z</ns0:timestamp>
</ns0:policy>
```


