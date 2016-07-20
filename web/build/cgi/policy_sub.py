#!/usr/bin/env python

#
# Generated Wed Jul 13 14:25:23 2016 by generateDS.py version 2.12b.
#

import sys

import policy_lib as supermod

etree_ = None
Verbose_import_ = False
(
    XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
) = range(3)
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError(
                        "Failed to import ElementTree from any known place")


def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
            'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#


class policySub(supermod.policy):
    def __init__(self, name=None, created=None, author=None, community=None, version=None, uniqueid=None, dataset=None, actions=None, anytypeobjs_=None):
        super(policySub, self).__init__(name, created, author, community, version, uniqueid, dataset, actions, anytypeobjs_, )
supermod.policy.subclass = policySub
# end class policySub


class locationPointSub(supermod.locationPoint):
    def __init__(self, ref=None, id=None, persistentIdentifier=None, location=None):
        super(locationPointSub, self).__init__(ref, id, persistentIdentifier, location, )
supermod.locationPoint.subclass = locationPointSub
# end class locationPointSub


class locationTypeSub(supermod.locationType):
    def __init__(self):
        super(locationTypeSub, self).__init__()
supermod.locationType.subclass = locationTypeSub
# end class locationTypeSub


class actionTypeSub(supermod.actionType):
    def __init__(self, policyID=None, valueOf_=None):
        super(actionTypeSub, self).__init__(policyID, valueOf_, )
supermod.actionType.subclass = actionTypeSub
# end class actionTypeSub


class triggerTypeSub(supermod.triggerType):
    def __init__(self, action=None, time=None, runonce=None, repeat_counter=None):
        super(triggerTypeSub, self).__init__(action, time, runonce, repeat_counter, )
supermod.triggerType.subclass = triggerTypeSub
# end class triggerTypeSub


class triggerActionTypeSub(supermod.triggerActionType):
    def __init__(self, ref=None, valueOf_=None):
        super(triggerActionTypeSub, self).__init__(ref, valueOf_, )
supermod.triggerActionType.subclass = triggerActionTypeSub
# end class triggerActionTypeSub


class coordinatesSub(supermod.coordinates):
    def __init__(self, site=None, path=None, resource=None, anytypeobjs_=None):
        super(coordinatesSub, self).__init__(site, path, resource, anytypeobjs_, )
supermod.coordinates.subclass = coordinatesSub
# end class coordinatesSub


class datasetTypeSub(supermod.datasetType):
    def __init__(self, collection=None, anytypeobjs_=None):
        super(datasetTypeSub, self).__init__(collection, anytypeobjs_, )
supermod.datasetType.subclass = datasetTypeSub
# end class datasetTypeSub


class actionsTypeSub(supermod.actionsType):
    def __init__(self, action=None, anytypeobjs_=None):
        super(actionsTypeSub, self).__init__(action, anytypeobjs_, )
supermod.actionsType.subclass = actionsTypeSub
# end class actionsTypeSub


class actionType1Sub(supermod.actionType1):
    def __init__(self, name=None, id=None, type_=None, trigger=None, sources=None, targets=None, anytypeobjs_=None):
        super(actionType1Sub, self).__init__(name, id, type_, trigger, sources, targets, anytypeobjs_, )
supermod.actionType1.subclass = actionType1Sub
# end class actionType1Sub


class sourcesTypeSub(supermod.sourcesType):
    def __init__(self, source=None, anytypeobjs_=None):
        super(sourcesTypeSub, self).__init__(source, anytypeobjs_, )
supermod.sourcesType.subclass = sourcesTypeSub
# end class sourcesTypeSub


class targetsTypeSub(supermod.targetsType):
    def __init__(self, target=None, anytypeobjs_=None):
        super(targetsTypeSub, self).__init__(target, anytypeobjs_, )
supermod.targetsType.subclass = targetsTypeSub
# end class targetsTypeSub


class persistentIdentifierTypeSub(supermod.persistentIdentifierType):
    def __init__(self, type_=None, valueOf_=None):
        super(persistentIdentifierTypeSub, self).__init__(type_, valueOf_, )
