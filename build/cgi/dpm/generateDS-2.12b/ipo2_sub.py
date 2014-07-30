#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys

import ipo2_sup as supermod

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


class PurchaseOrderTypeSub(supermod.PurchaseOrderType):
    def __init__(self, orderDate=None, shipTo=None, billTo=None, comment=None, items=None):
        super(PurchaseOrderTypeSub, self).__init__(orderDate, shipTo, billTo, comment, items, )
supermod.PurchaseOrderType.subclass = PurchaseOrderTypeSub
# end class PurchaseOrderTypeSub


class ItemsSub(supermod.Items):
    def __init__(self, item=None):
        super(ItemsSub, self).__init__(item, )
supermod.Items.subclass = ItemsSub
# end class ItemsSub


class itemSub(supermod.item):
    def __init__(self, partNum=None, productName=None, quantity=None, USPrice=None, comment=None, shipDate=None):
        super(itemSub, self).__init__(partNum, productName, quantity, USPrice, comment, shipDate, )
supermod.item.subclass = itemSub
# end class itemSub


class AddressSub(supermod.Address):
    def __init__(self, name=None, street=None, city=None, extensiontype_=None):
        super(AddressSub, self).__init__(name, street, city, extensiontype_, )
supermod.Address.subclass = AddressSub
# end class AddressSub


class USAddressSub(supermod.USAddress):
    def __init__(self, name=None, street=None, city=None, state=None, zip=None):
        super(USAddressSub, self).__init__(name, street, city, state, zip, )
supermod.USAddress.subclass = USAddressSub
# end class USAddressSub


class UKAddressSub(supermod.UKAddress):
    def __init__(self, name=None, street=None, city=None, category_attr=None, exportCode=None, postcode=None, category=None):
        super(UKAddressSub, self).__init__(name, street, city, category_attr, exportCode, postcode, category, )
supermod.UKAddress.subclass = UKAddressSub
# end class UKAddressSub


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
        rootTag = 'purchaseOrder'
        rootClass = supermod.PurchaseOrderType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:ipo="http://www.example.com/IPO"',
            pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'purchaseOrder'
        rootClass = supermod.PurchaseOrderType
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
        rootTag = 'purchaseOrder'
        rootClass = supermod.PurchaseOrderType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:ipo="http://www.example.com/IPO"')
    return rootObj


def parseLiteral(inFilename, silence=False):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    roots = get_root_tag(rootNode)
    rootClass = roots[1]
    if rootClass is None:
        rootClass = supermod.PurchaseOrderType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('#from ipo2_sup import *\n\n')
        sys.stdout.write('import ipo2_sup as model_\n\n')
        sys.stdout.write('rootObj = model_.purchaseOrder(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_="purchaseOrder")
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
