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
import logger
from characters import *

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

    def get_string(self, regexp_type = "strict", raw=False):
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

    def matches_char(self, char, method="lax"):
        """Return True if and only the sequence could include the char."""
        return False
 
class Sequence(BaseSequence):
    """Extends `BaseSequence`. Leaf sequence that is used to contain 
    characters."""
    def __init__(self, char):
        """`char`: must be of type `Char`."""
        BaseSequence.__init__(self)
        logging.debug("Created an object of type '%s'", 
            self.__class__.__name__)
        self._chars = []
        #"""The characters contained in the sequence."""
        self._min = None
        #"""The character that has the lowest integer representation."""
        self._max = None
        #"""The character that has the highest integer representation."""
        self.append_char(char)

    @property
    def min(self):
        "Getter"
        return self._min

    @property
    def max(self):
        "Getter"
        return self._max

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
        can_append = self._can_append(char)
        if (can_append):
            self._chars.append(char)
        return can_append

    def get_category(self):
        """The category of the sequence is the category of all the characters.
        >>> Sequence(Char("1")).get_category() == DIGITS
        True
        >>> Sequence(Char("t")).get_category() == \
                LOWER_CASE_LETTERS
        True
        >>> Sequence(Char("D")).get_category() == \
                UPPER_CASE_LETTERS
        True
        >>> Sequence(Char("_")).get_category() == OTHER_WORDS
        True
        >>> Sequence(Char("?")).get_category() == SPECIALS
        True
        >>> Sequence(Char("-")).get_category() == OTHERS
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

        logging.debug("check if (min - 1) %s == other_max %s", 
            ord(self._min.get_char()) - 1, ord(sequence.max.get_char()))
        logging.debug("check if (other_min - 1) %s == max %s", 
            ord(sequence.min.get_char()) - 1, ord(self._max.get_char()))
        lmin = ord(self._min.get_char())
        lmax = ord(self._max.get_char())
        logging.debug("ord(self._min.get_char()) = " + str(lmin))
        logging.debug("ord(self._max.get_char()) = " + str(lmax))
        logging.debug("range [min - max] = " + str(xrange(lmin, lmax)))
        logging.debug("check if other_min %s is in [min - max] %s", 
            sequence.min.get_char(), str(xrange(ord(self._min.get_char()), 
                ord(self._max.get_char()))))
        logging.debug("check if other_max %s is in [min - max] %s", 
            sequence.max.get_char(), str(xrange(ord(self._min.get_char()), 
                ord(self._max.get_char()))))
        # check if the intervals are not disjoint
        if (sequence.get_category() == self.get_category()):
            if ((ord(self._min.get_char()) - 1 == 
                    ord(sequence.max.get_char())) or 
                (ord(sequence.min.get_char()) - 1 == 
                    ord(self._max.get_char())) or
                (ord(sequence.min.get_char()) in range(
                    ord(self._min.get_char()), 1 + ord(self._max.get_char())))\
                                                                            or
                (ord(sequence._max.get_char()) in range(
                    ord(self._min.get_char()), 1 + ord(self._max.get_char())))):
                appended = True
                for char in sequence._chars:
                    self._chars.append(char)
                self._min = min(self._min, sequence.min)
                self._max = max(self._max, sequence.max)
        return appended

    def get_string(self, regexp_type = "strict", raw=False):
        """The result depends on `regexp_type`.
        If `regexp_type` is "strict" the representation will be the exact 
        interval(@TODO ? except if the whole class is covered for \d and \s).
        If `regexp_type` is "lax" the representation of the class will be used
        for some characters :
            - digit -> \d
