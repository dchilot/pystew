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

_CONSOLE = logging.StreamHandler(sys.stdout)
_CONSOLE.setLevel(logging.INFO)
logging.getLogger('').addHandler(_CONSOLE)

def escape_char(char):
    """`char`: character to escape if needed.
    Returns a character so that it can be inserted in a regular expression, 
    escaping it if needed."""
    import sre_parse
    if (None == char):
        return ''
    if ((char in sre_parse.SPECIAL_CHARS) or ("-" == char) or ("]" == char)):
        return "\\" + char
    return char

class Char:
    """
    >>> Char('a').get_category()
    'LOWER_CASE_LETTER'
    >>> Char('G').get_category()
    'UPPER_CASE_LETTER'
    >>> Char(' ').get_category()
    'category_space'
    >>> Char('\\t').get_category()
    'category_space'
    >>> Char('?').get_category()
    'SPECIAL'
    >>> Char('_').get_category()
    'OTHER_WORD'
    >>> Char(None).get_category()
    'NONE'
    >>> (Char('4').get_category() == Char('7').get_category())
    True
    >>> (Char('A').get_category() == Char('G').get_category())
    True
    >>> (Char('f').get_category() == Char('i').get_category())
    True
    >>> (Char('+').get_category() == Char('?').get_category())
    True
    >>> (Char('-').get_category() == Char('~').get_category())
    True
    >>> # '_' is in its own category ('OTHER_WORD')
    >>> (Char('_').get_category() != Char('\').get_category())
    True
    """

    SPECIAL = 'SPECIAL'
    UNKNOWN = 'UNKNOWN'
    LOWER_CASE_LETTER = 'LOWER_CASE_LETTER'
    UPPER_CASE_LETTER = 'UPPER_CASE_LETTER'
    OTHER_WORD = 'OTHER_WORD'
    NONE = 'NONE'

    def __init__(self, char, regexp_type = "strict"):
        import sre_parse
        from sre_parse import SPECIAL_CHARS, CATEGORY_DIGIT
        from sre_parse import WHITESPACE, CATEGORY_SPACE

        self._regexp_type = regexp_type

        if (None == char):
            self._category = Char.NONE
        elif ('_' == char):
            self._category = Char.OTHER_WORD
        elif (char in sre_parse.DIGITS):
            self._category = CATEGORY_DIGIT
        elif (char in SPECIAL_CHARS):
            self._category = Char.SPECIAL
        elif (char in WHITESPACE):
            self._category = CATEGORY_SPACE
        elif (char.isalpha()):
            if (char.islower()):
                self._category = Char.LOWER_CASE_LETTER
            else:
                self._category = Char.UPPER_CASE_LETTER
        else:
            self._category = Char.UNKNOWN
        self._char = char
        logging.debug("char = " + str(char))
        logging.debug("self._category = " + self._category)

    def get_all_categories():
        """Returns all the possible categories for a character."""
        from sre_parse import CATEGORY_DIGIT
        from sre_parse import CATEGORY_SPACE
        return [CATEGORY_DIGIT, Char.SPECIAL, CATEGORY_SPACE, 
            Char.LOWER_CASE_LETTER, Char.UPPER_CASE_LETTER, 
            Char.UNKNOWN]

    def get_category(self):
        """Returns the category of this character."""
        return self._category

    def get_char(self):
        """Returns the wrapped character."""
        return self._char

    def get_string(self):
        """Returns a representation of the character that can be includede in 
        a regular expression."""
        return escape_char(self._char)

    def get_is_ordered(self):
        """Returns True if and only if the character is a digit or a letter
        (which are ordered)."""
        from sre_parse import CATEGORY_DIGIT
        return (self._category in [CATEGORY_DIGIT, 
            Char.LOWER_CASE_LETTER, Char.UPPER_CASE_LETTER])

    def __eq__(self, other_char):
        if (None == other_char):
            return False
        return (self._char == other_char.get_char())

    def __ne__(self, other_char):
        if (None == other_char):
            return True
        return (self._char != other_char.get_char())

    def __lt__(self, other_char):
        if (None == other_char):
            return True
        return (self._char < other_char.get_char())

    def __gt__(self, other_char):
        if (None == other_char):
            return False
        return (self._char > other_char.get_char())

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

