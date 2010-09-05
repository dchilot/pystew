"""Generate a regular expression based on sample strings."""

#Copyright (c) 2010 'pystew developpers'
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


import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='regexp.log',
    filemode='w')

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def escapeChar(char):
    import sre_parse
    if (None == char):
        return ''
    if ((char in sre_parse.SPECIAL_CHARS) or ("-" == char) or ("]" == char)):
        return "\\" + char
    return char

class Char:
    """
    >>> Char('a').getCategory()
    'LOWER_CASE_LETTER'
    >>> Char('G').getCategory()
    'UPPER_CASE_LETTER'
    >>> Char(' ').getCategory()
    'category_space'
    >>> Char('\\t').getCategory()
    'category_space'
    >>> Char('?').getCategory()
    'SPECIAL'
    >>> Char('_').getCategory()
    'OTHER_WORD'
    >>> Char(None).getCategory()
    'NONE'
    >>> (Char('4').getCategory() == Char('7').getCategory())
    True
    >>> (Char('A').getCategory() == Char('G').getCategory())
    True
    >>> (Char('f').getCategory() == Char('i').getCategory())
    True
    >>> (Char('+').getCategory() == Char('?').getCategory())
    True
    >>> (Char('-').getCategory() == Char('~').getCategory())
    True
    >>> # '_' is in its own category ('OTHER_WORD')
    >>> (Char('_').getCategory() != Char('\').getCategory())
    True
    """

    SPECIAL = 'SPECIAL'
    UNKNOWN = 'UNKNOWN'
    LOWER_CASE_LETTER = 'LOWER_CASE_LETTER'
    UPPER_CASE_LETTER = 'UPPER_CASE_LETTER'
    OTHER_WORD = 'OTHER_WORD'
    NONE = 'NONE'

    def __init__(self, char, type = "strict"):
        from sre_parse import DIGITS, SPECIAL_CHARS, CATEGORY_DIGIT
        from sre_parse import WHITESPACE, CATEGORY_SPACE
        def _getCategory(char):
            if (None == char):
                return Char.NONE
            elif ('_' == char):
                return Char.OTHER_WORD
            elif (char in DIGITS):
                return CATEGORY_DIGIT
            elif (char in SPECIAL_CHARS):
                return Char.SPECIAL
            elif (char in WHITESPACE):
                return CATEGORY_SPACE
            elif (char.isalpha()):
                if (char.islower()):
                    return Char.LOWER_CASE_LETTER
                else:
                    return Char.UPPER_CASE_LETTER
            else:
                return Char.UNKNOWN

        self._type = type
        self._category = _getCategory(char)
        self._char = char
        logging.debug("char = " + str(char))
        logging.debug("self._category = " + self._category)

    def getAllCategories():
        from sre_parse import DIGITS, SPECIAL_CHARS, CATEGORY_DIGIT
        from sre_parse import WHITESPACE, CATEGORY_SPACE
        return [CATEGORY_DIGIT, SPECIAL, CATEGORY_SPACE, 
            Char.LOWER_CASE_LETTER, Char.UPPER_CASE_LETTER, 
            Char.UNKNOWN]

    def getCategory(self):
        return self._category

    def getChar(self):
        return self._char

    def getString(self):
        return escapeChar(self._char)

    def getIsOrdered(self):
        from sre_parse import CATEGORY_DIGIT
        return (self._category in [CATEGORY_DIGIT, 
            Char.LOWER_CASE_LETTER, Char.UPPER_CASE_LETTER])

    def __eq__(self, other_char):
        if (None == other_char):
            return False
        return (self._char == other_char._char)

    def __ne__(self, other_char):
        if (None == other_char):
            return True
        return (self._char != other_char._char)

    def __lt__(self, other_char):
        if (None == other_char):
            return True
        return (self._char < other_char._char)

    def __gt__(self, other_char):
        if (None == other_char):
            return False
        return (self._char > other_char._char)

# constants
DIGITS = Char('0')
"""Sample for digits category."""
LOWER_CASE_LETTERS = Char('a')
"""Sample for lower case letters category."""
UPPER_CASE_LETTERS = Char('A')
"""Sample for upper case letters category."""
SPACES = Char(' ')
"""Sample for spaces category."""
OTHERS = Char('-')
"""Sample for 'characters not in any other category' category."""
OTHER_WORDS = Char('_')
"""Sample for 'character(s) that are included in the \w class but are not in 
any other category' category."""
SPECIALS = Char('?')
"""Sample for characters that need to be escaped because they have a special 
meaning category."""
#EMPTY = Char(None)
"""
Wrapper to apply fonction #getCategory on the object passed in parameter.
"""
def getCategory(value):
    return value.getCategory()
WORDS = [DIGITS, LOWER_CASE_LETTERS, UPPER_CASE_LETTERS, OTHER_WORDS]
CATEGORY_WORDS = map(getCategory, WORDS)
CATEGORY_HAVE_CLASS =  map(getCategory, WORDS + [SPACES])

