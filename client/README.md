# Data Policy Manager agent #

The Data Policy Manager allows to define, store, monitor policies.
A DPM policy is a set of actions applied to a set of data and triggered at a certain point in time.
A DPM agent is a client to list and retrieve DPM policies, translate them into B2SAFE operations, schedule them and provide back the status of their enforcement. It is implemented through a collection of python scripts.

Currently there is one main script: the *PolicyManager.py* python script.

## Deployment ##

1. clone the b2safe project as any user, NOT root.  
```$ git clone https://github.com/EUDAT-B2SAFE/B2SAFE-DPM.git```  
2. go to the directory where the packaging files are:  
```$ cd B2SAFE-DPM/client/packaging```  

#### RPM ####

3. create package:  
```$ ./create_rpm_package.sh```  
4. login as root and install package:
```
  $ rpm -ivh /home/irods/rpmbuild/RPMS/noarch/irods-eudat-b2safe-dpm-client_1.0-0.noarch.rpm  
  Preparing...                        ########################################### [100%]  
  1:irods-eudat-b2safe-dpm-client     ########################################### [100%]  
```  

#### DEB ####

3. create package:  
```$ ./create_deb_package.sh```  
4. login as root or use sudo to install package:  
```
  $ sudo dpkg -i  /home/irods/debbuild/irods-eudat-b2safe-dpm-client_1.0-0.deb
  Selecting previously unselected package irods-eudat-b2safe-dpm-client.  
  (Reading database ... .... files and directories currently installed.)  
  Preparing to unpack .../irods-eudat-b2safe-dpm-client_1.0-0.deb ...  
  Unpacking irods-eudat-b2safe-dpm-client (1.0-0) ...  
  Setting up irods-eudat-b2safe-dpm-client (1.0-0) ...  
```  

The package DPM client has been installed in /opt/eudat/b2safe-dpm-client.

## Configuration ##

The DPM agent can be scheduled periodically relying on the local unix crontab or controlled via iRODS, by using the msiExecCmd iRODS command. 
The typical install path is a subdirectory under the `/opt/eudat/b2safe-dpm-client` and linked in the `iRODS/service/bin/cmd` directory to point to the scripts.

Such a organization would look something like this:
```
 iRODS/server/bin/cmd/runPolicyManager.py -> /opt/eudat/b2safe-dpm-client/cmd/PolicyManager.py 
   
 /opt/eudat/b2safe-dpm-client/cmd
 /opt/eudat/b2safe-dpm-client/conf
 /opt/eudat/b2safe-dpm-client/output
 /opt/eudat/b2safe-dpm-client/rules
 /opt/eudat/b2safe-dpm-client/test

 /var/log/irods
```

Inside the `/opt/eudat/b2safe-dpm-client/conf` directory are three files:  
1) `config.ini`: this file holds center specific properties and should be configured for each center.  
2) `usermap.json`: this file contains the map between the global (EUDAT wide) identity of the user and the local identity on
the center's B2SAFE instance.  
3) `credentials.json`: this file contains the user name and password to connect to the policy DB.  

## PolicyManager.py ##

### Using the script ###

to get help on how to use the script run `./PolicyManager.py -h`:
```
usage: PolicyManager.py [-h] -T {periodic,hook,cli} [-t] [-v] -c CONFIG
                        {http,file,clean,update} ...

EUDAT Data Policy Manager (DPM) client

positional arguments:
  {http,file,clean,update}
                        sub-command help
    http                Fetch policy over http
    file                Fetch policy from a file
    clean               Clean the expired policies from crontab
    update              Update policy status in the central DB

optional arguments:
  -h, --help            show this help message and exit
  -T {periodic,hook,cli}, --type {periodic,hook,cli}
                        Specify if this invokation is triggered periodic or
                        via an irods hook
  -t, --test            Test the DPM client (does not trigger an actual
                        replication)
  -v, --verbose         Run the DPM client in verbose mode
  -c CONFIG, --config CONFIG
                        Path to config.ini
```
Required parameters:

the -T parameter is used to specify what is invoking the script. Is it an iRODS
system hook, is it a periodic invocation running at set intervals or if it is 
started from the command line.

The script has two modes to operate, (1) the http mode and (2) the file mode. 
The http mode requires the URL of the policy DB in the configuration file. 
The file mode requires you to supply the path to the policy xml file which is stored locally.

Optional parameters:

Supply the -v parameter to run the script in verbose mode. This will display all
kinds of information on what the scrip is doing.

Supply the -t mode to run the script in test mode. In test mode it will fetch and
parse the policy file and print to command it would execute to stdout. The actual
iRODS policy is not started. 

### Examples ###

`./PolicyManager.py -t -v -T cli -c /opt/eudat/b2safe-dpm-client/conf/config.ini http`

`./PolicyManager.py -t -v -T cli file -p ./policy_test.xml`

### Data send to the DPM server ###

The `update` positional command tells to the PolicyManager to check if the expected list of policies is accepted from the local sites, already enforced or never scheduled. Then the status of each policy is updated in the central DPM DB.
Data uploads have the following format and will be send as application/xml document:
```
<?xml version="1.0" encoding="UTF-8"?>
<tns:policy xmlns:tns="http://eudat.eu/2016/policy-status" uniqueid="5439064f-0d3e-4971-8cfe-5bde89d10f8b">
    <tns:name>Cineca_first</tns:name>
    <tns:version>1.0</tns:version>
    <tns:checksum method="MD5">93ed6021618e1f451d2307244fdd4db0</tns:checksum>
    <tns:status>DONE</tns:status>
    <tns:timestamp>2016-08-21T09:30:10Z</tns:timestamp>
</tns:policy>
```
It is also possible to update a specific policy with the parameter -i .