def get_category(value):
    """Wrapper to apply fonction #get_category on the object passed in 
    parameter."""
    return value.get_category()
WORDS = [DIGITS, LOWER_CASE_LETTERS, UPPER_CASE_LETTERS, OTHER_WORDS]
CATEGORY_WORDS = map(get_category, WORDS)
CATEGORY_HAVE_CLASS =  map(get_category, WORDS + [SPACES])

"""
>>> DIGITS.get_category() in CATEGORY_HAVE_CLASS
True
>>> LOWER_CASE_LETTERS.get_category() in CATEGORY_HAVE_CLASS
True
>>> UPPER_CASE_LETTERS.get_category() in CATEGORY_HAVE_CLASS
True
>>> OTHER_WORDS.get_category() in CATEGORY_HAVE_CLASS
True
>>> for char in [SPACES, OTHERS, SPECIALS]:
>>>     char.get_category() in CATEGORY_HAVE_CLASS
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

    def set_contained(self):
        """A sequence is contained if it is part of an interval ("[...]")."""
        self._contained = True

    def is_leaf(self):
        """A leaf is a sequence that does not have sub-sequences."""
        return True

    def get_string(self, regexp_type = "strict"):
        """String representation of a sequence used to generate the regular 
        expression."""
        return ""

    def linearise(self):
        """Experimental fun."""
        return [self.get_string()]

    def merge(self):
        """Order the stored elements in the sequence."""
        logging.debug("Do nothing to merge this kind of sequence.")

    def set_optional(self):
        """A sequence is optional if the cardinality can be 0."""
        self._optional = True

    def get_is_optional(self):
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
        self.append_char(char)

    def is_leaf(self):
        """This kind of sequence is always a leaf."""
        return True

    def get_length(self):
        """Length of the interval covered by this sequence."""
        return (ord(self._max.get_char()) - ord(self._min.get_char()))

    def append_char(self, char):
        """`char`: must be of type `Char`.
        Try to add a `char` to this sequence. It will fail if the resulting 
        list of characters would not be an interval anymore or if the 
        character is not of the same category as the sequence. A character can 
        be added more than once.
        Returns True if and only if the character has been added.
        >>> seq = Sequence(Char("t"))
        >>> seq.append_char(Char("v"))
        False
        >>> seq.append_char(Char("u"))
        True
        >>> seq.append_char(Char("v"))
        True
        >>> seq.append_char(Char("b"))
        False
        >>> seq.append_char(Char("u"))
        True
        """
        appended = False
        if (None != self._min):
            if ((self._min.get_category() == char.get_category()) and
                ((ord(self._min.get_char()) - 2 < ord(char.get_char())) and 
                (ord(char.get_char()) < ord(self._max.get_char()) + 2))):
                if (self._min.get_char() > char.get_char()):
                    self._min = char
                if (self._max.get_char() < char.get_char()):
                    self._max = char
                self._chars.append(char)
                appended = True
        else:
            self._chars.append(char)
            self._min = char
            self._max = char
            appended = True
        return appended

    def get_category(self):
        """The category of the sequence is the category of all the characters.
        >>> Sequence(Char("1")).get_category() == DIGITS.get_category()
        True
        >>> Sequence(Char("t")).get_category() == \
                LOWER_CASE_LETTERS.get_category()
        True
        >>> Sequence(Char("D")).get_category() == \
                UPPER_CASE_LETTERS.get_category()
        True
        >>> Sequence(Char("_")).get_category() == OTHER_WORDS.get_category()
        True
        >>> Sequence(Char("?")).get_category() == SPECIALS.get_category()
        True
        >>> Sequence(Char("-")).get_category() == OTHERS.get_category()
        True
        """
        return self._min.get_category()

    def append_sequence(self, sequence):
        """Try to append all the characters of an other sequence to this one.
        The two sequences have to be of the same category and the resulting 
        character list must make an interval.
        Returns True if and only if the sequence has been added.
        >>> left = Sequence(Char("g"))
        >>> left.append_char(Char("h"))
        True
        >>> left.append_char(Char("i"))
        True
        >>> left.append_char(Char("j"))
        True
        >>> right = Sequence(Char("e"))
        >>> right.append_char(Char("d"))
        True
        >>> left.append_sequence(right)
        False
        >>> right.append_char(Char("f"))
        True
        >>> left.append_sequence(right)
        True
        """
        appended = False

#        logging.debug("check if min -1 %s == other_max %s", 
#            ord(self._min.get_char()) - 1, ord(sequence._max.get_char()))
#        logging.debug("check if other_min -1 %s == max %s", 
#            ord(sequence._min.get_char()) - 1, ord(self._max.get_char()))
#        logging.debug("check if other_min %s is in [min_max] %s", 
#            sequence._min.get_char(), range(ord(self._min.get_char()), 
#                ord(self._max.get_char())))
#        logging.debug("check if other_max %s is in [min_max] %s", 
#            sequence._max.get_char(), range(ord(self._min.get_char()), 
#                ord(self._max.get_char())))
        # check if the intervals are not disjoint
        if (sequence.get_category() == self.get_category()):
            if ((ord(self._min.get_char()) - 1 == 
                    ord(sequence._max.get_char())) or 
                (ord(sequence._min.get_char()) - 1 == 
                    ord(self._max.get_char())) or
                (ord(sequence._min.get_char()) in range(
                    ord(self._min.get_char()), ord(self._max.get_char()))) or
                (ord(sequence._max.get_char()) in range(
                    ord(self._min.get_char()), ord(self._max.get_char())))):
                appended = True
                for char in sequence._chars:
                    self._chars.append(char)
                self._min = min(self._min, sequence._min)
                self._max = max(self._max, sequence._max)
        return appended

    def get_string(self, regexp_type = "strict"):
        """The result depends on `regexp_type`.
        If `regexp_type` is "strict" the representation will be the exact 
        interval(@TODO ? except if the whole class is covered for \d and \s).
        If `regexp_type` is "lax" the representation of the class will be used
        for some characters :
            - digit -> \d
            - letter or '_' -> \w
            - space -> \s        
        If the sequence is not contained and more than one character or 
        different from a class is returned brakets will be added unless the 
        sequence is part of a bigger interval."""
        use_brackets = False
        if (("lax" == regexp_type) and (self._max != self._min) and 
            (self.get_category() in CATEGORY_HAVE_CLASS)):
            if (self.get_category() == DIGITS.get_category()):
                string = "\d"
            elif (self.get_category() in CATEGORY_WORDS):
                string = "\w"
            elif (self.get_category() == SPACES.get_category()):
                string = "\s"
            else:
                raise Exception("Unexpected category: " + self.get_category())
        else:
            if (self._max == self._min):
                string = self._max.get_string()
            elif (ord(self._max.get_char()) - ord(self._min.get_char()) > 1):
                string = self._min.get_string() + "-" + self._max.get_string()
                use_brackets = True
            else:
                string = self._min.get_string() + self._max.get_string()
                use_brackets = True
        if ((not self._contained) and (use_brackets)):
            string = "[" + string + "]"
        return string

    def linearise(self):
        if (self._max == self._min):
            lin = [self._max.get_string()]
        elif (ord(self._max.get_char()) - ord(self._min.get_char()) > 1):
            lin = [self._min.get_string() + "-" + self._max.get_string()]
        else:
            lin = [self._min.get_string() + self._max.get_string()]
        return lin

    def get_is_interval(self):
        """A single character can not be called an interval.
        Returns True if and only if this sequence contains more than on 
        characters (not considering duplicates).
        >>> seq = Sequence(Char("g"))
        >>> seq.get_is_interval()
        False
        >>> seq.append_char(Char("h"))
        True
        >>> seq.get_is_interval()
        True
        >>> seq.append_char(Char("i"))
        True
        >>> seq.get_is_interval()
        True
        >>> seq = Sequence(Char("5"))
        >>> seq.get_is_interval()
        False
        >>> seq.append_char(Char("5"))
        True
        >>> seq.get_is_interval()
        False
        >>> seq.append_char(Char("4"))
        True
        >>> seq.get_is_interval()
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
        self._sequences = {}
        self.__sub_init()
    
    def __sub_init(self):
        """Prepares the content of `_sequences`."""
        self._sequences = {}
        if (MultiSequence.OR == self._kind):
            self._sequences[DIGITS.get_category()] = []
            self._sequences[LOWER_CASE_LETTERS.get_category()] = []
            self._sequences[UPPER_CASE_LETTERS.get_category()] = []
            self._sequences[OTHER_WORDS.get_category()] = []
            self._sequences[SPACES.get_category()] = []
            self._sequences[SPECIALS.get_category()] = []
            self._sequences[OTHERS.get_category()] = []

    def is_leaf(self):
        """Returns False as the purpose of a MultiSequence is to contain other 
        sequences."""
        return False

    def get_category(self):
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

    def append_sequence(self, sequence):
        """Appending a sequence can only fail in case the one it is added to 
        is of kind AND and both sequences are of different categories.
        There is no guarantee that a sub-sequence will be inserted at an 
        optimal place as it is only appended. To order the sub-sequences you
        need to call `merge`.
        Returns True if and only if the sequence has been added."""