"""
>>> DIGITS.getCategory() in CATEGORY_HAVE_CLASS
True
>>> LOWER_CASE_LETTERS.getCategory() in CATEGORY_HAVE_CLASS
True
>>> UPPER_CASE_LETTERS.getCategory() in CATEGORY_HAVE_CLASS
True
>>> OTHER_WORDS.getCategory() in CATEGORY_HAVE_CLASS
True
>>> for char in [SPACES, OTHERS, SPECIALS]:
>>>     char.getCategory() in CATEGORY_HAVE_CLASS
True
True
True
"""

"""
Concatenation of two sequences
"strict"
Same thing for 'A', 'a' and '0'
[a-c] + d -> [a-d]
[a-c] + e -> [a-ce]
[a-c] + [b-g] -> [a-g]
[a-c] + [d-g] -> [a-g]
[a-c] + [e-g] -> [a-ce-g]
[a-c] + ? -> [a-c] | ?
( [a-c] | _ ) + ? -> [a-c] | _ | ?
replace full intervals 'a', 'A' and '1' by classes (@TODO)
"lax"
enlarge your intervals 'a', 'A' and '1' (use classes)
"""


class BaseSequence(object):
    """Base class for sequences used to group characters forming regular 
    expressions."""
    def __init__(self):
        logging.debug("Created an object of type '%s'", 
            self.__class__.__name__)
        self._contained = False
        self._force_parenthesis = False
        self._optional = False

    def setContained(self):
        """A sequence is contained if it is part of an interval ("[...]")."""
        self._contained = True

    def isLeaf(self):
        """A leaf is a sequence that does not have sub-sequences."""
        return True

    def getString(self, type = "strict"):
        """String representation of a sequence used to generate the regular 
        expression."""
        return ""

    def linearise(self):
        """Experimental fun."""
        return [self.getString()]

    def merge(self):
        """Order the stored elements in the sequence."""
        logging.debug("Do nothing to merge this kind of sequence.")

    def setOptional(self):
        """A sequence is optional if the cardinality can be 0."""
        self._optional = True

    def getIsOptional(self):
        """Return True if and only if the sequence is optional."""
        return self._optional

class Sequence(BaseSequence):
    """Extends `BaseSequence`. Leaf sequence that is used to contain 
    characters."""
    def __init__(self, char):
        """`char`: must be of type `Char`."""
        BaseSequence.__init__(self)
        logging.debug("Created an object of type '%s'", 
            self.__class__.__name__)
        self._chars = []
        """The characters contained in the sequence."""
        self._min = None
        """The character that has the lowest integer representation."""
        self._max = None
        """The character that has the highest integer representation."""
        self.appendChar(char)

    def isLeaf(self):
        """This kind of sequence is always a leaf."""
        return True

    def getLength(self):
        """Length of the interval covered by this sequence."""
        return (ord(self._max.getChar()) - ord(self._min.getChar()))

    def appendChar(self, char):
        """`char`: must be of type `Char`.
        Try to add a `char` to this sequence. It will fail if the resulting 
        list of characters would not be an interval anymore or if the 
        character is not of the same category as the sequence. A character can 
        be added more than once.
        Returns True if and only if the character has been added.
        >>> seq = Sequence(Char("t"))
        >>> seq.appendChar(Char("v"))
        False
        >>> seq.appendChar(Char("u"))
        True
        >>> seq.appendChar(Char("v"))
        True
        >>> seq.appendChar(Char("b"))
        False
        >>> seq.appendChar(Char("u"))
        True
        """
        appended = False
        if (None != self._min):
            if ((self._min.getCategory() == char.getCategory()) and
                ((ord(self._min.getChar()) - 2 < ord(char.getChar())) and 
                (ord(char.getChar()) < ord(self._max.getChar()) + 2))):
                if (self._min.getChar() > char.getChar()):
                    self._min = char
                if (self._max.getChar() < char.getChar()):
                    self._max = char
                self._chars.append(char)
                appended = True
        else:
            self._chars.append(char)
            self._min = char
            self._max = char
            appended = True
        return appended

    def getCategory(self):
        """
        The category of the sequence is the category of all the characters.
        >>> Sequence(Char("1")).getCategory() == DIGITS.getCategory()
        True
        >>> Sequence(Char("t")).getCategory() == \
                LOWER_CASE_LETTERS.getCategory()
        True
        >>> Sequence(Char("D")).getCategory() == \
                UPPER_CASE_LETTERS.getCategory()
        True
        >>> Sequence(Char("_")).getCategory() == OTHER_WORDS.getCategory()
        True
        >>> Sequence(Char("?")).getCategory() == SPECIALS.getCategory()
        True
        >>> Sequence(Char("-")).getCategory() == OTHERS.getCategory()
        True
        """
        return self._min.getCategory()

    def appendSequence(self, sequence):
        """Try to append all the characters of an other sequence to this one.
        The two sequences have to be of the same category and the resulting 
        character list must make an interval.
        Returns True if and only if the sequence has been added.
        >>> left = Sequence(Char("g"))
        >>> left.appendChar(Char("h"))
        True
        >>> left.appendChar(Char("i"))
        True
        >>> left.appendChar(Char("j"))
        True
        >>> right = Sequence(Char("e"))
        >>> right.appendChar(Char("d"))
        True
        >>> left.appendSequence(right)
        False
        >>> right.appendChar(Char("f"))
        True
        >>> left.appendSequence(right)
        True
        """
        appended = False

