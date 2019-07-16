#!/usr/bin/env python

__author__ = 'Adil Hasan (Sigma2) <adilhasan2@gmail.com'

import argparse
import os
import sys
import irods.session
import irods.rule

def run(rulePath, author):
   """
       Execute the iRODS rule
   """
   try:
       env_file = os.environ["IRODS_ENVIRONMENT_FILE"]
   except KeyError:
       env_file = os.path.expanduser("~/.irods/irods_environment.json")

   with irods.session.iRODSSession(irods_env_file=env_file,
                                   client_user=author) as session:
       rule = irods.rule.Rule(session, rulePath)
       output = rule.execute()

   outStr = ""
   if output.MsParam_PI[0].inOutStruct.status == 0:
     buf = output.MsParam_PI[0].inOutStruct.stdoutBuf.buf
     if buf:
       outStr = buf.split("\n")[0]
   else:
     buf = output.MsParam_PI[0].inOutStruct.stderrBuf.buf
     if buf:
       outStr = buf.split("\n")[0]

   return(output.MsParam_PI[0].inOutStruct.status, outStr)


if __name__ == '__main__':
   argp = argparse.ArgumentParser(description="iRODS rule runner")
   argp.add_argument("rule", help="Path to rule file")
   argp.add_argument("owner", help="The owner of the iRODS data")
   args = argp.parse_args()

   status, output = run(rulePath=args.rule, author=args.owner)
   print("Return Status: %d " % status)
   print("Output (if any): " + output)


