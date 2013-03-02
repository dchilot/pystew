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

import collections
import xml.sax


class Coordinates(object):
    """
    Starts at #line = 1, #column = 1 to identify characters in a 'file'.
    """
    def __init__(self, line, column):
        self.line = line
        self.column = column

    def add(self, offset):
        """
        Compute the Coordinates the cursor would be after going through the
        characters described by #offset. The only newline characters recognized
        to jump to a new line is '\n'.
        """
        splitted = offset.split("\n")
        line_offset = len(splitted) - 1
        column_offset = len(splitted[-1])
        return Coordinates(
            self.line + line_offset, self.column + column_offset)

    def __str__(self):
        return "(l = " + str(self.line) + " ; c = " +\
            str(self.column) + ")"

    def __eq__(self, other):
        return ((self.line == other.line) and (self.column == other.column))

    def __lt__(self, other):
        return ((self.line < other.line) or
                ((self.line == other.line) and (self.column < other.column)))

    def __le__(self, other):
        return ((self.line < other.line) or
                ((self.line == other.line) and (self.column <= other.column)))

    def __hash__(self):
        return hash(str(self))


class Range(object):
    """
    Span between two coordinates (type Coorinates): begin (included) and
    end (excluded).
    It may contain a back pointer on the xpath that this range describes.
    If #previous and #next are not None, they point to the adjacent ranges in
    the file.
    """
    def __init__(self, begin=None, end=None, xpath=None):
        self._begin = begin
        self._end = end
        self._check_invariant()
        self._next = None
        self._previous = None
        self.xpath = xpath
        self._check_invariant()

    def _check_invariant(self):
        """
        This should be checked every time the object is updated.
        """
        if (not ((self._begin is None) or (self._end is None) or
                (self._begin < self._end))):
            print self._begin, self._end
            raise ValueError("Invariant broken !")

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value
        self._check_invariant()

    @property
    def begin(self):
        return self._begin

    @begin.setter
    def begin(self, value):
        self._begin = value
        self._check_invariant()

    @property
    def next(self):
        return self._next

    @property
    def previous(self):
        return self._previous

    def try_to_link(self, other):
        """
        Try to link then end of this range to the begining of then begining of
        the #other. This will work if the ranges are adjacent and #self before
        #other in the file.
        """
        linked = True
        if (self.end == other.begin):
            self._next = other
            other._previous = self
        elif (other.end == self.begin):
            # no coverage for this branch in the tests ... maybe it is useless
            other._next = self
            self._previous = other
        else:
            linked = False
        return linked

    def __eq__(self, other):
        return ((self.begin == other.begin) and (self._end == other._end))

    def __lt__(self, other):
        return ((self.begin < other.begin) or
                ((self.begin == other.begin) and (self._end < other._end)))

    def contains(self, coordinates):
        """
        Returns true if and only if #coorinates is in this range.
        """
        return ((self._begin <= coordinates) and
                ((self._end is None) or (coordinates < self._end)))

    def __str__(self):
        return '(xpath = ' + str(self.xpath) +\
            ' ; b = ' + str(self._begin) + ' ; e = ' + str(self._end) + ')'


