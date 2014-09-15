__author__ = 'Willem Elbers, MPI-TLA, willem.elbers@mpi.nl'

from lxml import etree
from Policy import Policy

class ReplicationPolicy(Policy):
    def __init__(self, element, ns):
        Policy.__init__(self, element, ns);
        self.dataset = None
        self.actions = []

    def toString(self):
        str = 'Policy:'
        str += Policy.toString(self);
        str += self.dataset.toString('\t')
        str += '\tActions:\n'
        for action in self.actions:
            str += action.toString('\t\t')
        return str

    def parse(self):
        Policy.parse(self)
        self.parseDataSets(self.root.findall(self.ns+'dataset'))
        self.parseActions(self.root.findall(self.ns+'actions'))

    def parseDataSets(self, datasets):
        if datasets == None:
            print('No datasets found')
        else:
            for dataset in datasets:
                self.dataset = Dataset(dataset, self.ns)

    def parseActions(self, actions):
        if actions == None:
            print('No actions found')
        elif not len(actions) == 1:
            print('Expected one <actions> element instead of '+str(len(actions)))
        else:
            for action in actions[0].findall(self.ns+'action'):
                self.actions.append(Action(action, self.ns))

class Dataset():
    """
        <dataset>
            <collection id="0">
                <persistentIdentifier type="PID"> 11100/6c8ac19e-c982-11e2-b3cb-e41f13eb41b2</persistentIdentifier>
            </collection>
            ...
        </dataset>
    """
    def __init__(self, element, ns):
        self.collections = []
        for collectionElement in element.findall(ns+'collection'):
            self.collections.append(Collection(collectionElement, ns))

    def toString(self, prefix=''):
        str = '%sCollections:\n' % (prefix)
        for collection in self.collections:
            str += '%s\t%s\n' % (prefix, collection.toString())
        return str

class Collection():
    """
    Class defining all collection properties
    """
    def __init__(self, element, ns):
        self.id = element.get('id').strip()
        #process persistent identifier
        pid = element.findall(ns+'persistentIdentifier')
        if pid:
            self.type = pid[0].get('type').strip()
            self.value = pid[0].text.strip()
        #process location
        location = element.findall(ns+'location')
        if location:
            loc = location[0].text.strip()

    def toString(self):
        str = '%s [%s] %s' % (self.type, self.id,self.value)
        return str

class Action():
    """
    Class parsing and defining all action properties

    <action name="replication onchange">
      <type>replication</type>
      <trigger type="action">onchange</trigger>
      <sources>
        <source>...</source>
        ...
        <source>...</source>
      </sources>
      <targets>
        <target>...</target>
        ...
        <target>...</target>
      </targets>
    </action>
    """
    def __init__(self, element, ns):
        self.targets = []
        self.sources = []

        self.name = element.get('name').strip()
        self.type = element.findall(ns+'type')[0].text.strip()
        self.trigger = element.findall(ns+'trigger')[0].text.strip()
        if not element.findall(ns+'trigger')[0].get('type') == None:
            self.triggerType = element.findall(ns+'trigger')[0].get('type').strip()
        else:
            self.triggerType = 'runonce'

        #Process sources
        for source in element.findall(ns+'sources/'+ns+'source'):
            self.sources.append(Location(source, ns))

        #Process targets
        for target in element.findall(ns+'targets/'+ns+'target'):
            self.targets.append(Location(target, ns))

    def toString(self, prefix='\t'):
        str = '%sAction: %s [%s] running %s\n' % (prefix, self.name, self.type, self.trigger)
        str += '%s\tSources:\n' % (prefix)
        for source in self.sources:
            str += '%s\t\tlocation [%s, %s, %s]\n' % (prefix, self.location.site, self.location.path, self.location.resource)
        str += '%s\tTargets:\n' % (prefix)
        for target in self.targets:
            str += '%s\t\tlocation [%s, %s, %s]\n' % (prefix, target.location.site, target.location.path, target.location.resource)
        return str;

class Location():
    """
    Class defining all target properties
    """
    def __init__(self, element, ns):
        self.id = element.get('id')
        for location in element.findall(ns+'location'):
            self.location = self.parseLocationType(location)

    def parseLocationType(self, location):
        type = location.get('{http://www.w3.org/2001/XMLSchema-instance}type')
        if type == 'irodsns:coordinates':
            return IrodsLocation(location)
        else:
            print("Unkown location type")
            return None

class IrodsLocation:
    """
        <location xsi:type="irodsns:coordinates">
            <irodsns:site type="EUDAT">CINECA</irodsns:site>
            <irodsns:path>/path/to/destination</irodsns:path>
            <irodsns:resource>defaultResc</irodsns:resource>
        </location>
    """
    def __init__(self, element):
        self.dpmIrodsns = '{http://eudat.eu/2013/iRODS-policy}'
        self.site = element.findall(self.dpmIrodsns+'site')[0].text.strip()
        if not element.findall(self.dpmIrodsns+'path')[0].text == None:
            self.path = element.findall(self.dpmIrodsns+'path')[0].text.strip()
        else:
            self.path = ''
        resElements = element.findall(self.dpmIrodsns+'resource')
        if resElements == None or len(resElements) <= 0:
            self.resource = None
        else:
            self.resource = resElements[0].text.strip()