#        if (EMPTY.get_category() == sequence.get_category()):
#            logging.error("We should not be here!")
#            self._optional = True
#            return False
        appended = False
        if (MultiSequence.OR == self._kind):
            if (sequence.is_leaf()):
                # you can only put leaves inside
                sequences = self._sequences[sequence.get_category()]
                if (len(sequences) > 0):
                    for pivot in sequences:
                        if (pivot.append_sequence(sequence)):
                            appended = True
                            break
                    if (not appended):
                        sequences.append(sequence)
                        appended = True
                else:
                    sequences.append(sequence)
                    appended = True
        else:
            if (sequence.is_leaf()):
                if (len(self._sequences.keys()) == 0):
                    self._sequences[sequence.get_category()] = []
                    self._sequences[sequence.get_category()].append(sequence)
                else:
                    if (self._sequences.has_key(sequence.get_category())):
                        # when 'AND' only put together sequences of the same 
                        # category
                        for pivot in self._sequences[sequence.get_category()]:
                            appended |= pivot.append_sequence(sequence)
        return appended

    def merge(self):
        """Not optimal way to try to merge the sub-sequences in case the gaps 
        between them have been filled (or more)."""
        old_sequences = self._sequences
        self.__sub_init()
        for key in old_sequences.keys():
            for sequence in old_sequences[key]:
                self.append_sequence(sequence)

    def get_string(self, regexp_type = "strict"):
        """This has only been implemented with OR kind in mind.
        The result depends on `regexp_type`.
        If `regexp_type` is "strict" the representation will be the exact 
        interval(@TODO ? except if the whole class is covered for \d and \s).
        If `regexp_type` is "lax" the representation of the class will be used 
        for some characters :
            - digit -> \d
            - letter or '_' -> \w
            - space -> \s
        If more than one character or different from a class is returned 
        brakets will be added unless the sequence is part of a bigger 
        interval."""
        string = ""
        logging.debug("Sequence.get_string() [lax]")
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
                    (self._sequences[key][0].get_length() > 1)) and 
                    ("lax" == regexp_type)):
                    if (key == DIGITS.get_category()):
                        processed = True
                        add_digits_class = True
                    elif (key in CATEGORY_WORDS):
                        processed = True
                        add_words_class = True
                    elif (key == SPACES.get_category()):
                        processed = True
                        add_spaces_class = True
                if (not processed):
                    for sequence in self._sequences[key]:
                        if (key == DIGITS.get_category()):
                            added_digits += 1
                            digits += sequence.get_string(regexp_type)
                        elif (key in CATEGORY_WORDS):
                            added_words += 1
                            words += sequence.get_string(regexp_type)
                        elif (key == SPACES.get_category()):
                            added_spaces += 1
                            spaces += sequence.get_string(regexp_type)
                        else:
                            added_others += 1
                            others += sequence.get_string(regexp_type)
        added_count = 0
        if (("lax" == regexp_type) and (add_digits_class)):
            added_count += 1
            string += "\d"
        else:
            added_count += added_digits
            string += digits
        if (("lax" == regexp_type) and (add_words_class)):
            added_count += 1
            string += "\w"
        else:
            added_count += added_words
            string += words
        if (("lax" == regexp_type) and (add_spaces_class)):
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
        lin = []
        for key in self._sequences.keys():
            sub_list = []
            added = False
            for sequence in self._sequences[key]:
                sub_list.append(sequence.linearise())
                added = True 
            if (added):
                lin.append(sub_list)
        return lin