class XPath(object):
    """
    Object that describes a very simple xpath expression to identify an
    element. The depth is the number of ancestors an xpath has.
    """
    def __init__(self, name, parent=None, begin_coordinates=None):
        """
        If the elment named #name is not the root, it should have a parent.
        If you work in a file, you should give the first coordinates the
        element appears in the file (#begin_coorinates).
        """
        self.name = name
        self._parent = parent
        if (len(name) == 0):
            raise ValueError("Tag name can not be empty.")
        if (parent is not None):
            self.depth = parent.depth + 1
            self._count = 1
        else:
            self.depth = 1
            self._count = 1
        self.multiple = (self._count > 1)
        if (begin_coordinates is not None):
            self._coordinates = [Range(begin_coordinates, xpath=self)]
        else:
            self._coordinates = []
        self._next = None
        self._previous = None

    def add_begin(self, coordinates):
        """
        In a file, ranges that are part of one single element are not all
        adjacent, so you may have to add the begining of an other portion
        starting at #coordinates.
        """
        assert((len(self._coordinates) == 0) or
               ((self._coordinates[-1].begin is not None) and
                (self._coordinates[-1].end is not None)))
        self._coordinates.append(Range(coordinates, xpath=self))

    def add_end(self, coordinates):
        """
        You will have to tell when the begun ranges end by providing
        #coordinates except for the root (so anything still in the file but
        outside of the xml root will still be marked as belonging to the root).
        """
        assert((len(self._coordinates) > 0) and
               (self._coordinates[-1].begin is not None) and
               (self._coordinates[-1].end is None))
        assert(self._coordinates[-1].begin < coordinates)
        self._coordinates[-1].end = coordinates

    def try_to_link(self, other):
        """
        Glue together two xpaths to show they are adjacent.
        """
        linked = False
        if ((len(self._coordinates) != 0) and (len(other._coordinates) != 0)):
            if (self._coordinates[-1].try_to_link(other._coordinates[-1])):
                linked = True
        return linked

    def get_next_from(self, coordinates):
        """
        Get the first range that does not belong to this xpath starting from
        #coordinates (positive). It will return None if not found.
        """
        next = coordinates
        found = False
        result = None
        for r in self._coordinates:
            if (r.contains(next)):
                found = True
                next = r.end
                result = r.next
            else:
                if (found):
                    break
        return result

    def get_previous_from(self, coordinates):
        """
        Get the first range that does not belong to this xpath starting from
        #coordinates (negative). It will return None if not found.
        """
        previous = coordinates
        found = False
        result = None
        self._coordinates.reverse()
        for r in self._coordinates:
            if (r.contains(previous)):
                found = True
                previous = r.begin
                result = r.previous
            else:
                if (found):
                    break
        self._coordinates.sort()
        return result

    @property
    def closed(self):
        """
        True if and only if all the ranges for the xpath have a valid begin and
        end. Please not that the XPath for the root element is not closed.
        """
        return ((len(self._coordinates) == 0) or
                ((self._coordinates[-1].begin is not None) and
                 (self._coordinates[-1].end is not None)))

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def names(self):
        """
        Returns the name of the element matched by this xpath preceeded by
        those of its ancestors in a list.
        """
        result = []
        if (self._parent is not None):
            result += self._parent.names
        result.append(self.name)
        return result

    @property
    def hierarchy(self):
        """
        Returns this xpath preceeded by its ancestors in a list.
        """
        result = []
        if (self._parent is not None):
            result += self._parent.hierarchy
        result.append(self)
        return result

    @property
    def count(self):
        """
        The number of elements matched by this xpath when not using any index
        (#seealso #simple_str).
        """
        return self._count

    @count.setter
    def count(self, value):
        """
        You should use this setter when you know this xpath would match more
        than one element (#seealso #__str__).
        """
        self.multiple = (value > 1)
        self._count = value

    @property
    def simple_str(self):
        result = ""
        if (self._parent is not None):
            result += str(self._parent)
        result += "/"
        result += self.name
        return result

    def __str__(self):
        """
        Returns the xpath with an index for arrays to identify precisely only
        one element.
        """
        result = self.simple_str
        if (self.multiple):
            result += "[" + str(self._count) + "]"
        return result

    def __eq__(self, other):
        return (str(self) == str(other))

    def __lt__(self, other):
        if (self.depth < other.depth):
            return True
        elif (self.depth > other.depth):
            return False
        else:
            for self_name, other_name in zip(self.names, other.names):
                if (self_name < other_name):
                    return True
                elif (self_name > other_name):
                    return False
        return False

    def contains(self, other):
        """
        Returns True if and only #self contains #other, which means #other is
        an ancestor of #self (or #self itself), but checking by names if they
        have different depths. NB: when built properly this could be checked by
        looking at the ancestors (this might be tried one day).
        """
        if (self == other):
            return True
        if (self.depth < other.depth):
            return False
        elif (self.depth > other.depth):
            for self_, other_ in zip(self.hierarchy, other.hierarchy):
                self_name = self_.name
                other_name = other_.name
                self_count = self_.count
                other_count = other_.count
                if ((self_name != other_name) or (self_count != other_count)):
                    return False
            return True
        else:
            return False

    def contains_coordinates(self, coordinates):
        for r in self._coordinates:
            if (r.begin <= coordinates):
                if ((r.end is None) or (coordinates < r.end)):
                    return True
        return False