#        logging.debug("check if min -1 %s == other_max %s", 
#            ord(self._min.getChar()) - 1, ord(sequence._max.getChar()))
#        logging.debug("check if other_min -1 %s == max %s", 
#            ord(sequence._min.getChar()) - 1, ord(self._max.getChar()))
#        logging.debug("check if other_min %s is in [min_max] %s", 
#            sequence._min.getChar(), range(ord(self._min.getChar()), 
#                ord(self._max.getChar())))
#        logging.debug("check if other_max %s is in [min_max] %s", 
#            sequence._max.getChar(), range(ord(self._min.getChar()), 
#                ord(self._max.getChar())))
        # check if the intervals are not disjoint
        if (sequence.getCategory() == self.getCategory()):
            if ((ord(self._min.getChar()) - 1 == 
                    ord(sequence._max.getChar())) or 
                (ord(sequence._min.getChar()) - 1 == 
                    ord(self._max.getChar())) or
                (ord(sequence._min.getChar()) in range(
                    ord(self._min.getChar()), ord(self._max.getChar()))) or
                (ord(sequence._max.getChar()) in range(
                    ord(self._min.getChar()), ord(self._max.getChar())))):
                appended = True
                for char in sequence._chars:
                    self._chars.append(char)
                self._min = min(self._min, sequence._min)
                self._max = max(self._max, sequence._max)
        return appended

    def getString(self, type = "strict"):
        """The result depends on `type`.
        If `type` is "strict" the representation will be the exact interval
        (@TODO ? except if the whole class is covered for \d and \s).
        If `type` is "lax" the representation of the class will be used for 
                some characters :
                    - digit -> \d
                    - letter or '_' -> \w
                    - space -> \s        
        If the sequence is not contained and more than one character or 
        different from a class is returned brakets will be added unless the 
        sequence is part of a bigger interval."""
        use_brackets = False
        if (("lax" == type) and (self._max != self._min) and 
            (self.getCategory() in CATEGORY_HAVE_CLASS)):
            if (self.getCategory() == DIGITS.getCategory()):
                string = "\d"
            elif (self.getCategory() in CATEGORY_WORDS):
                string = "\w"
            elif (self.getCategory() == SPACES.getCategory()):
                string = "\s"
            else:
                raise Exception("Unexpected category: " + self.getCategory())
        else:
            if (self._max == self._min):
                string = self._max.getString()
            elif (ord(self._max.getChar()) - ord(self._min.getChar()) > 1):
                string = self._min.getString() + "-" + self._max.getString()
                use_brackets = True
            else:
                string = self._min.getString() + self._max.getString()
                use_brackets = True
        if ((not self._contained) and (use_brackets)):
            string = "[" + string + "]"
        return string

    def linearise(self):
        use_brackets = False
        if (self._max == self._min):
            list = [self._max.getString()]
        elif (ord(self._max.getChar()) - ord(self._min.getChar()) > 1):
            list = [self._min.getString() + "-" + self._max.getString()]
        else:
            list = [self._min.getString() + self._max.getString()]
        return list

    def getIsInterval(self):
        """A single character can not be called an interval.
        Returns True if and only if this sequence contains more than on 
        characters (not considering duplicates).
        >>> seq = Sequence(Char("g"))
        >>> seq.getIsInterval()
        False
        >>> seq.appendChar(Char("h"))
        True
        >>> seq.getIsInterval()
        True
        >>> seq.appendChar(Char("i"))
        True
        >>> seq.getIsInterval()
        True
        >>> seq = Sequence(Char("5"))
        >>> seq.getIsInterval()
        False
        >>> seq.appendChar(Char("5"))
        True
        >>> seq.getIsInterval()
        False
        >>> seq.appendChar(Char("4"))
        True
        >>> seq.getIsInterval()
        True
        """
        return (self._max != self._min)