supermod.persistentIdentifierType.subclass = persistentIdentifierTypeSub
# end class persistentIdentifierTypeSub


class runonceTypeSub(supermod.runonceType):
    def __init__(self):
        super(runonceTypeSub, self).__init__()
supermod.runonceType.subclass = runonceTypeSub
# end class runonceTypeSub


class repeat_counterTypeSub(supermod.repeat_counterType):
    def __init__(self, interval_minutes=None, valueOf_=None):
        super(repeat_counterTypeSub, self).__init__(interval_minutes, valueOf_, )
supermod.repeat_counterType.subclass = repeat_counterTypeSub
# end class repeat_counterTypeSub


class siteTypeSub(supermod.siteType):
    def __init__(self, type_=None, valueOf_=None):
        super(siteTypeSub, self).__init__(type_, valueOf_, )
supermod.siteType.subclass = siteTypeSub
# end class siteTypeSub


class datasetType2Sub(supermod.datasetType2):
    def __init__(self, collection=None, anytypeobjs_=None):
        super(datasetType2Sub, self).__init__(collection, anytypeobjs_, )
supermod.datasetType2.subclass = datasetType2Sub
# end class datasetType2Sub


class actionsType3Sub(supermod.actionsType3):
    def __init__(self, action=None, anytypeobjs_=None):
        super(actionsType3Sub, self).__init__(action, anytypeobjs_, )
supermod.actionsType3.subclass = actionsType3Sub
# end class actionsType3Sub


class actionType4Sub(supermod.actionType4):
    def __init__(self, name=None, id=None, type_=None, trigger=None, sources=None, targets=None, anytypeobjs_=None):
        super(actionType4Sub, self).__init__(name, id, type_, trigger, sources, targets, anytypeobjs_, )
supermod.actionType4.subclass = actionType4Sub
# end class actionType4Sub


class sourcesType5Sub(supermod.sourcesType5):
    def __init__(self, source=None, anytypeobjs_=None):
        super(sourcesType5Sub, self).__init__(source, anytypeobjs_, )
supermod.sourcesType5.subclass = sourcesType5Sub
# end class sourcesType5Sub


class targetsType6Sub(supermod.targetsType6):
    def __init__(self, target=None, anytypeobjs_=None):
        super(targetsType6Sub, self).__init__(target, anytypeobjs_, )
supermod.targetsType6.subclass = targetsType6Sub
# end class targetsType6Sub


class persistentIdentifierType7Sub(supermod.persistentIdentifierType7):
    def __init__(self, type_=None, valueOf_=None):
        super(persistentIdentifierType7Sub, self).__init__(type_, valueOf_, )
supermod.persistentIdentifierType7.subclass = persistentIdentifierType7Sub
# end class persistentIdentifierType7Sub


class runonceType8Sub(supermod.runonceType8):
    def __init__(self):
        super(runonceType8Sub, self).__init__()
supermod.runonceType8.subclass = runonceType8Sub
# end class runonceType8Sub


class repeat_counterType9Sub(supermod.repeat_counterType9):
    def __init__(self, interval_minutes=None, valueOf_=None):
        super(repeat_counterType9Sub, self).__init__(interval_minutes, valueOf_, )
supermod.repeat_counterType9.subclass = repeat_counterType9Sub
# end class repeat_counterType9Sub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'policy'
        rootClass = supermod.policy
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:tns="http://eudat.eu/2013/policy"',
            pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'policy'
        rootClass = supermod.policy
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
    if not silence:
        content = etree_.tostring(
            rootElement, pretty_print=True,
            xml_declaration=True, encoding="utf-8")
        sys.stdout.write(content)
        sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'policy'
        rootClass = supermod.policy
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:tns="http://eudat.eu/2013/policy"')
    return rootObj


def parseLiteral(inFilename, silence=False):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    roots = get_root_tag(rootNode)
    rootClass = roots[1]
    if rootClass is None:
        rootClass = supermod.policy
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('#from ??? import *\n\n')
        sys.stdout.write('import ??? as model_\n\n')
        sys.stdout.write('rootObj = model_.policy(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_="policy")
        sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()
