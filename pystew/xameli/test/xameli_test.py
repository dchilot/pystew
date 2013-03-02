#Copyright (c) 2012 'pystew developpers'
#
#This software is provided 'as-is', without any express or implied
#warranty. In no event will the authors be held liable for any damages
#arising from the use of this software.
#
#Permission is granted to anyone to use this software for any purpose,
#including commercial applications, and to alter it and redistribute it
#freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

#
#$Rev::               $: Revision of last commit
#$Author::            $: Author of last commit
#$Date::              $: Date of last commit

# make sure the local version is used instead of the one in the python lib folder
# http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
import os
import sys
import inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "..", "..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import unittest
#from pystew import xameli
import pystew.xameli
import xml.sax
import StringIO
import lxml.etree

from nose.tools import raises
from nose.tools import assert_equal
from nose.tools import assert_not_equal


class CoordinatesTests(unittest.TestCase):
    def test_1(self):
        coordinates = pystew.xameli.Coordinates(1, 2)
        assert_equal(1, coordinates.line)
        assert_equal(2, coordinates.column)
        other_coordinates = pystew.xameli.Coordinates(3, 2)
        assert_not_equal(other_coordinates, coordinates)
        same_coordinates = pystew.xameli.Coordinates(1, 2)
        assert_equal(same_coordinates, coordinates)
        assert(other_coordinates > coordinates)

    def test_2(self):
        coordinates = pystew.xameli.Coordinates(1, 1)
        assert_equal(pystew.xameli.Coordinates(1, 2), coordinates.add(" "))

    def test_3(self):
        assert(pystew.xameli.Coordinates(4, 6) <= pystew.xameli.Coordinates(4, 6))
        assert(pystew.xameli.Coordinates(3, 6) <= pystew.xameli.Coordinates(4, 6))
        assert(pystew.xameli.Coordinates(4, 6) <= pystew.xameli.Coordinates(4, 7))