class MultiSequence(BaseSequence):
    """Extends `BaseSequence`. A sequence that contains other sequences. It 
    can either contain only sequences of one category (`kind` == AND) or 
    sequences of any category (`kind` == OR). Those sequences may be refered 
    to as sub-sequences."""
    OR = "or"
    """A multisequence of this kind will accept all the categories of 
    sequences."""
    AND = "and"
    """A multisequence of this kind will only accept sequence of one category
    (given by the first one)."""
    def __init__(self, kind = OR):
        """`kind`: ("or" | "and")"""
        BaseSequence.__init__(self)
        logging.debug("Created an object of type '%s'", "MultiSequence")
        self._kind = kind
        self.__subInit()
    
    def __subInit(self):
        self._sequences = {}
        if (MultiSequence.OR == self._kind):
            self._sequences[DIGITS.getCategory()] = []
            self._sequences[LOWER_CASE_LETTERS.getCategory()] = []
            self._sequences[UPPER_CASE_LETTERS.getCategory()] = []
            self._sequences[OTHER_WORDS.getCategory()] = []
            self._sequences[SPACES.getCategory()] = []
            self._sequences[SPECIALS.getCategory()] = []
            self._sequences[OTHERS.getCategory()] = []

    def isLeaf(self):
        """Returns False as the purpose of a MultiSequence is to contain other 
        sequences."""
        return False

    def getCategory(self):
        """tentative ... not sure what it should return for `OR` kind."""
        if (MultiSequence.OR == self._kind):
            return None
        elif (MultiSequence.AND == self._kind):
            if (len(self._sequences) == 1):
                return None
            else:
                return self._sequences.keys()[0]
        else:
            raise Exception("Forbidden kind of sequence: '" + self._kind + "'")

    def appendSequence(self, sequence):
        """Appending a sequence can only fail in case the one it is added to 
        is of kind AND and both sequences are of different categories.
        There is no guarantee that a sub-sequence will be inserted at an 
        optimal place as it is only appended. To order the sub-sequences you
        need to call `merge`.
        Returns True if and only if the sequence has been added."""
#        if (EMPTY.getCategory() == sequence.getCategory()):
#            logging.error("We should not be here!")
#            self._optional = True
#            return False
        appended = False
        if (MultiSequence.OR == self._kind):
            if (sequence.isLeaf()):
                # you can only put leaves inside
                sequences = self._sequences[sequence.getCategory()]
                if (len(sequences) > 0):
                    for pivot in sequences:
                        if (pivot.appendSequence(sequence)):
                            appended = True
                            break
                    if (not appended):
                        sequences.append(sequence)
                        appended = True
                else:
                    sequences.append(sequence)
                    appended = True
        else:
            if (sequence.isLeaf()):
                if (len(self._sequences.keys()) == 0):
                    self._sequences.append(sequence)
                else:
                    if (self._sequences.has_key(sequence.getCategory()) and
                        self.sequences[sequence.getCategory()].\
                            appendSequence(sequence)):
                        # when 'AND' only put together sequences of the same 
                        # category
                        appended = True
        return appended

    def merge(self):
        """Not optimal way to try to merge the sub-sequences in case the gaps 
        between them have been filled (or more)."""
        old_sequences = self._sequences
        self.__subInit()
        for key in old_sequences.keys():
            for sequence in old_sequences[key]:
                self.appendSequence(sequence)

    def getString(self, type = "strict"):
        """This has only been implemented with OR kind in mind.
        The result depends on `type`.
        If `type` is "strict" the representation will be the exact interval
        (@TODO ? except if the whole class is covered for \d and \s).
        If `type` is "lax" the representation of the class will be used for 
        some characters :
            - digit -> \d
            - letter or '_' -> \w
            - space -> \s
        If more than one character or different from a class is returned 
        brakets will be added unless the sequence is part of a bigger 
        interval."""
        string = ""
        added_sequence = False
        logging.debug("Sequence.getString() [lax]")
        add_digits_class = False
        add_words_class = False
        add_spaces_class = False
        digits = ""
        words = ""
        spaces = ""
        others = ""
        added_digits = 0
        added_words = 0
        added_spaces = 0
        added_others = 0
        for key in self._sequences.keys():
            if (len(self._sequences[key]) > 0):
                processed = False
                if (((len(self._sequences[key]) > 1) or 
                    (self._sequences[key][0].getLength() > 1)) and 
                    ("lax" == type)):
                    if (key == DIGITS.getCategory()):
                        processed = True
                        add_digits_class = True
                    elif (key in CATEGORY_WORDS):
                        processed = True
                        add_words_class = True
                    elif (key == SPACES.getCategory()):
                        processed = True
                        add_spaces_class = True
                if (not processed):
                    for sequence in self._sequences[key]:
                        if (key == DIGITS.getCategory()):
                            added_digits += 1
                            digits += sequence.getString(type)
                        elif (key in CATEGORY_WORDS):
                            added_words += 1
                            words += sequence.getString(type)
                        elif (key == SPACES.getCategory()):
                            added_spaces += 1
                            spaces += sequence.getString(type)
                        else:
                            added_others += 1
                            others += sequence.getString(type)
        added_count = 0
        if (("lax" == type) and (add_digits_class)):
            added_count += 1
            string += "\d"
        else:
            added_count += added_digits
            string += digits
        if (("lax" == type) and (add_words_class)):
            added_count += 1
            string += "\w"
        else:
            added_count += added_words
            string += words
        if (("lax" == type) and (add_spaces_class)):
            added_count += 1
            string += "\s"
        else:
            added_count += added_spaces
            string += spaces
        added_count += added_others
        string += others
        if (added_count > 1):
            string = "[" + string + "]"
        return string

    def linearise(self):
        list = []
        added_sequence = False
        use_parenthesis = False
        for key in self._sequences.keys():
            sub_list = []
            added = False
            use_brackets = False
            for sequence in self._sequences[key]:
                sub_list.append(sequence.linearise())
                added = True 
            if (added):
                list.append(sub_list)
        return list

