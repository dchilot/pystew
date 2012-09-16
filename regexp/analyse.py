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
import characters
import generator
import re
import copy
import sys
import bisect
import operator
import itertools

def minex(iterable):
    s = set(iterable)
    if ((len(s) > 1) and (0 in s)):
        s.remove(0)
    if (len(s) > 0):
        return min(s)
    else:
        return 0

class Repetition(object):
    def __init__(self):
        self._items = []
        self._batches = [0]
        self._force_optional = False

    def force_optional(self):
        self._force_optional = True

    def add(self, item):
        self._batches[-1] += 1
        self._items.append(item)

    def new_batch(self):
        if (self._batches[-1] != 0):
            self._batches.append(0)

    def get_max_count(self):
        return max(self._batches)

    def get_min_count(self):
        if (self._force_optional):
            return 0
        else:
            return minex(self._batches)

    def get_items(self):
        return self._items

    def __repr__(self):
        maximum = self.get_max_count()
        minimum = self.get_min_count()
        if ((maximum is not None) and (maximum > 0)):
            if (minimum != maximum):
                count = "{%s,%s}" % (minimum, maximum)
            else:
                count = "{%s}" % (minimum)
            return count + " x " + str(self._items[0])
        else:
            return "/0/"

def group(s):
    """\
    `s` should be a string or something that looks like a list of characters.
    Returns a map of 
    """
    result = {}
    length = len(s)
    if (1 >= length):
        repetition = Repetition()
        repetition.add(s)
        result[length] = [repetition]
    else:
        for g in range((length / 2), 0, -1):
            seq = s[0:g]
            tail = s[g:]
            loop = True
            repetition = Repetition()
            repetition.add(seq)
            while (loop):
                loop = False
                if (seq == tail[:g]):
                    repetition.add(tail[:g])
                    tail = tail[g:]
                    loop = (len(tail) > g)
            if (repetition.get_max_count() > 1):
                if (len(tail) > 0):
                    tails = group(tail)
                    max_tail = tails[max(tails.keys())]
#                    print '1 max_tail = ' + str(max_tail)
                    result[g] = [repetition] + max_tail
                else:
                    result[g] = [repetition]
#        if (len(result) == 0):
        head = s[0]
        tail = s[1:]
        tails = group(tail)
        keys = set(tails.keys())
        if ((len(keys) > 1) and (0 in keys)):
            keys.remove(0)
        max_tail = tails[min(keys)]
        head_repetition = Repetition()
        head_repetition.add([head])
#        print '2 max_tail = ' + str(max_tail)
        result[0] = [head_repetition] + max_tail
    return result

class MetaChar(object):
    """
    >>> e1 = MetaChar(None)
    >>> e2 = MetaChar(None)
    >>> print e1 == e2
    True
    >>> s = set()
    >>> s.add(e1)
    >>> s.add(e2)
    >>> print s
    set([``])
    """
    def __init__(self, char, custom_meta_categories = None):
        """`char`: the character to wrap.
        `custom_meta_categories`: a map containing for a custom catagory and a 
        function used to check that a character belongs to this category. The 
        custom category has to be a string. The first matching category is 
        used and the others are not analysed.
        """
        self._char = characters.Char(char)
        self._meta_category = None
        if (custom_meta_categories is not None):
            for category in custom_meta_categories.keys():
                function = custom_meta_categories[category]
                if (function(self._char.get_char())):
                    self._meta_category = category
                    break
        if (self._meta_category is None):
            self._meta_category = self._char.get_meta_category()

    @property
    def empty(self):
        return (characters.EMPTY == self._char)

    def get_char(self):
        return self._char.get_char()

    def get_string(self, raw=False):
        return self._char.get_string(raw=raw)

    def get_category(self):
        return self._char.get_category()

    def get_meta_category(self):
        return self._meta_category

    def is_contiguous(self, other):
        assert(isinstance(other, MetaChar))
        maybe = (self.get_category() == other.get_category())
        if (maybe):
            delta = abs(ord(self.get_char()) - ord(other.get_char()))
            return (1 == delta)
        else:
            return False

    def just_greater_than(self, other):
        """other|self -> True"""
        assert(isinstance(other, MetaChar))
        return ((self.get_category() == other.get_category()) and 
            ((ord(self.get_char()) - ord(other.get_char())) == 1))

    def just_lower_than(self, other):
        """self|other -> True"""
        assert(isinstance(other, MetaChar))
        return ((self.get_category() == other.get_category()) and 
            ((ord(self.get_char()) - ord(other.get_char())) == -1))

    def greater_than_just_greater_than(self, other):
        """other|just_greater ; just_greater > self -> True"""
        assert(isinstance(other, MetaChar))
        return ((self.get_category() == other.get_category()) and 
            ((ord(self.get_char()) - ord(other.get_char())) > 1))

    def lower_than_just_lower_than(self, other):
        """just_lower|other ; self < just_lower -> True"""
        assert(isinstance(other, MetaChar))
        return ((self.get_category() == other.get_category()) and 
            ((ord(self.get_char()) - ord(other.get_char())) < -1))

    def __repr__(self):
        if (self.get_char() is not None):
            return "`" + self.get_char() + "`"
        else:
            return "``"

    def __add__(self, other):
        assert(isinstance(other, MetaChar))
        return MetaCharList([self, other])

    def __eq__(self, other):
        return (self.get_char() == other.get_char())

    def __lt__(self, other):
        return (self.get_char() < other.get_char())

    def __gt__(self, other):
        return (self.get_char() > other.get_char())

    def __ne__(self, other):
        if (other is None):
            return (not self.empty)
        else:
            return (self.get_char() != other.get_char())

    def __hash__(self):
        if (self.empty):
            return -1
        else:
            return ord(self._char.get_char())