class RangeTests(unittest.TestCase):
    def test_1(self):
        r = pystew.xameli.Range()
        assert(r.begin is None)
        assert(r.end is None)
        begin = pystew.xameli.Coordinates(1, 2)
        r.begin = begin
        assert_equal(begin, r.begin)
        end = pystew.xameli.Coordinates(3, 4)
        r.end = end
        assert_equal(end, r.end)

    def test_2(self):
        c1 = pystew.xameli.Coordinates(1, 1)
        r = pystew.xameli.Range(c1)
        assert_equal(c1, r.begin)
        assert(r.end is None)
        begin = pystew.xameli.Coordinates(1, 2)
        r.begin = begin
        assert_equal(begin, r.begin)
        end = pystew.xameli.Coordinates(3, 4)
        r.end = end
        assert_equal(end, r.end)

    def test_3(self):
        c1 = pystew.xameli.Coordinates(1, 1)
        r = pystew.xameli.Range(begin=c1)
        assert_equal(c1, r.begin)
        assert(r.end is None)
        begin = pystew.xameli.Coordinates(1, 2)
        r.begin = begin
        assert_equal(begin, r.begin)
        end = pystew.xameli.Coordinates(3, 4)
        r.end = end
        assert_equal(end, r.end)

    def test_4(self):
        c1 = pystew.xameli.Coordinates(2, 1)
        r = pystew.xameli.Range(end=c1)
        assert_equal(c1, r.end)
        assert(r.begin is None)
        begin = pystew.xameli.Coordinates(1, 2)
        r.begin = begin
        assert_equal(begin, r.begin)
        end = pystew.xameli.Coordinates(3, 4)
        r.end = end
        assert_equal(end, r.end)

    def test_5(self):
        c1 = pystew.xameli.Coordinates(1, 1)
        c2 = pystew.xameli.Coordinates(1, 4)
        r = pystew.xameli.Range(end=c2, begin=c1)
        assert_equal(c1, r.begin)
        assert_equal(c2, r.end)
        begin = pystew.xameli.Coordinates(1, 3)
        r.begin = begin
        assert_equal(begin, r.begin)
        end = pystew.xameli.Coordinates(3, 4)
        r.end = end
        assert_equal(end, r.end)

    @raises(Exception)
    def test_6(self):
        c1 = pystew.xameli.Coordinates(1, 1)
        c2 = pystew.xameli.Coordinates(1, 2)
        pystew.xameli.Range(begin=c2, end=c1)

    @raises(Exception)
    def test_7(self):
        r = pystew.xameli.Range(pystew.xameli.Coordinates(1, 2))
        r.end = pystew.xameli.Coordinates(1, 1)

    @raises(ValueError)
    def test_8(self):
        r = pystew.xameli.Range(end=pystew.xameli.Coordinates(2, 2))
        r.begin = pystew.xameli.Coordinates(10, 1)

    def test_9(self):
        r = pystew.xameli.Range(pystew.xameli.Coordinates(1, 2), pystew.xameli.Coordinates(4, 5))
        assert(not r.contains(pystew.xameli.Coordinates(10, 1)))
        assert(not r.contains(pystew.xameli.Coordinates(1, 1)))
        assert(not r.contains(pystew.xameli.Coordinates(4, 6)))
        assert(not r.contains(pystew.xameli.Coordinates(4, 5)))
        assert(r.contains(pystew.xameli.Coordinates(4, 4)))
        assert(r.contains(pystew.xameli.Coordinates(1, 2)))
        assert(r.contains(pystew.xameli.Coordinates(1, 3)))
        assert(r.contains(pystew.xameli.Coordinates(4, 4)))
        assert(r.contains(pystew.xameli.Coordinates(3, 5)))
        assert(r.contains(pystew.xameli.Coordinates(2, 2)))
        assert(r.contains(pystew.xameli.Coordinates(2, 9999)))
        assert(r.contains(pystew.xameli.Coordinates(2, -22)))

    def test_10(self):
        r1 = pystew.xameli.Range(pystew.xameli.Coordinates(1, 2), pystew.xameli.Coordinates(4, 5))
        assert(r1.next is None)
        assert(r1.previous is None)
        r2 = pystew.xameli.Range(pystew.xameli.Coordinates(4, 6), pystew.xameli.Coordinates(11, 2))
        assert(r2.next is None)
        assert(r2.previous is None)
        r1.try_to_link(r2)
        assert(r1.next is None)
        assert(r2.next is None)
        assert(r1.previous is None)
        assert(r2.previous is None)
        r3 = pystew.xameli.Range(pystew.xameli.Coordinates(4, 5), pystew.xameli.Coordinates(11, 2))
        assert(r3.next is None)
        assert(r3.previous is None)
        r1.try_to_link(r3)
        assert_equal(r1.next, r3)
        assert_equal(r3.previous, r1)
        assert(r1.previous is None)
        assert(r3.next is None)
        assert_equal("(xpath = None ; b = (l = 1 ; c = 2) ; e = (l = 4 ; c = 5))", str(r1))


