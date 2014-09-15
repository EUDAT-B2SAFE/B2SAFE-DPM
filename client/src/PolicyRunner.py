from cProfile import run
import subprocess
import sys
from crontab import CronTab
import os.path


class PolicyRunner:

    def __init__(self, test=False, debug=False):
        self.test = test
        self.debug = debug
        self.iruleCmd = '/srv/irods/iRODS-pre-production/clients/icommands/bin/irule'

    def runPolicy(self, policy):
        """
        Run a policy
        """
        if self.debug:
            print policy.toString()

        path = sys.path[0]
        for action in policy.actions:
            """
            Process all collections with the selected action(s)
            """
            for collection in policy.dataset.collections:
                for target in action.targets:
                    policyId=policy.policyId

                    rulePath = '%s/replicate.%s.r' % (path, policyId)
                    if self.test:
                        rulePath = '%s/replicate_test.%s.r' % (path, policyId)

                    if self.shouldRuleBeRun(action, rulePath):
                        self.createAndRunRule(policyId, action, collection, target, rulePath)

    def shouldRuleBeRun(self, action, rulePath):
        """
            Decide if the current rule must be run or not
            - a 'runonce' rule should only be run if the rule file does not exist yet
            - a 'periodic' rule shoule always be run
        """
        if not action.triggerType == 'runonce':
            return True
        elif not os.path.isfile(rulePath):
            return True
        else:
            print "Skipped: Reason = runonce with existing rule file [%s]" % (rulePath)
            return False

    def createAndRunRule(self, policyId, action, collection, target, rulePath):
        """
        Create a rule file and run it
        """
        delayFormat = self.generateDelayedRuleFormat(action)
        if not delayFormat is None:
            print('Generating rule: '),
            self.generateRule(rulePath, collection.value, target.location.path, target.location.resource, policyId, delayFormat)
            print('done\n'),

            """
            Using shell=True here, sanitize input or find alternative
            """
            print('Command: '),
            if not self.test:
                try:
                    output = subprocess.check_output([self.iruleCmd+' -F '+rulePath], shell=True)
                except subprocess.CalledProcessError as ex:
                    print "ret=%s" % ex.returncode
                    print "msg=%s" % ex.message

                print 'executed'
                if self.debug:
                    print 'output: [\n'+output+']'
            else:
                print 'skipped in test mode'
        else:
            print 'Skipped delay format [%s, %s]' % (action.triggerType, action.trigger)

    def generateDelayedRuleFormat(self, action):
        """
            Compute delayed rule format base on trigger type and trigger value
        """
        delay_format = None
        if action.triggerType == 'runonce':
            if action.trigger == '*':
                delay_format = '<PLUSET>1m</PLUSET>'
            else:
                delay_format = '<ET>%s</ET>' % (action.trigger.replace('T', '.')) #TODO: Check for sane input
        elif action.triggerType == 'periodic':
                cron_entry = CronTab(action.trigger)
                delay_format = '<PLUSET>%.0f%s</PLUSET>' % (cron_entry.next(), 's') #seconds until we need to run for the first time
        else:
            print 'Unkown triggertype [%s]' % (action.triggerType)
        return delay_format

    def generateRule(self, ruleFilePath, collection, path, resource, id, delay):
        f = open(ruleFilePath,'w')
        f.write('replicate {\n')
        f.write('\tlogInfo("DPM Client call to replicate.r");\n')
        f.write('\tlogInfo(*sourceNode);\n')
        f.write('\tlogInfo(*destRootCollection);\n')
        f.write('\tlogInfo(*destResource);\n')
        f.write('\tlogInfo(*policyId);\n')
        f.write('\tdelay("%s") {\n' % (delay))
        f.write('\t\treplicate(*sourceNode,*destRootCollection,*destResource, *policyId);\n')
        f.write('\twriteLine("serverLog","Generated replication for [*policyId]");\n')
        f.write('\t}\n')
        f.write('}\n')
        f.write('INPUT *sourceNode="%s",*destRootCollection="%s",*destResource="%s",*policyId="%s"\n' % (collection, path, resource, id))
        f.write('OUTPUT ruleExecOut\n')
        f.close()
