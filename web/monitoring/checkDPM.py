#!/usr/bin/env python

import logging
import traceback
import os, sys, io, time
import argparse
import timeout_decorator
import urllib2, urllib, socket
import json, pprint
import xml.etree.ElementTree



def check_url(url):

    rta=0
    try:
        start=time.time()
        if (urllib2.urlopen(url, timeout=1).getcode() < 501):
            msg='[OK]'
            retcode=0
        rta=time.time()-start
        
    except urllib2.URLError as e:
        msg="[URLError] %s" % e
        retcode = 2
    except socket.timeout as e:
        msg="[Socket Timeout] %s" % e
        retcode = 2
    except IOError as e:
        msg="[IOError] %s" % e
        retcode = 1
    except ValueError as e:
        msg="[ValueError] %s" % e
        retcode = 1
    except Exception as e:
        msg="[Unknown Error] %s" % e
        retcode = 3
    else:
        msg = '[OK]'
        retcode = 0

    return (retcode,msg,rta)



def check_dpm_request(dpm_req_url):
    # Checks and validates a request submitted to DPM

    userpwstat = xml.etree.ElementTree.parse('checkDPM.xml').getroot()
    username = userpwstat.find('user').text
    password = userpwstat.find('pw').text

    pwman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    pwman.add_password(None, dpm_req_url, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(pwman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)

    rta=0
    try:
        start=time.time()
	response = urllib2.urlopen(dpm_req_url)
        rta=time.time()-start
        
        assert response.code == 200
	retree = xml.etree.ElementTree.parse(response).getroot()

    except urllib2.URLError as e:
        msg = "[URLError] %s " % e
        retcode = 2
    except socket.timeout as e:
        msg = "[Socket Timeout] %s " % e
        retcode = 2
    except IOError as e:
        msg = "[IOError] %s " % e
        retcode = 1
    except ValueError as e:
        msg = "[ValueError] %s " % e
        retcode = 1
    except Exception as e:
        msg = "[Unknown Error] %s " % e
        retcode = 3
    else:
        if retree.find('status').text == userpwstat.find('status').text:
            msg = '[OK]'
            retcode = 0
        else:
	    msg = '[Status string mismatch]'
            retcode = 4

    return (retcode,msg,rta)


def main():
    B2SAFE_DPM_version='1.0'

    args = get_args()

    if args.version :
        print ('B2SAFE_DPM %s' % (B2SAFE_DPM_version))
        sys.exit(0)

    sys.exit(checkService(args))

def checkService(args):

    b2safe_dpm_url='https://'+args.hostname
    if args.port :
         b2safe_dpm_url+=':'+args.port
    print (' Check the service endpoint %s' % b2safe_dpm_url)

    print ('| %-15s | %-7s | %-25s | %-6s |' % ('Probe','RetCode','Message','RTA'))
    print ('-----------------------------------------------')

    totretcode=0

    answer=check_url(b2safe_dpm_url)
    print (' %-15s - %-7s - %-25s - %-7.2f ' % ('URLcheck',answer[0],answer[1],answer[2]))
    if answer[0] > totretcode : totretcode = answer[0]

    dpm_request=b2safe_dpm_url+'/BaseX867/rest/dbtest/test-get.xml'
    answer = check_dpm_request(dpm_request)
    print (' %-15s - %-7s - %-25s - %-7.2f ' % ('DBtest',answer[0],answer[1],answer[2]))
    if answer[0] > totretcode : totretcode = answer[0]

    return totretcode


def get_args():
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = "Description: Performs checks and returns the appropriate messages and codes."
    )
   
    p.add_argument('--version', '-v', help="prints the B2SAFE DPM version and exits", action='store_true')
    p.add_argument('--timeout', '-t', help="time out : After given number of seconds excecution terminates.", default=1000, metavar='INT')
    p.add_argument('--hostname', '-H',  help='Hostname or IP address of the B2SAFE DPM service, to which probes are submitted (default is dpm-eudat.norstore.uio.no)', default='dpm-eudat.norstore.uio.no', metavar='URL')
    p.add_argument('--port', '-p',  help='(Optional) Port of the B2SAFE DPM service, to which probes are submitted (default is None)', default=None, metavar='URL')
    
    args = p.parse_args()
    
    return args
               
if __name__ == "__main__":
    main()