class XPathTests(unittest.TestCase):
    def test_1(self):
        tag = pystew.xameli.XPath("tag")
        assert_equal(str(tag), "/tag")
        assert_equal(tag.name, "tag")
        assert_equal(tag.count, 1)
        assert_equal(tag, tag)
        assert(not (tag < tag))

    def test_2(self):
        tag_1 = pystew.xameli.XPath("tag")
        tag_2 = pystew.xameli.XPath("tag")
        assert_equal(tag_1, tag_2)
        assert(not (tag_1 < tag_2))
        assert(not (tag_2 < tag_1))

    def test_3(self):
        root = pystew.xameli.XPath("root")
        sub = pystew.xameli.XPath("sub", root)
        assert_equal(sub.depth, 2)
        assert_equal(root.depth, 1)
        assert_equal(str(sub), "/root/sub")

    @raises(ValueError)
    def test_4(self):
        pystew.xameli.XPath("")

    @raises(ValueError)
    def test_5(self):
        root = pystew.xameli.XPath("root")
        pystew.xameli.XPath("", root)

    def test_6(self):
        root = pystew.xameli.XPath("root")
        sub1 = pystew.xameli.XPath("sub", root)
        assert(not sub1.multiple)
        sub2 = pystew.xameli.XPath("sub", root)
        assert(not sub2.multiple)
        assert(sub1.contains(sub2))
        assert(sub2 == sub1)
        sub_sub1 = pystew.xameli.XPath("sub_sub", sub1)
        sub_sub2 = pystew.xameli.XPath("sub_sub", sub2)
        assert(sub_sub1 == sub_sub2)
        assert(sub_sub2 == sub_sub1)
        assert(sub_sub1.contains(sub1))
        assert(sub_sub1.contains(sub2))
        assert_equal(sub_sub1.names, ["root", "sub", "sub_sub"])
        sub1.multiple = True
        assert(sub1.multiple)
        sub2.count = 2
        assert(sub2.multiple)
        assert(not sub1.contains(sub2))
        assert(not sub2.contains(sub1))
        assert(not sub2 == sub1)
        assert_equal(sub1.depth, 2)
        assert_equal(sub2.depth, 2)
        assert_equal(sub_sub1.depth, 3)
        assert(sub_sub1.contains(sub1))
        assert(not sub_sub1.contains(sub2))
        assert(sub_sub2.contains(sub2))
        assert(not sub_sub2.contains(sub1))

    @raises(Exception)
    def test_7(self):
        root = pystew.xameli.XPath("root")
        root.add_begin(pystew.xameli.Coordinates(2, 2))
        # begin < end
        root.add_end(pystew.xameli.Coordinates(1, 2))

    @raises(Exception)
    def test_8(self):
        root = pystew.xameli.XPath("root")
        # begin before end
        root.add_end(pystew.xameli.Coordinates(1, 2))

    @raises(Exception)
    def test_9(self):
        root = pystew.xameli.XPath("root")
        root.add_begin(pystew.xameli.Coordinates(2, 2))
        # begin before end before begin
        root.add_begin(pystew.xameli.Coordinates(4, 1))

    @raises(Exception)
    def test_10(self):
        root = pystew.xameli.XPath("root")
        root.add_begin(pystew.xameli.Coordinates(2, 2))
        root.add_end(pystew.xameli.Coordinates(4, 1))
        root.add_end(pystew.xameli.Coordinates(5, 1))

    def test_11(self):
        c1 = pystew.xameli.Coordinates(4, 1)
        root = pystew.xameli.XPath("root", begin_coordinates=c1)
        assert(root.contains_coordinates(c1))
        assert(not root.contains_coordinates(pystew.xameli.Coordinates(3, 3)))
        assert(root.contains_coordinates(pystew.xameli.Coordinates(4, 2)))

    def test_12(self):
        c1 = pystew.xameli.Coordinates(4, 1)
        c2 = pystew.xameli.Coordinates(4, 8)
        before_c2 = pystew.xameli.Coordinates(4, 7)
        root = pystew.xameli.XPath("root", begin_coordinates=c1)
        root.add_end(c2)
        assert(root.contains_coordinates(c1))
        assert(root.contains_coordinates(before_c2))
        assert(not root.contains_coordinates(pystew.xameli.Coordinates(5, 3)))
        assert(not root.contains_coordinates(pystew.xameli.Coordinates(4, 9)))
        assert(root.contains_coordinates(pystew.xameli.Coordinates(4, 2)))

    def test_13(self):
        root = pystew.xameli.XPath("root")
        assert(not root.contains_coordinates(pystew.xameli.Coordinates(1, 1)))
        assert(not root.contains_coordinates(pystew.xameli.Coordinates(42, 2)))

    def test_14(self):
        root = pystew.xameli.XPath("root", begin_coordinates=pystew.xameli.Coordinates(1, 1))
        assert(not root.closed)
        root.add_end(pystew.xameli.Coordinates(1, 4))
        assert(root.closed)
        for r in root.coordinates:
            print "r =", r.begin, r.end
        assert(root.contains_coordinates(pystew.xameli.Coordinates(1, 1)))
        assert(root.contains_coordinates(pystew.xameli.Coordinates(1, 3)))
        assert(not root.contains_coordinates(pystew.xameli.Coordinates(1, 4)))

    def test_15(self):
        #<root>1
        #2  3<sub>4
        #5      6<sub_sub>
        #
        root = pystew.xameli.XPath("root", begin_coordinates=pystew.xameli.Coordinates(1, 1))
        f1 = pystew.xameli.Coordinates(1, 7)
        f2 = pystew.xameli.Coordinates(2, 1)
        f3 = pystew.xameli.Coordinates(2, 4)
        f4 = pystew.xameli.Coordinates(2, 9)
        f5 = pystew.xameli.Coordinates(3, 1)
        f6 = pystew.xameli.Coordinates(3, 6)
        root.add_end(f1)
        root.add_begin(f1)
        root.add_end(f2)
        root.add_begin(f2)
        root.add_end(f3)
        sub = pystew.xameli.XPath("sub", root, begin_coordinates=f3)
        root.try_to_link(sub)
        assert_equal(root.get_next_from(pystew.xameli.Coordinates(1, 1)).xpath, sub)
        assert(root.get_previous_from(pystew.xameli.Coordinates(1, 1)) is None)
        assert_equal(
            sub.get_previous_from(pystew.xameli.Coordinates(2, 6)).xpath, root)
        assert(root.get_previous_from(pystew.xameli.Coordinates(3, 6)) is None)
        assert(root.get_next_from(pystew.xameli.Coordinates(4, 2)) is None)
        sub.add_end(f4)
        root.add_begin(f4)
        root.add_end(f5)
        root.add_begin(f5)
        root.add_end(f6)