#            - letter or '_' -> \w
            - space -> \s        
        If the sequence is not contained and more than one character or 
        different from a class is returned brakets will be added unless the 
        sequence is part of a bigger interval."""
        if (raw):
            return "".join(map(lambda x : x.get_char(), self._chars))
#            uniq = set()
#            for c in self._chars:
#                uniq.add(c)
#            return "".join(uniq)
        use_brackets = False
        string = ""
        if (("lax" == regexp_type) and (self._max != self._min) and 
#            (self.get_category() in CATEGORY_HAVE_CLASS)):
            (self.get_category() in [DIGITS, SPACES, LOWER_CASE_LETTERS, 
                UPPER_CASE_LETTERS])):
            if (self.get_category() == DIGITS):
                string = "\d"
#            elif (self.get_category() in CATEGORY_WORDS):
#                string = "\w"
            elif (self.get_category() == LOWER_CASE_LETTERS):
                string = "a-z"
                use_brackets = True
            elif (self.get_category() == UPPER_CASE_LETTERS):
                string = "A-Z"
                use_brackets = True
            elif (self.get_category() == SPACES):
                string = "\s"
            else:
                raise Exception("Unexpected category: " + self.get_category())
        else:
            if (self._max == self._min):
                string = self._max.get_string(raw=raw)
            elif (ord(self._max.get_char()) - ord(self._min.get_char()) > 1):
                string = (self._min.get_string(raw=raw) + "-" + 
                    self._max.get_string(raw=raw))
                use_brackets = True
            else:
                string = (self._min.get_string(raw=raw) + 
                    self._max.get_string(raw=raw))
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
        Returns True if and only if this sequence contains more than one 
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

    def _can_append(self, char):
        matches = False
        if (None != self._min):
            if ((self._min.get_category() == char.get_category()) and
                ((ord(self._min.get_char()) - 2 < ord(char.get_char())) and 
                (ord(char.get_char()) < ord(self._max.get_char()) + 2))):
                if (self._min.get_char() > char.get_char()):
                    self._min = char
                if (self._max.get_char() < char.get_char()):
                    self._max = char
                matches = True
        else:
            self._min = char
            self._max = char
            matches = True
        return matches

    def matches(self, char, method="lax"):
        """Return True if and only the sequence could include the char."""
        if ("strict" == method):
            matches = self._can_add(char)
        else:
            matches = (self._min.get_category() == char.get_category())
        return matches


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
            self._sequences[DIGITS] = []
            self._sequences[LOWER_CASE_LETTERS] = []
            self._sequences[UPPER_CASE_LETTERS] = []
            self._sequences[OTHER_WORDS] = []
            self._sequences[SPACES] = []
            self._sequences[SPECIALS] = []
            self._sequences[OTHERS] = []

    def is_leaf(self):
        """Returns False as the purpose of a MultiSequence is to contain other 
        sequences."""
        return False

    def get_category(self):
        """tentative ... not sure what it should return for `OR` kind."""
        if (MultiSequence.OR == self._kind):
            return None
        elif (MultiSequence.AND == self._kind):
            if (len(self._sequences) == 0):
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
        other_category = sequence.get_category()
        if (MultiSequence.OR == self._kind):
            if (sequence.is_leaf()):
                other_sequences = [sequence]
            else:
                other_sequences = sequence._sequences[other_category]
            sequences = self._sequences[other_category]
            for sub_sequence in other_sequences:
                appended = False
                if (len(sequences) > 0):
                    for pivot in sequences:
                        if (pivot.append_sequence(sub_sequence)):
                            appended = True
                            break
                    if (not appended):
                        sequences.append(sub_sequence)
                        appended = True
                else:
                    sequences.append(sub_sequence)
                    appended = True
#                sub_sequence.set_contained()
        else:
            if (sequence.is_leaf()):
                if (len(self._sequences.keys()) == 0):
                    self._sequences[other_category] = []
                    self._sequences[other_category].append(sequence)
                    appended = True
                else:
                    if (self._sequences.has_key(other_category)):
                        # when 'AND' only put together sequences of the same 
                        # category
                        for pivot in self._sequences[other_category]:
                            appended |= pivot.append_sequence(sequence)
                        if (not appended):
                            self._sequences[other_category].append(
                                sequence)
                            appended = True
            else:
                if (len(self._sequences.keys()) == 0):
                    self._sequences[other_category] = []
                    for key in sequence._sequences:
                        sub_sequence = sequence._sequences[key]
                        self._sequences[other_category].append(
                            sub_sequence)
                    appended = True
                else:
                    if (self._sequences.has_key(other_category)):
                        # when 'AND' only put together sequences of the same 
                        # category
                        for key in sequence._sequences:
                            sub_sequences = sequence._sequences[key]
                            for sub_sequence in sub_sequences:
                                appended = False
                                for pivot in self._sequences[other_category]:
#                                    pivot.set_contained()
                                    appended |= (
                                        pivot.append_sequence(sub_sequence))
                                    if (appended):
                                        break
                                if (not appended):
                                    self._sequences[other_category].append(
                                        sub_sequence)
                                    appended = True
#                                sub_sequence.set_contained()

        return appended

    def merge(self):
        """Not optimal way to try to merge the sub-sequences in case the gaps 
        between them have been filled (or more)."""
        old_sequences = self._sequences
        self.__sub_init()
        for key in old_sequences.keys():
            for sequence in old_sequences[key]:
                self.append_sequence(sequence)
        multi_key = (len(self._sequences.keys()) > 1)
        for key in self._sequences.keys():
            if ((multi_key) or (len(self._sequences[key]) > 1)):
                for sequence in self._sequences[key]:
                    sequence.set_contained()

    def get_string(self, regexp_type = "strict", raw=False):
        """This has only been implemented with OR kind in mind.
        The result depends on `regexp_type`.
        If `regexp_type` is "strict" the representation will be the exact 
        interval(@TODO ? except if the whole class is covered for \d and \s).
        If `regexp_type` is "lax" the representation of the class will be used 
        for some characters :
            - digit -> \d