class SequenceFactory(object):
    """Factory to create sequences."""
    def __init__(self, type = "strict"):
        logging.debug("Created an object of type '%s'", "SequenceFactory")
        self._type = type

    def createSequence(self, char):
        """Creates a sequence containing the character `char`."""
        return Sequence(Char(char, self._type))

    def addSequences(self, left, right):
        """Try to append `right` to `left`. If it fails than create a new 
        sequence containing both."""
        if (left.appendSequence(right)):
            right.setContained()
            return left
        else:
            sequence = MultiSequence()
            left.setContained()
            right.setContained()
            sequence.appendSequence(left)
            sequence.appendSequence(right)
            return sequence

class Node:
    """A node stands for a final character in the generated regular expression 
    (for now). It is responsible for building the appropriate sequences using 
    a `SequenceFactory`.
    """
    def __init__(self, characters, iType):
        """characters : the characters the node will have to match.
        iType : ("strict" | "lax")"""
        self._len = len(characters)
        self._range = characters
        characters = list(set(characters))
        characters.sort()
        if ((len(self._range) > 1) and (len(characters) == 1)):
            iType = "strict"
        logging.debug('characters = ' + str(characters))
        self._root_sequence = None
        factory = SequenceFactory("strict")
        for char in characters:
            new_sequence = factory.createSequence(char)
            if (None == self._root_sequence):
                self._root_sequence = new_sequence
            else:
                self._root_sequence = factory.addSequences(
                    self._root_sequence, new_sequence)
        # make sure that the number of intervals is minimal
        self._root_sequence.merge()

    def setOptional(self):
        """Force this node to consider that the list of provided characters 
        was not complete and thus that this node may represent the absence of 
        a character."""
        self._root_sequence.setOptional()

    def getIsOptional(self):
        """Return True if and only if the node does not necessarily contain 
        a character."""
        return self._root_sequence.getIsOptional()

    def getLength(self):
        """Maybe the nale is not appropriate.
        Returns the number of characters provided to the constructor."""
        return self._len

    def getString(self, type = "strict"):
        """Returns the mini regular expression coding for this character 
        without considering the possibility that it is optional."""
        return self._root_sequence.getString(type)

def generate(sample_strings, iType = "lax"):
    """`sample_strings`: list of strings for which to generate a matching 
    regexp. It does not need to be ordered.
    Returns a regular expression that matches the sample strings. The 
    regular expression is checked against the strings at the end.
    An error is logged if the regular expression does not match one of the 
    provided string."""
    intervals = []
    # compute the length of the long_listuest and shortest strings
    all_lengths = map(len, sample_strings)
    max_length = max(all_lengths)
    min_length = min(all_lengths)
    logging.debug("max_length = " + str(max_length))
    logging.debug("min_length = " + str(min_length))
    for i in range(max_length):
        intervals.append([])
    for string in sample_strings:
        i = 0
        for char in string:
            intervals[i].append(char)
            i += 1
    logging.debug(str(intervals))
    nodes = []
    i = 0
    for interval in intervals:
        i += 1
        # the trick is to force the node in strict mode not to lose any 
        # information early in the process it will still be time later to 
        # adapt the result given by the nodes.
        node = Node(interval, "strict")
        if (i > min_length):
            # we have gone further than what the shortest string could reach 
            # so any node after this point may contain no character.
            node.setOptional()
        nodes.append(node)

    ref_node = None
    # number of consecutive nodes matching the same characters.
    count = 0
    # number of consecutive nodes matching the same characters that contain 
    # one character (non optional nodes).
    left = None
    # Here it is! The result regular expression.
    result = ""
    # the job of this not too self explanatory loop is to group consecutive 
    # nodes that match exaclty the same characters.
    for node in nodes:
        logging.debug("node.getString(iType) = %s", node.getString(iType))
        logging.debug("node.getLength() = %i", node.getLength())        
        if (None != ref_node):
            if (ref_node.getString(iType) == node.getString(iType)):
                if (not node.getIsOptional()):
                    left += 1
                count += 1
            else:
                result += ref_node.getString(iType)
                if (count > 1):
                    if ((left == count)):
                        logging.debug("{%i}", count)
                        result += "{" + str(count) + "}"
                    else:
                        logging.debug("{%i-%i}", left, count)
                        result += "{" + str(left) + "," + str(count) + "}"
                elif (ref_node.getIsOptional()):
                    result += "?"
                ref_node = node
                logging.debug("next ref_node")
                logging.debug("ref_node.getString(iType) = %s", 
                    ref_node.getString(iType))
                logging.debug("ref_node.getLength() = %i", 
                    ref_node.getLength())
                count = 1
                if (ref_node.getIsOptional()):
                    left = 0
                else:
                    left = 1
        else:
            logging.debug("create ref_node")
            ref_node = node
            count = 1
            if (ref_node.getIsOptional()):
                left = 0
            else:
                left = 1
            logging.debug("ref_node.getString(iType) = %s", 
                ref_node.getString(iType))
            logging.debug("ref_node.getLength() = %i", ref_node.getLength())
    if (None != ref_node):
        result += ref_node.getString(iType)
        if (count > 1):
            if ((left == count)):
                logging.debug("{%i}", count)
                result += "{" + str(count) + "}"
            else:
                logging.debug("{%i-%i}", left, count)
                result += "{" + str(left) + "," + str(count) + "}"
        elif (ref_node.getIsOptional()):
            result += "?"
    def getString(value):
        return value.getString()
    logging.debug(map(getString, nodes))
    import re
    logging.debug("result = " + result)
    # now check that the regular expression matches all the sample strings
    # (which is a bare minimum)
    matcher = re.compile(result)
    for string in sample_strings:
        if (None == matcher.match(string)):
            logging.error("Error: '" + result + "' does not match '" + 
                string + "'")
    return result