class SequenceFactory(object):
    """Factory to create sequences."""
    def __init__(self, regexp_type = "strict"):
        logging.debug("Created an object of regexp_type '%s'", 
            "SequenceFactory")
        self._regexp_type = regexp_type

    def create_sequence(self, char):
        """Creates a sequence containing the character `char`."""
        return Sequence(Char(char, self._regexp_type))

    def add_sequences(self, left, right):
        """Try to append `right` to `left`. If it fails than create a new 
        sequence containing both."""
        if (left.append_sequence(right)):
            right.set_contained()
            return left
        else:
            sequence = MultiSequence()
            left.set_contained()
            right.set_contained()
            sequence.append_sequence(left)
            sequence.append_sequence(right)
            return sequence

class Node:
    """A node stands for a final character in the generated regular expression 
    (for now). It is responsible for building the appropriate sequences using 
    a `SequenceFactory`.
    """
    def __init__(self, characters, regexp_type):
        """characters : the characters the node will have to match.
        regexp_type : ("strict" | "lax") not used for now."""
        self._len = len(characters)
        self._range = characters
        characters = list(set(characters))
        characters.sort()
        if ((len(self._range) > 1) and (len(characters) == 1)):
            regexp_type = "strict"
        logging.debug('characters = ' + str(characters))
        self._root_sequence = None
        factory = SequenceFactory("strict")
        for char in characters:
            new_sequence = factory.create_sequence(char)
            if (None == self._root_sequence):
                self._root_sequence = new_sequence
            else:
                self._root_sequence = factory.add_sequences(
                    self._root_sequence, new_sequence)
        # make sure that the number of intervals is minimal
        self._root_sequence.merge()

    def set_optional(self):
        """Force this node to consider that the list of provided characters 
        was not complete and thus that this node may represent the absence of 
        a character."""
        self._root_sequence.set_optional()

    def get_is_optional(self):
        """Return True if and only if the node does not necessarily contain 
        a character."""
        return self._root_sequence.get_is_optional()

    def get_length(self):
        """Maybe the nale is not appropriate.
        Returns the number of characters provided to the constructor."""
        return self._len

    def get_string(self, regexp_type = "strict"):
        """Returns the mini regular expression coding for this character 
        without considering the possibility that it is optional."""
        return self._root_sequence.get_string(regexp_type)