#        sub_sub = pystew.xameli.XPath("sub_sub", root, begin_coordinates=f6)
        assert(root.get_next_from(pystew.xameli.Coordinates(0, 0)) is None)

    def test_16(self):
        system_page = pystew.xameli.XPath("system-page")
        name = pystew.xameli.XPath("name", system_page)
        assert(system_page < name)
        assert(not(system_page > name))
        assert(name > system_page)
        assert(not(name < system_page))


class XameliParse(unittest.TestCase):
    def test_1(self):
        # this is a bit ugly in order to use tabs without scaring pep8
        text = (
            '<root>\n'
            '	<element att1="a" att2="42"/>\n'
            '	<element>\n'
            '		<text>this is some text</text>\n'
            '	</element>\n'
            '</root>')
        mapper = pystew.xameli.XPathMapper()
        mapper.parse(text)
        xpath = mapper.get_xpath(4, 5)
        assert_equal("/root/element[2]/text", str(xpath))


class XameliTests(unittest.TestCase):
    @classmethod
    def setup_class(self):
        self._doc = """\
<system-page id="ef81d1c90a00016b00659a66bcacb166">
    <name>page</name>
    <is-published>true</is-published>
    <title>Lorem Ipsum Dolor Sit Amet</title>
    <summary>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</summary>
    <author>Author Name</author>
    <teaser>Teaser</teaser>
    <keywords>Comma, Separated, Keywords</keywords>
    <description>Description</description>
    <display-name>Lorem Ipsum</display-name>
    <path>/index-block-example/page</path>
    <created-by>admin</created-by>
    <created-on>1245263810949</created-on>
    <last-modified-by>admin</last-modified-by>
    <last-modified>1245954849582</last-modified>
    <page-xhtml>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. 1</p>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. 2</p>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. 3</p>
    </page-xhtml>
</system-page>"""

    def test_1(self):
        pystew.xameli.XPathMapper()

    def test_2(self):
        assert(issubclass(pystew.xameli.XPathMapper, xml.sax.ContentHandler))

    def test_3(self):
        doc = "<xml/>"
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(doc, x)
        xpath = str(x.get_xpath(1, 1))
        print "xpath = " + xpath
        assert_equal("/xml", xpath)

    def test_4(self):
        #    0 123456789
        #    1          0123456789
        #    2                    012345678
        doc = "<a><b><c>content</c></b></a>"
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(doc, x)
        self.helper(1, [(1, 3), (25, 30)], x, "/a")
        self.helper(1, [(4, 6), (21, 24)], x, "/a/b")
        self.helper(1, [(7, 20)], x, "/a/b/c")

    def helper(self, line, columns, mapper, expected):
        for column_range in columns:
            for column in range(column_range[0], column_range[1]):
                found = str(mapper.get_xpath(line, column))
                if (found != expected):
                    print "line = ", line
                    print "column = ", column
                    print "found = ", found
                    print "expected = ", expected
                assert_equal(found, expected)

    def test_5(self):
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(self._doc, x)
        self.helper(1, [(1, 52)], x, "/system-page")
        self.helper(2, [(1, 4)], x, "/system-page")

        self.helper(2, [(5, 22)], x, "/system-page/name")
        self.helper(3, [(1, 4)], x, "/system-page")

        self.helper(13, [(5, 43)], x, "/system-page/created-on")

        self.helper(16, [(5, 17)], x, "/system-page/page-xhtml")
        self.helper(17, [(1, 8)], x, "/system-page/page-xhtml")

        self.helper(17, [(9, 74)], x, "/system-page/page-xhtml/p[1]")
        self.helper(18, [(1, 8)], x, "/system-page/page-xhtml")
        self.helper(18, [(9, 74)], x, "/system-page/page-xhtml/p[2]")
        self.helper(19, [(1, 8)], x, "/system-page/page-xhtml")
        self.helper(19, [(9, 74)], x, "/system-page/page-xhtml/p[3]")
        self.helper(20, [(1, 4)], x, "/system-page/page-xhtml")

        self.helper(20, [(5, 18)], x, "/system-page/page-xhtml")

        self.helper(21, [(1, 99)], x, "/system-page")

    def test_6(self):
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(self._doc, x)
        f = StringIO.StringIO(self._doc)
        tree = lxml.etree.parse(f)
        for line, xml_line in enumerate(self._doc.split("\n")):
            line += 1
            column = xml_line.find('<') + 1
            while (column > 0):
                xpath = str(x.get_xpath(line, column))
                print line, column, xpath
                elements = tree.xpath(xpath)
                print len(elements)
                assert_equal(len(elements), 1)
                for element in elements:
                    print "'" + xml_line + "'"
                    print "'" + element.tag + "'"
                    print (xml_line.find(element.tag) > -1)
                    assert(xml_line.find(element.tag) > -1)
                    if ((len(element.text) > 0) and
                            (-1 == element.text.find("\n"))):
                        print "'" + element.text + "'"
                        assert(element.text in xml_line)
                column = xml_line.find('<', column) + 1
            line += 1

