# The Data Policy Manager Web interface
The DPM web interface consists of html, javascript, css and python scripts that
allow users to create and manage policies. The policies themselves are stored in
an baseX XML database (http://basex.org/). Please not the DPM has only been
tested on Linux machines - you may experience problems installing on a
Windows-based machine.

## Deploying the DPM
Most users will only be interested in deploying the DPM. The DPM makes use of a
mailserver to send emails. By default the email host is set to localhost. If
you want to change the host you need to edit the $DPMINSTALL/config/policy.cfg
script to point to your email server.

1. Download the baseX XML database server (http://basex.org) and follow the
instructions to install and run the server. NOTE: although the baseX server
is populated by the DPM direct access to the baseX database is needed for clients wishing to
query or download policies.

2. Make sure the python packages passlib  and virtualenv installed:
pip install passlib
pip install virtualenv

3. cd build/admin

4. run the script:
'''
./configure_dpm.py
'''
This will prompt you for the following paths:

* Base URI for the CGI scripts.
* Base PATH for the CGI scripts (this is the directory in which the cgi scripts live).
* Base URI for the BaseX XML database.
* Username and password for access to the BaseX database.
* Authentication method - currently EUDAT AAI is supported and a STANDALONE method.
Please note that the STANDALONE method provides no authentication or access control
and SHOULD NOT be used in production.
* The name of the administrator of the DPM.
* The username for the DPM admin. NOTE: for the AAI mode the username should be
the AAI persistent identifier for the administrator.
* The email address of the DPM admin.
* Root URI for the web pages.

You can supply the input parameters via config file using the '-c' option (see
the 'Config File Schema' section for the structure of the file). The script
will create the databases for the DPM and assemble the web pages and cgi scripts.

5. Once the script has completed you will need to copy the 'html', 'cgi'
directories under the 'deploy' directory to those that map to the corresponding
URI. NOTE: the wsgi directory does not need to be copied. This directory and its
contents will be removed from future releases.

6. Make sure that the 'data' directory for the 'cgi' directory is writeable by
the webserver to allow the web server to populate the policy database.

## Using the DPM
You can use the web interface to create a policy for replication (currently the
only supported policy on the client-side). A description of how to create a policy can be found on
the wiki: https://github.com/EUDAT-B2SAFE/B2SAFE-DPM/wiki/Quick-start:-definition-of-a-specific-data-policy


## Building the web interface
This is only required for people interested in making changes to the scripts or
pages. The DPM consists of a collection of html, javascript, css and python
scripts that need to be assembled for deployment. The assembly is done using the
grunt task manager tool. This means you need to have nodejs installed.

1. If you don't have node (http://nodejs.org/) installed then download and
   install it following the instructions on the nodejs site.

2. Install the grunt command line interface
   (http://gruntjs.com/getting-started) globally (you may need to be root to
   do this):
'''
npm install -g grunt-cli
'''
2. cd to the web directory

3. You will need to install the various grunt modules:
'''
npm install
'''

4. You should now be in a position to build the software. Run:
'''
grunt build
'''
This will run a number of tasks that effectively 'compile' the scripts
and store them in under the 'build' directory. At this point you can follow
the 'Deploying the DPM' steps to deploy the pages on your web server.

## Config File Schema
Using the '-c' option of the configure_dpm.py script you can supply the input
parameters in a config file. The structure of the file should follow:

    [DEFAULT]
    CGI_URL=<root url to the cgi scripts>
    CGI_PATH=<root path to the cgi scripts>
    XML_URL=<url to the baseX XML database>
    XML_USER=<baseX username that has admin access to the databases>
    XML_PASS=<password for the baseX user>
    ADMIN_USER=<the username or AAI persistent identifier for the admin user>
    ADMIN_NAME=<the firstname lastname of the admin user>
    ADMIN_EMAIL=<the email address of the admin user>
    AUTH_TYPE=<the authentication type: either 1 or 2 where 1=AAI, 2=STANDALONE>
    ROOT_URL=<root url to the DPM html>


Comments:
adilhasan2@gmail.com
