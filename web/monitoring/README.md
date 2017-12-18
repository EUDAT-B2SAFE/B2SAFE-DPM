# Montoring for the Data Policy Manager
The script in this directory is a probe for monitoring the Data Policy Manager Service. The
probe checks the database and web server are accessible. 

The script requires the timeout_decorator package to be installed.

To run the script:

./checkDPM.py -p port -H host

where 'port' is the port the DPM service is running on and 'host' is the hostname of
the service. The probe assumes the DPM web server and database are running on the same
host.