###############################################################################
#                                                                             #
#                           Ugly tests part follows                           #
#                                                                             #
###############################################################################

def checkEqual(expected, gotten):
    """`expected`: string containing the expected result.
    `gotten`: string containing what has realy been computed.
    Logs "OK" if `expected` and `gotten` are equal, and an error message 
    otherwise."""
    if (expected != gotten):
        logging.error("Error: expected '" + str(expected) + "' but found '" + 
            str(gotten) + "'")
    else:
        logging.info("OK")

def test_generate(data, type, expected = None):
    """`data`: list of strings used to generate the regular expression.
    `type`: "strict" | "lax"
    `expected`: if provided, string containing the expected regular expression.
    """
    exp = generate(data, type)
    logging.info(str(data) +  " -> " + exp)
    if (None != expected):
        checkEqual(expected, exp)

test_generate([ "5", "2" ], "lax", "\d")
test_generate([ "A", "2" ], "lax", "[2A]")
test_generate([ "A", "2" ], "strict", "[2A]")
test_generate([ "Le petit chat dort.", "11/02/2004" ], "strict", 
    "[1L][1e][ /][0p][2e][t/][2i][0t][0 ][4c]h?a?t? ?d?o?r?t?\.?")
test_generate([ "Le petit chat dort.", "11/02/2004" ], "lax", 
    "[1L][1e][ /][0p][2e][t/][2i][0t][0 ][4c]h?a?t? ?d?o?r?t?\.?")
test_generate([ "AAAA", "11" ], "lax", "[1A]{2}A{0,2}")
test_generate([ "1 2 3", "abcdefg" ], "lax", "[1a][b ][2c][d ][3e]f?g?")
test_generate([ "   ", "1/2" ], "lax", "[1 ][ /][2 ]")
test_generate([ " ", "/" ], "lax", "[ /]")
test_generate([ "1", "12" ], "lax", "12?")
test_generate([ " ", "  " ], "lax", " {1,2}")
test_generate([ "1", "11" ], "lax", "1{1,2}")
test_generate([ "1", "11", "234", "999 " ], "lax", "\d{1,3} ?")

test_generate([ "j", "N", "Z", "t" ], "lax", "\w")
test_generate([ "x", "J", "B", "H" ], "lax", "\w")
test_generate([ "2", "c", "y" ], "strict", "[2cy]")

def getRandomString(desired_length):
    import string
    import random
    import sre_parse
    return "".join([random.choice(string.letters + string.digits + 
            string.punctuation + sre_parse.CATEGORY_SPACE) 
        for x in range(0, desired_length)]) 

def getRandomStringLight(desired_length):
    import string
    import random
    import sre_parse
    return "".join([random.choice(string.letters + string.digits + "[]-?+*" + 
            sre_parse.CATEGORY_SPACE) 
        for x in range(0, desired_length)]) 

r1 = [getRandomString(12), getRandomString(12), 
    getRandomString(12), getRandomString(12)]
r2 = [getRandomString(12), getRandomString(11), 
    getRandomString(10), getRandomString(9)]
r3 = [getRandomString(40), getRandomString(40), getRandomString(40), 
    getRandomString(40), getRandomString(40), getRandomString(40)]