#    things should not work this way
#    def test_7(self):
#        x = pystew.xameli.XPathMapper()
#        xml.sax.parseString(self._doc, x)
#        self.helper_reverse(1, [(1, 99)], x, "/system-page")
#
#        self.helper_reverse(2, [(1, 99)], x, "/system-page/name")
#
#        self.helper_reverse(13, [(1, 99)], x, "/system-page/created-on")
#
#        self.helper_reverse(16, [(1, 99)], x, "/system-page/page-xhtml")
#
#        self.helper_reverse(17, [(1, 99)], x, "/system-page/page-xhtml/p[1]")
#        self.helper_reverse(18, [(1, 99)], x, "/system-page/page-xhtml/p[2]")
#        self.helper_reverse(19, [(1, 99)], x, "/system-page/page-xhtml/p[3]")
#
#        self.helper_reverse(20, [(1, 99)], x, "/system-page/page-xhtml")
#
#        self.helper_reverse(21, [(1, 99)], x, "/system-page")

    def test_8(self):
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(self._doc, x)
        xpath = x.get_xpath(3, 2)
        system_page = pystew.xameli.XPath("system-page")
        name = pystew.xameli.XPath("name", system_page)
        is_published = pystew.xameli.XPath("is-published", system_page)
        assert_equal(xpath, system_page)
        assert_equal(
            xpath.get_next_from(pystew.xameli.Coordinates(3, 2)).xpath, is_published)
        page_xhtml = pystew.xameli.XPath("page-xhtml", system_page)
        p3 = pystew.xameli.XPath("p", page_xhtml)
        p3.count = 3
        xpath_2 = x.get_xpath(19, 50)
        assert_equal(xpath_2, p3)
        assert_equal(xpath_2.get_previous_from(
            pystew.xameli.Coordinates(19, 50)).xpath, page_xhtml)
        xpath_3 = x.get_xpath(20, 10)
        assert_equal(xpath_3, page_xhtml)
        assert_equal(xpath_3.get_previous_from(
            pystew.xameli.Coordinates(20, 1)).xpath, p3)
        assert_equal(xpath.get_previous_from(pystew.xameli.Coordinates(3, 2)).xpath, name)

    def test_9(self):
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(self._doc, x)
        xpath = x.get_xpath(0, 0)
        assert_equal(None, xpath)

    def test_reverse(self):
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(self._doc, x)
        coordinates = x.get_coordinates('/system-page/page-xhtml/p[1]')
        assert_equal(2, len(coordinates))
        coordinates = x.get_coordinates('/system-page/page-xhtml/p[3]')
        assert_equal(2, len(coordinates))
        coordinates = x.get_coordinates('/system-page/page-xhtml/p[2]')
        expected_coordinates = [
            pystew.xameli.Coordinates(18, 9),
            pystew.xameli.Coordinates(18, 70),
        ]
        assert_equal(len(expected_coordinates), len(coordinates))
        assert_equal(expected_coordinates, coordinates)

    def test_reverse_2(self):
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(self._doc, x)
        coordinates = x.get_coordinates('/system-page')
        expected_coordinates = [
            pystew.xameli.Coordinates(1, 1),
            pystew.xameli.Coordinates(21, 1),
        ]
        assert_equal(len(expected_coordinates), len(coordinates))
        assert_equal(expected_coordinates, coordinates)

    def test_reverse_3(self):
        x = pystew.xameli.XPathMapper()
        #           0 123456789
        #           1          0123456789
        #           2                    0123456789
        #           3                              012
        with_empty = "<x><t><e/></t><t><e></e></t></x>"
        xml.sax.parseString(with_empty, x)
        found = x.get_xpath(1, 11)
        assert_equal('/x/t[1]', str(found))
        print x._xpaths
        for xpath, value in x._xpaths.items():
            print "---"
            print str(xpath)
            print str(value)
        coordinates = x.get_coordinates('/x/t[1]/e')
        for coords in coordinates:
            print coords
        expected_coordinates = [
            pystew.xameli.Coordinates(1, 7),
        ]
        assert_equal(len(expected_coordinates), len(coordinates))
        assert_equal(expected_coordinates, coordinates)
        coordinates = x.get_coordinates('/x/t[2]/e')
        expected_coordinates = [
            pystew.xameli.Coordinates(1, 18),
            pystew.xameli.Coordinates(1, 21),
        ]
        assert_equal(len(expected_coordinates), len(coordinates))
        assert_equal(expected_coordinates, coordinates)

    def test_reverse_4(self):
        x = pystew.xameli.XPathMapper()
        xml.sax.parseString(self._doc, x)
        coordinates = x.get_coordinates('/nfh')
        assert_equal([], coordinates)


class XameliMain(unittest.TestCase):
    def test_main(self):
        pystew.xameli.fake_main()