class CategoryWrapper(object):
    def __init__(self, category):
        self._inner_category = category

    def get(self):
        return self._inner_category

    def __repr__(self):
        return self._inner_category.get_category()

    def __eq__(self, other):
        return (self.__repr__() == other.__repr__())

    def __lt__(self, other):
        return (self.__repr__() < other.__repr__())

    def __gt__(self, other):
        return (self.__repr__() > other.__repr__())

    def __ne__(self, other):
        return (self.__repr__() != other.__repr__())

    def get_category(self):
        return self._inner_category.get_category()

class Category(object):
    def __init__(self, meta_chars):
        self._meta_characters = []
        for meta_char in meta_chars:
            self.add(meta_char)

    def add(self, meta_char):
        assert(isinstance(meta_char, MetaChar))
        do_add = True
        if (len(self._meta_characters) > 0):
            if (self._meta_characters[0].get_category() != 
                meta_char.get_category()):
                do_add = False
        if (do_add):
            self._meta_characters.append(meta_char)
        return do_add

    def get_category(self):
        if (len(self._meta_characters) > 0):
            return self._meta_characters[0].get_category()
        else:
            return None

    def get_characters(self):
        result = []
        for meta_character in self._meta_characters:
            result.append(meta_character.get_char())
        return result

    def get_meta_characters(self):
        return self._meta_characters

    def __repr__(self):
        lines = [""] * 5
        char_line = ""
        category_line = ""
        for meta_char in self._meta_characters:
            if (len(char_line) > 0):
                char_line += ", "
            else:
                category_line = " " + meta_char.get_category() + " "
            char_line += "'" + meta_char.get_char() + "'"
        char_line = " " + char_line + " "
        if (len(category_line) > len(char_line)):
            length = len(category_line)
            char_line = char_line.ljust(length, ' ')
        else:
            length = len(char_line)
            category_line = category_line.ljust(length, ' ')
        char_line = "|" + char_line
        category_line = "|" + category_line
        lines[0] = "+" + "-" * length
        lines[1] = category_line
        lines[2] = lines[0]
        lines[3] = char_line
        lines[4] = lines[0]
        return lines

class MetaCategoryWrapper(object):
    def __init__(self, meta_category):
        self._inner_meta_category = meta_category

    def get(self):
        return self._inner_meta_category
        
    def __repr__(self):
        return self._inner_meta_category.get_meta_category()

    def __eq__(self, other):
        return (self.__repr__() == other.__repr__())

    def __lt__(self, other):
        return (self.__repr__() < other.__repr__())

    def __gt__(self, other):
        return (self.__repr__() > other.__repr__())

    def __ne__(self, other):
        return (self.__repr__() != other.__repr__())

