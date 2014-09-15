__author__ = 'Willem Elbers, MPI-TLA, willem.elbers@mpi.nl'

import ConfigParser

class ConfigParser():

    def __init__(self, config_file):
        self.config_file = config_file
        print "Loading configuration from [%s]" % self.config_file
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def SectionMap(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                #if dict1[option] == -1:
                #    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1