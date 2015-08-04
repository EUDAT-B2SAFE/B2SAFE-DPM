__author__ = 'Willem Elbers, MPI-TLA, willem.elbers@mpi.nl'

from cProfile import run
import subprocess
import sys
from crontab import CronTab
import os
import time


class PolicyRunner:


    def __init__(self, test=False, debug=False):
        self.test = test
        self.debug = debug
        self.iruleCmd = '/usr/bin/irule'
        self.crontab  = CronTab(user=True)
        

    def runPolicy(self, policy):
        """
        Run a policy
        """
        if self.debug:
            print policy.toString()

        path = sys.path[0]
        author = policy.author
        policyId = policy.policyId
        a_id = 0
        for action in policy.actions:
            """
            Process all collections with the selected action(s)
            """
            a_id += 1
            c_id = 0 
            for collection in policy.dataset.collections:
                c_id += 1 
                t_id = 0
                for target in action.targets:
                    t_id += 1 
                    rulePath = '%s/replicate.%s_%s_%s_%s.r' % (path, policyId, a_id, c_id, t_id)
                    if self.test:
                        rulePath = '%s/replicate_test.%s_%s_%s_%s.r' % (path, policyId, a_id, c_id, t_id)

                    if self.shouldRuleBeRun(action, rulePath):
                        jobId = policyId + '_' + str(a_id) + str(c_id) + str(t_id)
                        self.createAndRunRule(policyId, action, collection, target, author, rulePath, jobId)


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
            print "Skipped: Reason = runonce with existing rule file [%s]" % (rulePath)
            return False


    def createAndRunRule(self, policyId, action, collection, target, author, rulePath, jobId):
        """
        Create a rule file and run it
        """     
        print('Generating rule: '),
        self.generateRule(rulePath, collection.value, target.location.path, target.location.resource, policyId)
        print('done\n'),

        if action.triggerType == 'runonce':
            print 'Executing the rule just one time'
            self.executeRule(author, rulePath)
        elif action.triggerType == 'time':
            print 'Scheduling the rule execution via system crontab'
            cronJob_iter = self.crontab.find_comment(jobId)
            if sum(1 for _ in cronJob_iter) == 0:
                cmd = 'export clientUserName=' + author + '; ' + self.iruleCmd + ' -F ' + rulePath
                cronJob = self.crontab.new(command=cmd, comment=jobId)
                cronJob.setall((action.trigger).split())
                cronJob.enable()
                self.crontab.write_to_user(user=True)
            else:
                print 'Skipping rule execution, policy already scheduled [id=%s]' % (policyId)
        else:
            print 'Unkown trigger type [%s]' % (action.triggerType)


    def executeRule(self, author, rulePath):
        """
            Create the shell command to be executed
            Using shell=True here, sanitize input or find alternative
        """
        print('Command: '),
        if not self.test:
            d = dict(os.environ)
            d['clientUserName'] = author
            proc = subprocess.Popen([self.iruleCmd+' -F'+rulePath], env=d, stdout=subprocess.PIPE, shell=True)
            output, err = proc.communicate()
            rc = proc.poll()
            if rc:
                print "ret=%s" % rc
                print "msg=%s" % output
                print 'executed'
                if self.debug:
                    print 'output: [\n'+output+']'
            else:
                print 'skipped in test mode'      
        

    def generateRule(self, ruleFilePath, collection, path, resource, id):
        f = open(ruleFilePath,'w')
        f.write('replicate {\n')
        f.write('\tlogInfo("DPM Client call to replicate.r");\n')
        f.write('\tlogInfo(*sourceNode);\n')
        f.write('\tlogInfo(*destRootCollection);\n')
        f.write('\tlogInfo(*destResource);\n')
        f.write('\tlogInfo(*policyId);\n')
        f.write('\t*recursive = bool("true");\n')
        f.write('\t*registered = bool("true");\n')
        f.write('\tEUDATReplication(*sourceNode, *destRootCollection, *registered, *recursive, *response);\n')
        f.write('\twriteLine("serverLog","Generated replication for [*policyId]");\n')
        f.write('}\n')
        f.write('INPUT *sourceNode="%s",*destRootCollection="%s",*destResource="%s",*policyId="%s"\n' % (collection, path, resource, id))
        f.write('OUTPUT ruleExecOut\n')
        f.close()