class MetaCategory(object):
    def __init__(self, meta_chars):
        self._categories = []
        self._meta_category = None
        for meta_char in meta_chars:
            self.add(meta_char)

    def add(self, meta_char):
        assert(isinstance(meta_char, MetaChar))
        added = False
        if (len(self._categories) == 0):
            self._categories.append(Category([meta_char]))
            self._meta_category = meta_char.get_meta_category()
            added = True
        else:
            if (meta_char.get_meta_category() == self._meta_category):
                if (not self._categories[-1].add(meta_char)):
                    self._categories.append(Category([meta_char]))
                added = True
        return added

    def get_categories(self):
        result = []
        for category in self._categories:
            result.append(CategoryWrapper(category))
        return result

    def get_meta_category(self):
        return self._meta_category

    def get_characters(self):
        result = []
        for category in self._categories:
            result += category.get_characters()
        return result

    def get_meta_characters(self):
        result = []
        for category in self._categories:
            result += category.get_meta_characters()
        return result

    def __repr__(self):
        lines = [""] * 7
        for category in self._categories:
            for i, sub_line in enumerate(category.__repr__()):
                lines[i + 2] += sub_line
        length = len(lines[2]) - 1
        lines[0] = "+" + "-" * length
        lines[1] = " " + str(self._meta_category) + " "
        lines[1] = lines[1].ljust(length, " ")
        lines[1] = "|" + lines[1]
        return lines

class MetaCharList(object):
    def __init__(self, meta_chars):
        self._meta_categories = []
        for meta_char in meta_chars:
            self.add(meta_char)

    def add(self, meta_char):
        assert(isinstance(meta_char, MetaChar))
        if (len(self._meta_categories) == 0):
            self._meta_categories.append(MetaCategory([meta_char]))
            added = True
        else:
            if (not self._meta_categories[-1].add(meta_char)):
                self._meta_categories.append(MetaCategory([meta_char]))

    @property
    def characters(self):
        for meta_category in self._meta_categories:
            for character in meta_category.get_characters():
                yield character

    @property
    def meta_characters(self):
        for meta_category in self._meta_categories:
            for character in meta_category.get_meta_characters():
                yield character

    def get_meta_characters(self):
        meta_characters = []
        for meta_category in self._meta_categories:
            for meta_character in meta_category.get_meta_characters():
                meta_characters.append(meta_character)
        return meta_characters

    def get_categories(self):
        result = []
        for meta_category in self._meta_categories:
            result += meta_category.get_categories()
        return result

    def get_meta_categories(self):
        result = []
        for meta_category in self._meta_categories:
            result.append(MetaCategoryWrapper(meta_category))
        return result

    def get_character(self, index):
        result = None
        offset = 0
        for meta_category in self._meta_categories:
            characters = meta_category.get_characters()
            if (len(characters) > index - offset):
                result = characters[index - offset]
                break
            else:
                offset += len(characters)
                if (0 > index - offset):
                    break
        return result

    def get_meta_character(self, index):
        result = None
        offset = 0
        for meta_category in self._meta_categories:
            meta_characters = meta_category.get_meta_characters()
            if (len(meta_characters) > index - offset):
                result = meta_characters[index - offset]
                break
            else:
                offset += len(meta_characters)
                if (0 > index - offset):
                    break
        return result

    def get_meta_category(self, index):
        """Get the MetaCategory at character with index #index."""
        result = None
        offset = 0
        for meta_category in self._meta_categories:
            meta_characters = meta_category.get_meta_characters()
            if (len(meta_characters) > index - offset):
                result = meta_category
                break
            else:
                offset += len(meta_characters)
                if (0 > index - offset):
                    break
        return result

    def __len__(self):
        length = 0
        for meta_category in self._meta_categories:
            for character in meta_category.get_meta_characters():
                length += 1
        return length

    def __repr__(self):
        lines = [""] * 7
        for meta_category in self._meta_categories:
            for i, sub_line in enumerate(meta_category.__repr__()):
                lines[i] += sub_line
        result = ""
        lines[0] += "+"
        lines[1] += "|"
        lines[2] += "+"
        lines[3] += "|"
        lines[4] += "+"
        lines[5] += "|"
        lines[6] += "+"
        for line in lines:
            result += line + "\n"
        return result

# 0     +-----------------------------------------+-----+----------------+
# 1     | MetaCategory 1                          | ... | MetaCategory i |
# 2 0   +----------------------+-----+------------+-----+----------------+
# 3 1   | Category 1           | ... | Category j | ... | ...            |
# 4 2 0 +----------------------+-----+------------+-----+----------------+
# 5 3 1 | char 1, ..., char k  | ... | ...        | ... | ...            |
# 6 4 2 +----------------------+-----+------------+-----+----------------+