#            - letter or '_' -> \w
            - space -> \s
        If more than one character or different from a class is returned 
        brakets will be added unless the sequence is part of a bigger 
        interval."""
        string = ""
        logging.debug("Sequence.get_string(%s)" % regexp_type)
        if (raw):
            raw_result = ""
            for key, sequences in self._sequences.items():
                for sequence in sequences:
                    raw_result += sequence.get_string(regexp_type, raw)
            return raw_result
        add_digits_class = False
#        add_words_class = False
        add_lower_case_letters_class = False
        add_upper_case_letters_class = False
        add_spaces_class = False
        digits = ""
#        words = ""
        lower_case_letters = ""
        upper_case_letters = ""
        spaces = ""
        others = ""
        added_digits = 0
#        added_words = 0
        added_lower_case_letters = 0
        added_upper_case_letters = 0
        added_spaces = 0
        added_others = 0
        for key in self._sequences.keys():
            if (len(self._sequences[key]) > 0):
                processed = False
                if (((len(self._sequences[key]) > 1) or 
                    (self._sequences[key][0].get_length() > 1)) and 
                    ("lax" == regexp_type)):
                    if (key == DIGITS):
                        processed = True
                        add_digits_class = True
#                    elif (key in CATEGORY_WORDS):
#                        processed = True
#                        add_words_class = True
                    elif (key == LOWER_CASE_LETTERS):
                        processed = True
                        add_lower_case_letters_class = True
                    elif (key == UPPER_CASE_LETTERS):
                        processed = True
                        add_upper_case_letters_class = True
                    elif (key == SPACES):
                        processed = True
                        add_spaces_class = True
                if (not processed):
                    for sequence in self._sequences[key]:
                        if (key == DIGITS):
                            added_digits += 1
                            digits += sequence.get_string(regexp_type, raw=raw)
#                        elif (key in CATEGORY_WORDS):
#                            added_words += 1
#                            words += sequence.get_string(regexp_type)
                        elif (key == LOWER_CASE_LETTERS):
                            added_lower_case_letters += 1
                            lower_case_letters += sequence.get_string(
                                regexp_type, raw=raw)
                        elif (key == UPPER_CASE_LETTERS):
                            added_upper_case_letters += 1
                            upper_case_letters += sequence.get_string(
                                regexp_type, raw=raw)
                        elif (key == SPACES):
                            added_spaces += 1
                            spaces += sequence.get_string(regexp_type, raw=raw)
                        else:
                            added_others += 1
                            others += sequence.get_string(regexp_type, raw=raw)
        added_count = 0
        need_brackets = False
        if (("lax" == regexp_type) and (add_digits_class)):
            added_count += 1
            string += "\d"
        else:
            added_count += added_digits
            string += digits
#        if (("lax" == regexp_type) and (add_words_class)):
#            added_count += 1
#            string += "\w"
#        else:
#            added_count += added_words
#            string += words
        if (("lax" == regexp_type) and (add_lower_case_letters_class)):
            added_count += 1
            string += "a-z"
            need_brackets = True
        else:
            added_count += added_lower_case_letters
            string += lower_case_letters
        if (("lax" == regexp_type) and (add_upper_case_letters_class)):
            added_count += 1
            string += "A-Z"
            need_brackets = True
        else:
            added_count += added_upper_case_letters
            string += upper_case_letters
        if (("lax" == regexp_type) and (add_spaces_class)):
            added_count += 1
            string += "\s"
        else:
            added_count += added_spaces
            string += spaces
        added_count += added_others
        string += others
        if ((need_brackets) or (added_count > 1)):
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

    def matches(self, char, method="lax"):
        for key, sequences in self._sequences.items():
            for sequence in sequences:
                if (sequence.matches(char, method)):
                    return True
        return False

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

    def try_add_sequences(self, left, right):
        """Try to append `right` to `left`. If it fails than return None."""
        if (left.append_sequence(right)):
            right.set_contained()
            return left
        else:
            return None

class Node(object):
    """A node stands for a final character in the generated regular expression 
    (for now). It is responsible for building the appropriate sequences using 
    a `SequenceFactory`.
    """
    def __init__(self, characters, regexp_type = "strict"):
        """`characters`: the characters the node will have to match.
        `regexp_type`: ("strict" | "lax") not used for now."""
        self._len = len(characters)
        self._range = characters
        #characters = list(set(characters))
        characters = list(characters)
        characters.sort()
        if ((len(self._range) > 1) and (len(characters) == 1)):
            regexp_type = "strict"
        logging.debug('characters = ' + str(characters))
        self._root_sequence = None
        factory = SequenceFactory("strict")
        for char in characters:
            new_sequence = factory.create_sequence(char)
            if (self._root_sequence is None):
                self._root_sequence = new_sequence
            else:
                self._root_sequence = factory.add_sequences(
                    self._root_sequence, new_sequence)
        # make sure that the number of intervals is minimal
        self._root_sequence.merge()
        # used to keep track of matching nodes 
        self._next = []
        self._regexp_type = regexp_type

    def add_matching_node(self, other_node):
        self._next.append(other_node)

    def get_matching_nodes(self):
        return self._next

    @property
    def characters(self):
        return self._range

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

    def get_string(self, regexp_type = "strict", raw=False):
        """Returns the mini regular expression coding for this character 
        without considering the possibility that it is optional."""
        return self._root_sequence.get_string(regexp_type, raw)

    def matches(self, char):
        return self._root_sequence.matches(char)

    def combine(self, other_node):
        new = Node(self.characters + other_node.characters, self._regexp_type)
        new._next = self._next
        return new

def make_optional_tail(tail, tail_len, regexp_type = "lax"):
    result = ""
    if (tail_len > 1):
        result += '(' * (tail_len - 1)
        result += tail.pop(0)
        for t in tail:
            result += t + '?)'
        result += '?'
    else:
        result += tail.pop(0) + '?'
    return result

def make_generated_tail(tail, tail_len, regexp_type = "lax"):
    flip = []
    lengths = map(len, tail)
    max_length = max(lengths)
    for i in range(max_length):
        row = ""
        for index, part in enumerate(tail):
            if (i < lengths[index]):
                row += part[i]
        flip.append(row)
#    print "flip = '%s'" % flip
    max_flipped_length = max(map(len, flip))
    result = generate(flip, regexp_type, make_generated_tail)
#    # this does not work
#    print "repr(result) = '%s'" % repr(result)
    length = len(result)
    single_char = ((1 == length) or ((2 == length) and (result[0] == '\\')))
    if ((single_char) or (1 == max_flipped_length)):
        result += "?"
    else:
        result = "(" + result + ")?"
    return result

def generate(sample_strings, regexp_type = "lax", 
    tail_handler = None, tail_regexp_type = None, super_merge=False):
    """`sample_strings`: list of strings for which to generate a matching 
    regexp. It does not need to be ordered.
    `regexp_type`: ("lax" | "strict"). Using "lax" you will be more likely to 
    get generic regular expression, wheras "strict" will generate regular 
    expression much closer to the samples given.
    `tail_handler`: function used to deal with the tail. The tail is the end 
    of the regular expression to generate, whene there are not characters from 
    all the sample strings available.
    `tail_regexp_type`: ("lax" | "strict"). The regexp_type used when calling 
    #tail_handler.
    `super_merge`: make node match by a range inclusion rather a simple string 
    comparison (this way '[a-z]' != 'g' but the nodes will be considered as 
    matching because g belongs to [a-z]).
    Returns a regular expression that matches the sample strings. The 
    regular expression is checked against the strings at the end.
    An error is logged if the regular expression does not match one of the 
    provided string."""
    if (tail_handler is None):
        tail_handler = make_optional_tail
    if (tail_regexp_type is None):
        tail_regexp_type = regexp_type
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
    tail = []
    def finish_node(sub_result):
        """Computes the cardinality of the node and the needed characters 
        to the regular expression after the node if needed.
        `sub_result`: initial representation of the regular expression.
        Returns the regular expression with one more node."""
        new_result = ""
        raw = (tail_handler == make_generated_tail)
        is_tail_started = (len(tail) > 0)
        is_optional = is_tail_started
        if (count > 1):
            if (is_tail_started):
                # we need to add to the tail
                if (raw):
                    xxxx = ref_node.get_string(regexp_type, raw=True)
                    tail.append(xxxx)
                    for node in ref_node.get_matching_nodes():
                        xxxx = node.get_string(regexp_type, raw=True)
                        tail.append(xxxx)
                else:
                    if ((left == count)):
                        logging.debug("{%i}", count)
                        xxxx = "{" + str(count) + "}"
                    else:
                        logging.debug("{%i-%i}", left, count)
                        xxxx = "{" + str(count) + "}"
                    xxxx = ref_node.get_string(regexp_type) + xxxx
                    tail.append(xxxx)
            else:
                if ((left == count)):
                    logging.debug("{%i}", count)
                    new_result += "{" + str(count) + "}"
                else:
                    logging.debug("{%i-%i}", left, count)
                    new_result += "{" + str(left) + "," + str(count) + "}"
        elif (ref_node.get_is_optional()):
            # if the method to create the tail is make_generated_tail, we have 
            # to prevent character escaping
            xxxx = ref_node.get_string(regexp_type, raw)
            tail.append(xxxx)
            is_optional = True
        if (not is_optional):
            sub_result += ref_node.get_string(regexp_type) + new_result
        return sub_result
    # the job of this not too self explanatory loop is to group consecutive 
    # nodes that match exaclty the same characters.
    for node in nodes:
        logging.debug("node.get_string(regexp_type) = %s", 
            node.get_string(regexp_type))
        logging.debug("node.get_length() = %i", node.get_length())        
        if (ref_node is not None):
            does_match = (ref_node.get_string(regexp_type) == 
                node.get_string(regexp_type))
            if ((not does_match) and (super_merge)):
                does_match = True
                if (['e'] == node.characters):
                    pass
                for char in node.characters:
#                    print "char = %s" % char
#                    print "type(char) = %s" % type(char)
                    does_match &= ref_node.matches(Char(char))
                if (not does_match):
                    logging.debug("%s are not *included* in %s"
                        % (node.characters, ref_node.get_string(regexp_type)))
                else:
                    ref_node = ref_node.combine(node)
            if (does_match):
                ref_node.add_matching_node(node)
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
    logging.debug("tail = %s" % tail)
    tail_len = len(tail)
    if (tail_len > 0):
        result += tail_handler(tail, tail_len, tail_regexp_type)
#        if (tail_len > 1):
#            result += '(' * (tail_len - 1)
#            result += tail.pop(0)
#            for t in tail:
#                result += t + '?)'
#            result += '?'
#        else:
#            result += tail.pop(0) + '?'
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
        string = str(string)
        if (matcher.match(string) is None):
            logging.error("Error: '" + result + "' does not match '" + 
                string + "'")
    return result

if (__name__ == "__main__"):
    import doctest
    doctest.testmod()