def generate(sample_strings, regexp_type = "lax"):
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
    for sample_string in sample_strings:
        i = 0
        for char in sample_string:
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
            node.set_optional()
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
    def finish_node(result):
        """Computes the cardinality of the node and and the needed characters 
        to the regular expression after the node if needed.
        `result`: initial representation of the regular expression.
        Returns the regular expression with one more node."""
        result += ref_node.get_string(regexp_type)
        if (count > 1):
            if ((left == count)):
                logging.debug("{%i}", count)
                result += "{" + str(count) + "}"
            else:
                logging.debug("{%i-%i}", left, count)
                result += "{" + str(left) + "," + str(count) + "}"
        elif (ref_node.get_is_optional()):
            result += "?"
        return result
    for node in nodes:
        logging.debug("node.get_string(regexp_type) = %s", 
            node.get_string(regexp_type))
        logging.debug("node.get_length() = %i", node.get_length())        
        if (None != ref_node):
            if (ref_node.get_string(regexp_type) == 
                node.get_string(regexp_type)):
                if (not node.get_is_optional()):
                    left += 1
                count += 1
            else:
                result = finish_node(result)
                ref_node = node
                logging.debug("next ref_node")
                logging.debug("ref_node.get_string(regexp_type) = %s", 
                    ref_node.get_string(regexp_type))
                logging.debug("ref_node.get_length() = %i", 
                    ref_node.get_length())
                count = 1
                if (ref_node.get_is_optional()):
                    left = 0
                else:
                    left = 1
        else:
            logging.debug("create ref_node")
            ref_node = node
            count = 1
            if (ref_node.get_is_optional()):
                left = 0
            else:
                left = 1
            logging.debug("ref_node.get_string(regexp_type) = %s", 
                ref_node.get_string(regexp_type))
            logging.debug("ref_node.get_length() = %i", ref_node.get_length())
    if (None != ref_node):
        result = finish_node(result)
    def get_string(value):
        """Wrapper around `get_string()`.
        Returns the `get_string()` from `value`."""
        return value.get_string()
    logging.debug(map(get_string, nodes))
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