class XPathMapper(xml.sax.ContentHandler):
    """
    SAX handler to use in order to compute the xpath to reach the elements,
    mapped to coordinates in the parsed file.
    """
    def __init__(self):
        """
        Just create the objects needed.
        """
        self._locator = None
        # map coordinates to xpath
        self.coordinates = {}
        self._path = [None]
        self._xpaths_counter = collections.Counter()
        # store only the first occurrence of an xpath (start + end)
        # key: xpath ; value: [coordinates]
        self._xpaths = collections.defaultdict(list)
        self._index = []
        self._last_xpath = None
        self._conflicts = collections.defaultdict(list)

    def startDocument(self):
        """
        Override xml.sax.ContentHandler.startDocument
        """
        self.coordinates.clear()
        self._xpaths_counter.clear()
        self._xpaths.clear()
        del self._index[:]
        self._last_xpath = None
        self._conflicts.clear()

    def endDocument(self):
        """
        Override xml.sax.ContentHandler.endDocument
        """
        self._xpaths.clear()
        for coordinates in sorted(self.coordinates):
            xpath = self.coordinates[coordinates]
            if ((coordinates in self._conflicts.keys()) and
                    (xpath in self._conflicts[coordinates])):
                # there was a self-closed element
                pass
            else:
                self._xpaths[xpath.simple_str].append(coordinates)

    def setDocumentLocator(self, locator):
        """
        Override xml.sax.ContentHandler.setDocumentLocator
        """
        self._locator = locator

    def startElement(self, name, attrs):
        """
        Override xml.sax.ContentHandler.startElement
        """
        coord = Coordinates(self._locator.getLineNumber(),
                            self._locator.getColumnNumber() + 1)
        xpath = XPath(name, self._path[-1], coord)
        if (coord in self.coordinates.keys()):
            self._conflicts[coord].append(self._last_xpath)
        if (self._last_xpath is not None):
            self._last_xpath.add_end(coord)
            assert(self._last_xpath.try_to_link(xpath))
        xpath_str = str(xpath)
        self._path.append(xpath)
        if (xpath_str in self._xpaths_counter.keys()):
            self._xpaths_counter[xpath_str] += 1
            self._index.append(self._xpaths_counter[xpath_str])
            xpath.count = self._xpaths_counter[xpath_str]
            if (xpath.count == 2):
                for coordinates in self._xpaths[xpath.simple_str]:
                    old_xpath = self.coordinates[coordinates]
                    old_xpath.multiple = True
                self._xpaths[xpath.simple_str + "[1]"] = \
                    self._xpaths[xpath.simple_str]
                #self._garbage.append(xpath.simple_str)
        else:
            self._index.append(None)
            self._xpaths_counter[xpath_str] += 1
        self._xpaths[xpath.simple_str].append(coord)
        self.coordinates[coord] = xpath
        self._last_xpath = xpath

    def characters(self, content):
        """
        Override xml.sax.ContentHandler.characters
        """
        xpath = self._path[-1]
        if (xpath != self._last_xpath):
            coord = Coordinates(self._locator.getLineNumber(),
                                self._locator.getColumnNumber() + 1)
            if (coord in self.coordinates.keys()):
                self._conflicts[coord].append(self._last_xpath)
            self._last_xpath.add_end(coord)
            xpath.add_begin(coord)
            assert(self._last_xpath.try_to_link(xpath))
            self._last_xpath = xpath

    def endElement(self, name):
        """
        Override xml.sax.ContentHandler.endElement
        """
        coord = Coordinates(self._locator.getLineNumber(),
                            self._locator.getColumnNumber() + 1)
        if (coord in self.coordinates.keys()):
            self._conflicts[coord].append(self._last_xpath)
        xpath = self._path[-1]
        if (xpath != self._last_xpath):
            self._last_xpath.add_end(coord)
            xpath.add_begin(coord)
            assert(self._last_xpath.try_to_link(xpath))
        if (self._index[-1] is not None):
            xpath.count = self._index[-1]
        self._xpaths[xpath.simple_str].append(coord)
        self.coordinates[coord] = xpath
        self._path.pop()
        self._index.pop()
        self._last_xpath = xpath

    def get_xpath(self, line, column):
        """
        This is the only interesting method in the whole file. Returns the
        xpath to get the element at the coordinates identified by #line and
        #column. If you are outside the root element, you will still get an
        xpath to the root element.
        You need the object to have built an inner representation either by
        calling #parse or by giving this object has a handler to a sax
        method doing the parsing.
        `line`: starts at 1.
        `column`: starts at 0.
        """
        reference = Coordinates(line, column)
        for xpath in self.coordinates.values():
            if (xpath.contains_coordinates(reference)):
                return xpath
        return None

    def parse(self, text):
        """
        Shortcut so that users do not have to worry about finding the sax
        method to parse a string. This will build the inner representation
        of `text` so that you can call #get_xpath.
        `text`: a string containing XML to parse.
        """
        xml.sax.parseString(text, self)

    def get_coordinates(self, xpath):
        """
        Returns the coordinates of the tags delimiting the element which
        match #xpath, if this element is found. For a self-closed element
        only on set of coordinates is returned, but if two tags are present
        then two sets of coorinates will be returned.
        `xpath`: this has to be an absolute xpath expression and match an
        element to be considered valid.
        """
        if (xpath.endswith(']')):
            open_bracket = xpath.rfind('[')
            index = int(xpath[open_bracket + 1:len(xpath) - 1])
            if (index > 0):
                short_xpath = xpath[:open_bracket]
                if (short_xpath in self._xpaths.keys()):
                    if ((index * 2) <= len(self._xpaths[short_xpath])):
                        begin = index * 2 - 2
                        end = begin + 2
                        return self._xpaths[short_xpath][begin:end]
        elif (xpath in self._xpaths.keys()):
            return self._xpaths[xpath]
        return []


def fake_main():
    """
    This is not a real main. You should not really try to run this module as
    a script so this will probably stay here for testing purpose.
    """
    complete = '''<root>
    <element att1="a" att2="42"/>
    <element>
        <text>this is some text</text>
    </element>
    <element>
        <sub>
            <a>text 1</a>
        </sub>
        <sub>
            <a>text 2</a>
            <b>text 3</b>
            <c>text 4</c>
        </sub>
    </element>
</root>'''
    mapper = XPathMapper()
    mapper.parse(complete)
    print mapper._xpaths
    for xpath, value in mapper._xpaths.items():
        print "---"
        print str(xpath)
        print str(value)

if (__name__ == "__main__"):  # pragma: no cover
    fake_main()