def analyse(string):
    """\
    Analyse all the characters of the string `string`. Analyse means build a 
    matecharacter that gives more informations (like the class).
    Return a `MetaCharList`.
    """
    result = MetaCharList([])
    for char in string:
        meta_char = MetaChar(char)
        result.add(meta_char)
    return result

def get_repetitions(analysed):
    repetitions = 1
    for item in analysed:
        if (isinstance(item, Repetition)):
            assert(item.get_min_count() != 0)
            repetitions *= item.get_max_count()
    return repetitions

def get_max_repetitions(map):
    print '\t' + str(map)
    max_r = -1
    items = []
    for k in map.keys():
        value = map[k]
        r = get_repetitions(value)
        if (r > max_r):
            max_r = r
            items = [value]
        elif (r == max_r):
            items.append(value)
    return items

def merge_lists(lists):
    result = []
    list_count = len(lists)
    iterators = [0] * list_count
    i_end = []
    for i in range(0, list_count):
        i_end.append(len(lists[i]))
    
    def has_more(index):
        return (i_end[index] > iterators[index])

    def finished():
        result = True
        for i in range(0, list_count):
            result = (result and (not has_more(i)))
        return result

    def partially_finished():
        result = False
        for i in range(0, list_count):
            result = (result or (not has_more(i)))
        return result

    def get_item(index):
        return lists[index][iterators[index]]

    def next_item(indexes):
        """`indexes`: the indexes of string for which to go to the following 
        item. It can be an iterable of int or a single int."""
        if (hasattr(indexes, '__iter__')):
            for index in indexes:
                iterators[index] += 1
        else:
            iterators[indexes] += 1

    def get_next_index(index):
        index += 1
        if (index >= list_count):
            return None
        while (not has_more(index)):
            index += 1
            if (index >= list_count):
                return None
        return index

    def get_other_indexes(index):
        others = []
        for i in range(list_count):
            if ((index != i) and (has_more(i))):
                others.append(i)
        return others

    while (not finished()):
        first_index = -1
        pivots = []
        failed = []
        discarded = []
        matches = []
        first_index = get_next_index(first_index)
        while (first_index is not None):
#            first_index = get_next_index(first_index)
            if (first_index is None):
                break
            pivot = copy.deepcopy(get_item(first_index))
#            print "\tpivot = %s" % (pivot)
            first_pivot = pivot.get_items()[0]
            next_index = get_next_index(first_index)
            f = []
            other = None
            match = [first_index]
#            while (next_index is not None):
#                other = get_item(next_index)
#                print "\t\tother = %s" % other
#                if (other.get_items()[0] == first_pivot):
#                    match.append(next_index)
#                    pivot.new_batch()
#                    for ii in other.get_items():
#                        pivot.add(ii)
#                else:
#                    f.append(next_index)
#                next_index = get_next_index(next_index)
            other_indexes = get_other_indexes(first_index)
            for other_index in other_indexes:
                other = get_item(other_index)
#                print "\t\tother = %s" % other
                if (other.get_items()[0] == first_pivot):
                    match.append(other_index)
                    pivot.new_batch()
                    for ii in other.get_items():
                        pivot.add(ii)
                else:
                    f.append(other_index)
            matches.append(match)
            if ((other is not None) and (len(f) == 0)):
                # everything matched
                first_index = get_next_index(first_index)
                break
            failed.append(f)
            discarded.append(first_index)
            first_index = get_next_index(first_index)
            pivots.append(pivot)
        if (len(failed) == 0):
            # everything matched on the first pivot
            if (partially_finished()):
                pivot.force_optional()
            result.append(pivot)
            next_item(matches[-1])
            print "everything matched"
        else:
            # pick the items that had the most matches
#            print "@TODO"
#            print "discarded = %s" % (discarded)
#            print "failed = %s" % (failed)
#            print "matches = %s" % (matches)
#            print "pivots = %s" % (pivots)
#            print "pivot = %s" % (pivot)
            len_matches = map(len, matches)
            min_index, min_value = min(
                enumerate(len_matches), key=operator.itemgetter(1))
