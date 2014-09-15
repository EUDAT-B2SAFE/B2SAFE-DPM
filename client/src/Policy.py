class Policy():
    def __init__(self, element, ns):
        self.root = element
        self.ns = ns
        self.name = None
        self.version = None
        self.author = None
        self.policyId = None

    def parse(self):
        self.name = self.root.get('name')
        self.version = self.root.get('version')
        self.author = self.root.get('author')
        self.policyId = self.root.get('uniqueid')

    def toString(self, prefix='\t'):
        return '%sName: %s\n%sVersion:%s\n%sAuthor: %s\n%sID:%s\n' % (prefix, self.name, prefix,self.version, prefix,self.author, prefix,self.policyId)