test_generate(r1, "lax")
test_generate(r1, "strict")
test_generate(r2, "lax")
test_generate(r2, "strict")
test_generate(r3, "lax")
test_generate(r3, "strict")

test_generate(
    ['L13|KgRZ?iK', '2*mu`/pdoyF', '{5RRg3J|L*1', 'hxEl^V!@1fY'], "lax")
test_generate(
    ['L13|KgRZ?iK', '2*mu`/pdoyF', '{5RRg3J|L*1', 'hxEl^V!@1fY'], "strict")
test_generate(
    ['^L-p0]cft(&', '0IFrP%xp$M', ')`yg%!5F+', 'z0ho)L{*'], "lax")
test_generate(
    ['^L-p0]cft(&', '0IFrP%xp$M', ')`yg%!5F+', 'z0ho)L{*'], "strict")
long_list = []
for i in range(25):
    long_list.append(getRandomStringLight(3))
logging.info("test_generate: long_list")
test_generate(long_list, "lax")
test_generate(long_list, "strict")


test_generate(['c6cG]NHp7', 'Epx5acgex', 'tGe8+HjSY', 'y0plbKtsO', 
    'BXYo+2Qwe', 'atKrnM?Iy', '2Xo]Yw5w5', '5LxOy*yfs', 'drt9DHm[Q', 
    'yonZGT?Sx', 'wwt-pcdlH', 'ok1Fdh97J', '[VIhgFga[', 'BKsYDQOEa', 
    'LJmcz9c2_', 'XK*Lyw-ry', 'C1dAte1L3', 'usTHKf4yy', '7lO20QOWY', 
    'aJ6Ytcccm', 'a2+8GV627', 'xlX?a[k+c', 'ZaocQm20z', 'WyRRBcVyc', 
    'Myrat]AeQ', 'xpVjq6PPV', 'HZcou_7+f', 'zCdsoaByp', 'cbV5?vUFj', 
    ']8e]aV6AB', 'rBae2rcNN', 'EZdcaeYgM', 'YppByMesA', 'L7F*mh9bw', 
    '5l4I[ceX4', '0sTgV]myM', 'dczeSGz0X', 'IeWMkszba', 'RD55AOyOb', 
    '7cuJhTSOL', '6vEtConwR', 'BhD?LncF1', 'vD]SEEcj+', 'jjypAfece', 
    'JAa7znpd0', 'VJE?pKH?O', '*RoZsQPte', '1tVcftDAV', 'VI**riyLP', 
    'vl*hee2r5'], "strict", 
"[0-25-7acdjort-zBCEH-JLMRV-Z\]\*\[][0-26-8a-cehj-lopr-tvwyA-DGI-LRVXZ][14-6ac\
-em-pr-ux-zD-FIKORTV-Y\]\*\+][257-9aceghjlopr-tABF-JLMORSYZ\-\]\*\?][02abd-hkm\
-uyzA-EGKLQSVY\]\+\?\[][269acefhim-or-tvw_E-HKM-OQTV\]\*\[][124-79c-egjkmnptyz\
ABDHO-QSUVY\-\?][027a-gjlpr-twyAEFILN-PSWX\+\?\[][013-57a-cefjmpsw-z_ABHJL-RVX\
Y\+\[]")


