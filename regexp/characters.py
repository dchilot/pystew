"""Describes a character as to be used in a regulare expression."""

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
import copy
import sre_parse

def escape_char(char, raw=False):
    """`char`: character to escape if needed.
    Returns a character so that it can be inserted in a regular expression, 
    escaping it if needed."""
    if (char is None):
        return ''
    if ((char in sre_parse.SPECIAL_CHARS) or ("-" == char) or ("]" == char)):
        if (not raw):
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
    WORD = 'WORD'

    def __init__(self, char, regexp_type = "strict"):
        self._regexp_type = regexp_type
        from sre_parse import SPECIAL_CHARS, CATEGORY_DIGIT
        from sre_parse import WHITESPACE, CATEGORY_SPACE

        if (char is None):
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
        """Returns all possible categories for a character."""
        return [sre_parse.CATEGORY_DIGIT, Char.SPECIAL, 
            sre_parse.CATEGORY_SPACE, Char.LOWER_CASE_LETTER, 
            Char.UPPER_CASE_LETTER, Char.UNKNOWN]

    def get_category(self):
        """Returns the category of this character."""
        return self._category

    def get_meta_category(self):
        """Returns the meta category of this character (#WORD if this is 
        a word (as defined in #CATEGORRY_WORDS, self._category otherwise)."""
        if (self._category in CATEGORY_WORDS):
            return Char.WORD
        else:
            return self._category

    def get_char(self):
        """Returns the wrapped character."""
        return self._char

    def get_string(self, raw=False):
        """Returns a representation of the character that can be includede in 
        a regular expression."""
        return escape_char(self._char, raw=raw)

    def get_is_ordered(self):
        """Returns True if and only if the character is a digit or a letter
        (which are ordered)."""
        return (self._category in [sre_parse.CATEGORY_DIGIT, 
            Char.LOWER_CASE_LETTER, Char.UPPER_CASE_LETTER])

    def __eq__(self, other_char):
        if (other_char is None):
            return False
        return (self._char == other_char.get_char())

    def __ne__(self, other_char):
        if (other_char is None):
            return True
        return (self._char != other_char.get_char())

    def __lt__(self, other_char):
        if (other_char is None):
            return True
        return (self._char < other_char.get_char())

    def __gt__(self, other_char):
        if (other_char is None):
            return False
        return (self._char > other_char.get_char())

def get_category_as_letter(category):
    if (Char.SPECIAL == category):
        return '$'
    elif (Char.UNKNOWN == category):
        return '?'
    elif (Char.LOWER_CASE_LETTER == category):
        return 'l'
    elif (Char.UPPER_CASE_LETTER == category):
        return 'U'
    elif (Char.OTHER_WORD == category):
        return 'o'
    elif (Char.NONE == category):
        return 'n'
    elif (Char.WORD == category):
        return 'w'
    elif (sre_parse.CATEGORY_DIGIT == category):
        return '0'
    elif (sre_parse.CATEGORY_SPACE == category):
        return ' '

# constants
DIGITS = Char('0').get_category()
"""Sample for digits category."""

LOWER_CASE_LETTERS = Char('a').get_category()
"""Sample for lower case letters category."""

UPPER_CASE_LETTERS = Char('A').get_category()
"""Sample for upper case letters category."""

SPACES = Char(' ').get_category()
"""Sample for spaces category."""

OTHERS = Char('-').get_category()
"""Sample for 'characters not in any other category' category."""

OTHER_WORDS = Char('_').get_category()
"""Sample for 'character(s) that are included in the \w class but are not in 
any other category' category."""

SPECIALS = Char('?').get_category()
"""Sample for 'characters that need to be escaped because they have a special 
meaning' category."""

EMPTY = Char(None)
"""The empty character."""

CATEGORY_WORDS = set(
    [DIGITS, LOWER_CASE_LETTERS, UPPER_CASE_LETTERS, OTHER_WORDS])
CATEGORY_HAVE_CLASS = copy.deepcopy(CATEGORY_WORDS)
CATEGORY_HAVE_CLASS.add(SPACES)

"""
>>> DIGITS in CATEGORY_HAVE_CLASS
True
>>> LOWER_CASE_LETTERS in CATEGORY_HAVE_CLASS
True
>>> UPPER_CASE_LETTERS in CATEGORY_HAVE_CLASS
True
>>> OTHER_WORDS in CATEGORY_HAVE_CLASS
True
>>> for char in [SPACES, OTHERS, SPECIALS]:
>>>     char.get_category() in CATEGORY_HAVE_CLASS
True
True
True
"""

def get_category_as_range(category):
    if (Char.SPECIAL == category):
        return ("\\" + "\\".join(sre_parse.SPECIAL_CHARS), True)
    elif (Char.LOWER_CASE_LETTER == category):
        return ('a-z', True)
    elif (Char.UPPER_CASE_LETTER == category):
        return ('A-Z', True)
    elif (Char.OTHER_WORD == category):
        return ('_', False)
    elif (Char.WORD == category):
        return ('\w', True)
    elif (sre_parse.CATEGORY_DIGIT == category):
        return ('\d', True)
    elif (sre_parse.CATEGORY_SPACE == category):
        return ('\s', True)
    elif (Char.UNKNOWN == category):
        return ('', False)
    else:
        raise Exception("Category '%s' not handled!" % category)

def get_categories_as_range(categories):
    string = ""
    is_range = False
    for category in sorted(categories):
        sub_string, sub_is_range = get_category_as_range(category)
        string += sub_string
        is_range |= sub_is_range
    return string, is_range

if __name__ == "__main__":
    import doctest
    doctest.testmod()
