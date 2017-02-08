__author__ = 'Willem Elbers (MPI-TLA) <willem.elbers@mpi.nl> \
              Claudio Cacciari (Cineca) <c.cacciari@cineca.it>'

import logging
import logging.handlers
from cProfile import run
import subprocess
import sys
from crontab import CronTab
import os
import time
import json


class PolicyRunner:

    def __init__(self, usermap, test=False, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".PolicyRunner"
        else: loggerName = "PolicyRunner"
        self.logger = logging.getLogger(loggerName)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.usermap = usermap
        self.test = test
        self.debug = debug
        self.iruleCmd = '/usr/bin/irule'
        self.crontab  = CronTab(user=True)


    def runPolicy(self, policy):
        """
        Run a policy
        """
        self.logger.info('Start to schedule the policy: ' + policy.policyId)
        self.logger.debug(policy.toString())

        path = os.path.join(os.path.dirname(sys.path[0]), 'rules')
        if policy.author not in self.usermap.keys():
            msg = 'EUDAT account [{}] is not mapped locally'.format(
                                                             policy.author)
            self.logger.error(msg)
            return msg
        author = self.usermap[policy.author]
        policyId = policy.policyId
        a_id = 0
        for action in policy.actions:
            """
            Process all collections with the selected action(s)
            """
            a_id += 1
            c_id = 0
            if action.sources is None or len(action.sources) == 0:
                if policy.dataset is not None:
                    source_list = policy.dataset.collections
                else:
                    msg = 'missing sources'
                    self.logger.error(msg)
                    return msg
            else:
                source_list =  action.sources
            for source in source_list:
                c_id += 1
                t_id = 0
                for target in action.targets:
                    t_id += 1
                    rulePath = '%s/replicate.%s_%s_%s_%s.r' % (path, policyId, a_id, c_id, t_id)
                    if self.test:
                        rulePath = '%s/replicate_test.%s_%s_%s_%s.r' % (path, policyId, a_id, c_id, t_id)

                    if self.shouldRuleBeRun(action, rulePath):
                        jobId = policyId + '_' + str(a_id) + '_' + str(c_id) + '_' + str(t_id)
                        self.createAndRunRule(policyId, action, source, target, author, rulePath, jobId)
        return None  


    def shouldRuleBeRun(self, action, rulePath):
        """
            Decide if the current rule must be run or not
            - a 'runonce' rule should only be run if the rule file does not exist yet
            - a 'periodic' rule should always be run
        """
        if not action.triggerType == 'runonce':
            return True
        elif not os.path.isfile(rulePath):
            return True
        else:
            self.logger.info("Skipped: Reason = runonce with existing rule file "
                            + "[%s]", rulePath)
            if self.test:
                print ('[Test mode] Skipped: Reason = runonce with existing '
                      + 'rule file [{}]'.format(rulePath))
            return False


    def createAndRunRule(self, policyId, action, source, target, author, rulePath, jobId):
        """
        Create a rule file and run it
        """
        self.logger.info('Generating rule')
        self.generateRule(rulePath, source, target.location.path, target.location.resource, policyId)
        path = os.path.join(os.path.dirname(sys.path[0]), 'output')
        resultPath = path + '/response.' + jobId + '.json'

        if action.triggerType == 'runonce':
            self.logger.info('Executing the rule just one time')
            if self.test:
                print '[Test mode] Executing the rule just one time'
            result = self.executeRule(author, rulePath)
            resultJson = json.loads(result.strip().replace("'",'"'))
            with open(resultPath, 'w') as outfile:
                json.dump(resultJson, outfile)
        elif action.triggerType == 'time':
            self.logger.info('Scheduling the rule execution via system crontab')
            if self.test:
                print '[Test mode] Scheduling the execution via system crontab'
            else:
                cronJob_iter = self.crontab.find_comment(jobId)
                if sum(1 for _ in cronJob_iter) == 0:
                    cmd = ('export clientUserName=' + author + '; '
                          + self.iruleCmd + ' -F ' + rulePath + ' > ' 
                          + resultPath)
                    cronJob = self.crontab.new(command=cmd, comment=jobId)
                    self.logger.debug('time trigger: ' + action.trigger)
                    cronJob.setall((action.trigger).split())
                    cronJob.enable()
                    self.crontab.write_to_user(user=True)
                else:
                    self.logger.info('Skipping rule execution, policy already '
                                   + 'scheduled [id=%s]', policyId)
        else:
            self.logger.error('Unkown trigger type [%s]', action.triggerType)
            if self.test:
                print 'ERROR: unkown trigger type [{}]'.format(
                                                        action.triggerType)


    def executeRule(self, author, rulePath):
        """
            Create the shell command to be executed
            Using shell=True here, sanitize input or find alternative
        """
        self.logger.info('Executing command: '+self.iruleCmd+' -F '+rulePath)
        if not self.test:
            d = dict(os.environ)
            d['clientUserName'] = author
            proc = subprocess.Popen([self.iruleCmd+' -F '+rulePath], env=d,
                                    stdout=subprocess.PIPE, shell=True)
            output, err = proc.communicate()
            rc = proc.poll()
            if rc:
                self.logger.debug("ret=%s", rc)
                self.logger.debug("msg=%s", output)
                self.logger.info('Command executed')
        else:
            print ('[Test mode] executing command: ' + self.iruleCmd + ' -F ' 
                  + rulePath)
            output = ("{'policyId':'', 'result':'', "
                                    + "'response':'Skipped in test mode'}")
            self.logger.info('Skipped in test mode')

        return output


    def generateRule(self, ruleFilePath, source, path, resource, id):

        f = open(ruleFilePath,'w')
        f.write('replicate {\n')
        f.write('\tlogInfo("DPM Client replicate rule");\n')

        if source.type == 'eudat pid' or source.type == 'pid':
            f.write('\t*pidValue = "{}";\n'.format(source.value))
            # expected a sourceNode of type 
            # irods://130.186.13.115:1247/cinecaDMPZone2/home/claudio/coll_C
            f.write('\tEUDATeURLsearch(*pidValue, *url);\n')
            f.write('\tmsiSubstr("*url", "8", "-1", *remaining);\n')
            f.write('\t*pathList = split(*remaining, "/");\n')
            f.write('\t*sourcePathList = tl(*pathList);\n')
            f.write('\t*sourceNode = "";\n')
            f.write('\tforeach(*sourcePathList) {\n')
            f.write('\t\t*sourceNode = *sourceNode ++ "/" ++ *sourcePathList;\n')
            f.write('\t}\n')

        f.write('\tlogInfo(*sourceNode);\n')
        f.write('\tlogInfo(*destRootCollection);\n')
        f.write('\tlogInfo(*destResource);\n')
        f.write('\tlogInfo(*policyId);\n')
        f.write('\t*recursive = "true";\n')
        f.write('\t*registered = "true";\n')
        f.write('\t*result = EUDATReplication(*sourceNode, *destRootCollection,'
              + '*registered, *recursive, *response);\n')
        f.write('\twriteLine("serverLog","Generated replication for policy '
              + '[*policyId]");\n')
        outputMsg = "{'policyId':'*policyId', 'result':'*result', 'response':'*response'}"
        f.write('\twriteLine("stdout", "' + outputMsg + '");\n')
        f.write('}\n')

        outString = 'INPUT *sourceNode="%s",*destRootCollection="%s",*destResource="%s",*policyId="%s"\n'
        if source.type == 'eudat pid' or source.type == 'pid':
            outString = 'INPUT *destRootCollection="%s",*destResource="%s",*policyId="%s"\n'
            f.write(outString % (path, resource, id))
        else:
            outString = 'INPUT *sourceNode="%s",*destRootCollection="%s",*destResource="%s",*policyId="%s"\n'
            f.write(outString % (source.value, path, resource, id))
        f.write('OUTPUT ruleExecOut\n')
        f.close()