#            print "min_index = %s" % min_index
#            print "pivots[min_index] = %s" % type(pivots[min_index])
            selected_pivot = pivots[min_index]
            selected_pivot.force_optional()
            result.append(selected_pivot)
#            print "selected_pivot = %s" % selected_pivot
            next_item(matches[min_index])
            first_index = get_next_index(min_index)

    expanded = ""
    for sub_result in result:
        all_chars = []
        node_mins = []
        node_maxs = []
        for item_list in sub_result.get_items():
            node_min = None
            node_max = None
            for i, item in enumerate(item_list):
                if (len(all_chars) - 1 < i):
                    all_chars.append([])
                all_chars[i] += item.get().get_characters()
                length = len(item.get().get_characters())
                if (len(node_mins) - 1 < i):
                    node_mins.append(length)
                else:
                    if (length < node_mins[i]):
                        node_mins[i] = length
                if (len(node_maxs) - 1 < i):
                    node_maxs.append(length)
                else:
                    if (length > node_maxs[i]):
                        node_maxs[i] = length
            node_mins.append(node_min)
            node_maxs.append(node_max)
        sub_string = ""
        has_repetitions = False
        zipped = zip(all_chars, node_mins, node_maxs)
        only_one = (len(zipped) == 1)
        if (not only_one):
            for all, node_min, node_max in zipped:
                node = generator.Node(all)
                node_str = node.get_string('lax')
                if (node_min != node_max):
                    node_str += "{%s,%s}" % (node_min, node_max)
                    has_repetitions = True
                else:
                    if (node_min > 1):
                        node_str += "{%s}" % (node_min)
                        has_repetitions = True
                sub_string += node_str
            node_min = 1
            node_max = 1
        else:
            all, node_min, node_max = zipped[0]
            node = generator.Node(all)
            sub_string = node.get_string('lax')
#        print "sub_string = " + sub_string
        min_c = node_min * sub_result.get_min_count()
        max_c = node_max * sub_result.get_max_count()
        if ((len(all_chars) > 1) or (has_repetitions)):
            if ((max_c > 1) or (min_c != max_c)):
                sub_string = "(" + sub_string + ")"
        if (min_c != max_c):
            sub_string += "{%s,%s}" % (min_c, max_c)
        else:
            if (min_c > 1):
                sub_string += "{%s}" % (min_c)
#        print "sub_string = " + sub_string
        expanded += sub_string
    return expanded

def merge(c1, c2, c3):
    print "merge(%s, %s, %s)" % (c1, c2, c3)
    result = []
    for list1 in c1:
        for list2 in c2:
            for list3 in c3:
                print "merge_lists([%s, %s, %s])" % (list1, list2, list3)
                result.append(merge_lists([list1, list2, list3]))
    return result

def merge2(c_list):
    print "merge2(%s)" % (c_list)
    result = []
    for product in itertools.product(*c_list):
        print "product = " + str(product)
#        print "merge_lists(%s)" % (product)
        result.append(merge_lists(product))
    return result

def restrict(element):
    c = group(element.get_categories())
#    c = group(element.get_meta_categories())
    print "c"
    print c
    # 
    restricted_c = get_max_repetitions(c)
    print "restricted_c"
    print restricted_c
    return restricted_c
#    m = group(element.get_meta_categories())
#    restricted_m = get_max_repetitions(m)
#    print "restricted_m"
#    print restricted_m
#    return restricted_m

