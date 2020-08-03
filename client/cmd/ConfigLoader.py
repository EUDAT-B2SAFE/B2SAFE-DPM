__author__ = 'Willem Elbers (MPI-TLA) <willem.elbers@mpi.nl> \
              Claudio Cacciari (Cineca) <c.cacciari@cineca.it>'

import configparser

class ConfigLoader():

    def __init__(self, config_file):

        self.config_file = config_file
        self.config = configparser.configparser()
        self.config.read(self.config_file)

    def SectionMap(self, section):

        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
            except:
                dict1[option] = None
        return dict1