def check_equal(expected, gotten):
    """`expected`: string containing the expected result.
    `gotten`: string containing what has realy been computed.
    Logs "OK" if `expected` and `gotten` are equal, and an error message 
    otherwise."""
    if (expected != gotten):
        logging.error("Error: expected '" + str(expected) + "' but found '" + 
            str(gotten) + "'")
    else:
        logging.info("OK")

def test_generate(data, regexp_type, expected = None):
    """`data`: list of strings used to generate the regular expression.
    `regexp_type`: "strict" | "lax"
    `expected`: if provided, string containing the expected regular expression.
    """
    exp = generate(data, regexp_type)
    logging.info(str(data) +  " -> " + exp)
    if (None != expected):
        check_equal(expected, exp)

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

def get_random_string(desired_length):
    """Returns a random string of length `desired_length` containing digits, 
    letters, punctuation or space like characters."""
    import string #TODO: find a replacment for this module
    import random
    import sre_parse
    return "".join([random.choice(string.letters + string.digits + 
            string.punctuation + sre_parse.CATEGORY_SPACE) 
        for _ in range(0, desired_length)]) 

def get_random_string_light(desired_length):
    """Returns a random string of length `desired_length` containing digits, 
    some special or space like characters."""
    import string #TODO: find a replacment for this module
    import random
    import sre_parse
    return "".join([random.choice(string.letters + string.digits + "[]-?+*" + 
            sre_parse.CATEGORY_SPACE) 
        for _ in range(0, desired_length)]) 

r1 = [get_random_string(12), get_random_string(12), 
    get_random_string(12), get_random_string(12)]
r2 = [get_random_string(12), get_random_string(11), 
    get_random_string(10), get_random_string(9)]
r3 = [get_random_string(40), get_random_string(40), get_random_string(40), 
    get_random_string(40), get_random_string(40), get_random_string(40)]
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
    long_list.append(get_random_string_light(3))
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