def main():

    with open("pretty_print", "w") as f:
        strings = ([
            "Le soleil se levera demain matin.",
            "Le petit chat dort 12.",
            "Il fait beau et chaud 12 13 14.",
            "La nuit est sombre.",
            "Les feintes sont possibles avec cet algorithme.",
            ])
        strings = ([
            "Le soleil se levera demain matin.",
            "Le petit chat dort.",
            "Il fait beau et chaud.",
            "La nuit est sombre.",
            "Les feintes sont possibles avec cet algorithme.",
            ])
        strings = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Nunc adipiscing elit eget sapien lacinia eu fringilla dolor pretium.",
            "Duis tempor velit sit amet quam condimentum eget tempus augue pretium.",
            "Vivamus cursus elit vitae enim euismod quis consequat felis pretium.",
            "Aliquam sit amet lorem ut neque condimentum sodales ut vel lorem.",
            "Proin sed lorem id lacus luctus tincidunt.",
            "Suspendisse a nisl id tellus fermentum tristique vitae sed sapien.",
            "Duis ultrices est vitae dolor hendrerit eu iaculis felis laoreet.",
            "Curabitur quis lectus nec mauris pharetra elementum.",
            "Duis nec lectus nulla, non gravida erat.",
            "Proin molestie posuere turpis, ac mollis nisl malesuada eu.",
            "Nulla dictum malesuada massa, eget tincidunt eros volutpat eget.",
            "Integer sed magna tellus, pulvinar aliquam eros.",
            "Maecenas convallis ornare ipsum, sed consequat enim porttitor bibendum.",
            "Mauris nec augue ac leo consectetur tempus nec mattis tellus.",
            "In dictum urna ac eros convallis volutpat.",
            "Duis at nunc eget enim vehicula pulvinar.",
            "Morbi quis ante id dui pellentesque fermentum.",
            "Nulla sit amet massa lacinia tortor egestas molestie.",
            "Nunc scelerisque vulputate risus, at venenatis eros consectetur vel.",
            "Sed at magna vestibulum est auctor sagittis.",
            "Donec vehicula sollicitudin arcu, at tempus nisl hendrerit sit amet.",
            "Sed mollis massa vitae felis ullamcorper convallis.",
            "Praesent in justo in urna adipiscing varius.",
            "Vivamus gravida eros non mi laoreet ac imperdiet arcu iaculis.",
            "Ut aliquam tincidunt arcu, eu venenatis leo tempus ac.",
            "Curabitur quis augue mauris, non dignissim nibh.",
            "Donec fringilla justo eget massa dignissim semper.",
            "Fusce iaculis leo vitae velit vulputate adipiscing.",
            "Proin et libero in quam molestie porttitor non at odio.",
            ]

#        strings = ([
#            " Column 1    | Column 2   | Last Column",
#            " something   | else       | is written ",
#            " it is not   | mandatory  | to fill    ",
#            " the last    | column     |",
#            " you can     | put a lot  | of chars   ",
#            ])

#        strings = ([
#            "Le petit chat dort.",
#            "Il fait beau et chaud.",
#            "Il etait un petit navire.",
#            ])
#        strings = ([
#            "A,",
#            "BC,",
#            "DEF,",
#            ])

        a = map(analyse, strings)
#        a1 = analyse(strings[0])
#        a2 = analyse(strings[1])
#        a3 = analyse(strings[2])
#        f.write(str(a1))
#        f.write(str(a2))
#        f.write(str(a3))
        for element in a:
            f.write(str(element))
            print element.get_categories()
#        print a1.get_categories()
#        print a2.get_categories()
#        print a3.get_categories()
        print "----------"
#        # group characters by categories
#        c1 = group(a1.get_categories())
#        print "c1"
#        print c1
#        # 
#        restricted_c1 = get_max_repetitions(c1)
#        print "restricted_c1"
#        print restricted_c1
#        m1 = group(a1.get_meta_categories())
#        restricted_m1 = get_max_repetitions(m1)
#        print "restricted_m1"
#        print restricted_m1
#        
#        c2 = group(a2.get_categories())
#        print "-------"
#        print "c2"
#        print c2
#        restricted_c2 = get_max_repetitions(c2)
#        print "restricted_c2"
#        print restricted_c2
#        m2 = group(a2.get_meta_categories())
#        restricted_m2 = get_max_repetitions(m2)
#        print "restricted_m2"
#        print restricted_m2
#
#        c3 = group(a3.get_categories())
#        print "-------"
#        print "c3"
#        print c3
#        restricted_c3 = get_max_repetitions(c3)
#        print "restricted_c3"
#        print restricted_c3
#        m3 = group(a3.get_meta_categories())
#        restricted_m3 = get_max_repetitions(m3)
#        print "restricted_m3"
#        print restricted_m3

        all_restricted = map(restrict, a)
        for e in all_restricted:
            print e
#        sys.exit(0)
#        regexps = merge(restricted_c1, restricted_c2, restricted_c3)
        regexps2 = merge2(all_restricted)
#        print merge_lists([restricted_c1, restricted_c2])
        for regexp in regexps2:
            print regexp
            matcher = re.compile(regexp)
            for string in strings:
                string = str(string)
                if (matcher.match(string) is None):
                    logging.error("Error: '" + regexp + "' does not match '" + 
                        string + "'")

if (__name__ == "__main__"):
    main()