big = ["bigLogXXX_100821_003795.tar.gz",
    "bigLogXXX_100821_015795.tar.gz",
    "bigLogXXX_100821_021795.tar.gz",
    "bigLogXXX_100821_033795.tar.gz",
    "bigLogXXX_100821_046795.tar.gz",
    "bigLogXXX_100821_057795.tar.gz",
    "bigLogXXX_100821_068923.tar.gz",
    "bigLogXXX_100821_072345.tar.gz",
    "bigLogXXX_100821_086495.tar.gz",
    "bigLogXXX_100821_093795.tar.gz",
    "bigLogXXX_100821_107795.tar.gz",
    "bigLogXXX_100821_118923.tar.gz",
    "bigLogXXX_100821_122345.tar.gz",
    "bigLogXXX_100821_136495.tar.gz",
    "bigLogXXX_100821_143795.tar.gz",
    "bigLogXXX_100821_158923.tar.gz",
    "bigLogXXX_100821_162345.tar.gz",
    "bigLogXXX_100821_176495.tar.gz",
    "bigLogXXX_100821_183795.tar.gz",
    "bigLogXXX_100821_198923.tar.gz",
    "bigLogXXX_100821_202345.tar.gz",
    "bigLogXXX_100821_216495.tar.gz",
    "bigLogXXX_100821_223795.tar.gz",
    "bigLogXXX_100821_236495.tar.gz",

    "bigLogXXX_100821_004795.tar.gz",
    "bigLogXXX_100821_016795.tar.gz",
    "bigLogXXX_100821_022795.tar.gz",
    "bigLogXXX_100821_034795.tar.gz",
    "bigLogXXX_100821_047795.tar.gz",
    "bigLogXXX_100821_058795.tar.gz",
    "bigLogXXX_100821_069923.tar.gz",
    "bigLogXXX_100821_073345.tar.gz",
    "bigLogXXX_100821_087495.tar.gz",
    "bigLogXXX_100821_094795.tar.gz",
    "bigLogXXX_100821_108795.tar.gz",
    "bigLogXXX_100821_119923.tar.gz",
    "bigLogXXX_100821_123345.tar.gz",
    "bigLogXXX_100821_137495.tar.gz",
    "bigLogXXX_100821_144795.tar.gz",
    "bigLogXXX_100821_159923.tar.gz",
    "bigLogXXX_100821_163345.tar.gz",
    "bigLogXXX_100821_177495.tar.gz",
    "bigLogXXX_100821_184795.tar.gz",
    "bigLogXXX_100821_199923.tar.gz",
    "bigLogXXX_100821_203345.tar.gz",
    "bigLogXXX_100821_217495.tar.gz",
    "bigLogXXX_100821_224795.tar.gz",
    "bigLogXXX_100821_237495.tar.gz",

    "bigLogXXX_100820_003795.tar.gz",
    "bigLogXXX_100820_015795.tar.gz",
    "bigLogXXX_100820_021795.tar.gz",
    "bigLogXXX_100820_033795.tar.gz",
    "bigLogXXX_100820_046795.tar.gz",
    "bigLogXXX_100820_057795.tar.gz",
    "bigLogXXX_100820_068923.tar.gz",
    "bigLogXXX_100820_072345.tar.gz",
    "bigLogXXX_100820_086495.tar.gz",
    "bigLogXXX_100820_093795.tar.gz",
    "bigLogXXX_100820_107795.tar.gz",
    "bigLogXXX_100820_118923.tar.gz",
    "bigLogXXX_100820_122345.tar.gz",
    "bigLogXXX_100820_136495.tar.gz",
    "bigLogXXX_100820_143795.tar.gz",
    "bigLogXXX_100820_158923.tar.gz",
    "bigLogXXX_100820_162345.tar.gz",
    "bigLogXXX_100820_176495.tar.gz",
    "bigLogXXX_100820_183795.tar.gz",
    "bigLogXXX_100820_198923.tar.gz",
    "bigLogXXX_100820_202345.tar.gz",
    "bigLogXXX_100820_216495.tar.gz",
    "bigLogXXX_100820_223795.tar.gz",
    "bigLogXXX_100820_236495.tar.gz",

    "bigLogXXX_100820_004795.tar.gz",
    "bigLogXXX_100820_016795.tar.gz",
    "bigLogXXX_100820_022795.tar.gz",
    "bigLogXXX_100820_034795.tar.gz",
    "bigLogXXX_100820_047795.tar.gz",
    "bigLogXXX_100820_058795.tar.gz",
    "bigLogXXX_100820_069923.tar.gz",
    "bigLogXXX_100820_073345.tar.gz",
    "bigLogXXX_100820_087495.tar.gz",
    "bigLogXXX_100820_094795.tar.gz",
    "bigLogXXX_100820_108795.tar.gz",
    "bigLogXXX_100820_119923.tar.gz",
    "bigLogXXX_100820_123345.tar.gz",
    "bigLogXXX_100820_137495.tar.gz",
    "bigLogXXX_100820_144795.tar.gz",
    "bigLogXXX_100820_159923.tar.gz",
    "bigLogXXX_100820_163345.tar.gz",
    "bigLogXXX_100820_177495.tar.gz",
    "bigLogXXX_100820_184795.tar.gz",
    "bigLogXXX_100820_199923.tar.gz",
    "bigLogXXX_100820_203345.tar.gz",
    "bigLogXXX_100820_217495.tar.gz",
    "bigLogXXX_100820_224795.tar.gz",
    "bigLogXXX_100820_237495.tar.gz"]


test_generate(["1", "2"], "strict", "[12]")
test_generate(["1", "a"], "strict", "[1a]")
test_generate(["112", "abc"], "strict", "[1a][1b][2c]")
test_generate(["1", "3", "2", "5", "4"], "strict", "[1-5]")
test_generate(["5289", "ecum", "dy"], "strict", "[5de][2cy][8u]?[9m]?")
test_generate(big, "lax", "bigLogX{3}_10{2}82\d_\d{6}\.tar\.gz")
test_generate(big, "strict", 
    "bigLogX{3}_10{2}82[01]_[0-2][0-9][1-9][3479][249][35]\.tar\.gz")

small = ["123", "124", "125", "128", "134"]
test_generate(small, "lax", "1\d{2}")
test_generate(["3", "4"], "lax", "\d")
test_generate(["5", "4"], "lax", "\d")
test_generate(["5", "2"], "lax", "\d")
