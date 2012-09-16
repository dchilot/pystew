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

#from analyse import *
import analyse
import comparator
import characters
import generator
import copy

import collections

import logger

#class GrowingResult(object):
#    def __init__(self, container, node, success):
#        self._container = container
#        self._node = node
#        self._success = success
#
#    @property
#    def success(self):
#        return self._success
#
#    @property
#    def container(self):
#        return self._container
#
#    @propert
#    def node(self):
#        return self._node
#
#class Grow(object):
#    def grow(self, node, trusted=False):
#        """
#        `node`: the node we want to add.
#        `trusted`: if True, consider that #node can be added ; if False, #node 
#        will be tested with #can_grow.
#        Return: an object of type #GrowingResult.
#        """ 
#        if (not trusted):
#            if (not self.can_grow(node)):
#                return GrowingResult(self, node, False)
#        self._grow(node)
#        return GrowingResult(self, node, True)

def _merge_contiguous_ranges(range1, range2, trusted=False):
    """Merges two objects of type Range that are contiguous."""
    if (not trusted):
        assert(range1.is_contiguous(range2))
    return Range(itertools.chain(range1.nodes, range2.nodes))


def try_merge_contiguous_ranges(range1, range2):
    """Tries to merge two objects of type Range if they are contiguous.
    Returns None if merging was not possible."""
    assert(range1 is not None)
    assert(range2 is not None)
    new_range = None
    if (range1.is_contiguous(range2)):
        new_range = _merge_contiguous_ranges(range1, range2, trusted=True)
    return new_range

def merge_contiguous_ranges(range1, range2, trusted=False):
    """Merges two objects of type Range that are contiguous."""
    assert(range1 is not None)
    assert(range2 is not None)
    return _merge_contiguous_ranges(range1, range2, trusted)

def match_if_at_ealst_one_common_category(agg1, agg2):
    return (len(agg1.categories.intersection(agg2.categories)) > 0)

def match_if_at_least_one_common_meta_category(agg1, agg2):
    return (len(agg1.meta_categories.intersection(agg2.meta_categories)) > 0)

def match_if_no_different_meta_category(agg1, agg2):
    if (((agg1.exact_match) and (not agg1.optional)) or
        ((agg2.exact_match) and (not agg2.optional))):
        return (agg1.meta_characters == agg2.meta_characters)
    return (agg1.meta_categories == agg2.meta_categories)

def match_if_no_different_category(agg1, agg2):
    if (((agg1.exact_match) and (not agg1.optional)) or
        ((agg2.exact_match) and (not agg2.optional))):
        return (agg1.meta_characters == agg2.meta_characters)
    return (agg1.categories == agg2.categories)

def merge_on_meta_category(destination, source):
    if ((destination.exact_match) or (source.exact_match)):
        pass
    elif (1 == source.max_count):
        source.transfert(
            destination, meta_categories=destination.meta_categories)

def merge_on_category(destination, source):
    if ((destination.exact_match) or (source.exact_match)):
        pass
    elif (1 == source.max_count):
        source.transfert(destination, categories=destination.categories)

def merge_on_meta_character(destination, source):
    if ((destination.exact_match) or (source.exact_match)):
        pass
    elif (1 == source.max_count):
        source.transfert(
            destination, meta_characters=destination.meta_characters)

def generate_from_aggregators(aggregators, type='MetaCharacter'):
    # too easy ...
#    return "".join(
#        map(lambda x: x.get_string(type), aggregators))
    # .. let's try something more complex
    print "start ..." + "".join(map(lambda x: x.get_string(type), aggregators))
    if ('MetaCharacter' == type):
#        merge_function = merge_on_meta_character
        merge_function = merge_on_category
    elif ('Category' == type):
#        merge_function = merge_on_category
        merge_function = merge_on_meta_category
    elif ('MetaCategory' == type):
        merge_function = merge_on_meta_category
    else:
        raise Exception("Unknown type '%s'." % type)
    fake_aggregators = copy.deepcopy(aggregators)
    length = 0
    need_reverse = False
    loop = True
    while (loop):
        loop = (length != len(fake_aggregators))
        last_fake_aggregator = None
        length = len(fake_aggregators)
        for i in range(length):
            fake_aggregator = fake_aggregators.pop(0)
            if (not fake_aggregator.empty):
                if (last_fake_aggregator is not None):
                    merge_function(last_fake_aggregator, fake_aggregator)
                    if (last_fake_aggregator.empty):
                        last_fake_aggregator = fake_aggregator
                    else:
                        if (not fake_aggregator.empty):
                            fake_aggregators.append(last_fake_aggregator)
                            last_fake_aggregator = fake_aggregator
                else:
                    last_fake_aggregator = fake_aggregator
        fake_aggregators.append(last_fake_aggregator)
        fake_aggregators.reverse()
        need_reverse = (not need_reverse)
    if (need_reverse):
        fake_aggregators.reverse()
    return "".join(map(lambda x: x.get_string(type), fake_aggregators))

class Aggregator(object):
    def __init__(self, meta_characters,
        match_function=match_if_at_ealst_one_common_category,
#        merge_function=merge_on_meta_category,
        min_count=1, max_count=1, optional=False):
        self._meta_characters = set()
        self._categories = set()
        self._meta_categories = set()
        if (match_function is None):
            self._match_function = match_if_at_ealst_one_common_category
        else:
            self._match_function = match_function
#        if (merge_function is None):
#            self._merge_function = merge_on_meta_category
#        else:
#            self._merge_function = merge_function
        if (isinstance(meta_characters, analyse.MetaChar)):
            self._add(meta_characters)
        else:
            if (len(meta_characters) == 0):
                pass
            for meta_character in meta_characters:
                self._add(meta_character)
        self._min_count = min_count
        self._max_count = max_count
        self._optional = optional
        self._exact_match = (1 == len(self._meta_characters))

    @property
    def empty(self):
        return (len(self._meta_characters) == 0)

    def set_match_function(self, match_function):
        """Use this if you want to update the fonction deciding whether the 
        other #Aggragator objects we add do match or not."""
        self._match_function = match_function

#    def set_merge_function(self, merge_function):
#        self._merge_function = merge_function

#    def merge(self, other):
#        if (1 == other._max_count):
#            self._merge_function(self, other)

    def transfert(self, destination, meta_categories = [], categories = [],
        meta_characters = []):
        transfered = []
        for meta_character in self._meta_characters:
            if ((meta_character.get_meta_category() in meta_categories) or
                (meta_character.get_category() in categories) or
                (meta_character in meta_characters)):
                transfered.append(meta_character)
                destination._add(meta_character)
        if (len(transfered) > 0):
            for meta_category in meta_categories:
                self._meta_categories.discard(meta_category)
            for category in categories:
                self._categories.discard(category)
            destination._max_count += 1
            if (self._min_count > 0):
                self._min_count -= 1
            for meta_character in transfered:
                self._meta_characters.discard(meta_character)
            self._update()

    def _update(self):
        self.meta_categories.clear()
        self.categories.clear()
        for meta_character in self._meta_characters:
            self._categories.add(meta_character.get_category())
            self._meta_categories.add(meta_character.get_meta_category())

    @property
    def meta_characters(self):
        return self._meta_characters

    @property
    def categories(self):
        return self._categories

    @property
    def meta_categories(self):
        return self._meta_categories

    @property
    def min_count(self):
        return self._min_count

    @property
    def max_count(self):
        return self._max_count

    @property
    def first_meta_character(self):
        first_meta_character = None
        for m in self._meta_characters:
            first_meta_character = m
            break
        return first_meta_character

    @property
    def first_two_meta_characters(self):
        meta_characters = []
        first = True
        for m in self._meta_characters:
            meta_characters.append(m)
            if (first):
                first = False
            else:
                break
        return meta_characters

    def _add(self, meta_character):
        self._meta_characters.add(meta_character)
        self._categories.add(meta_character.get_category())
        self._meta_categories.add(meta_character.get_meta_category())

    def add(self, other):
        added = False
#        if ((self._exact_match) or (other._exact_match)):
#            added = (self._meta_characters == other._meta_characters)
#            if (added):
#                self._max_count += other._max_count
#                self._min_count += other._min_count
#        el
        if (self._match_function(self, other)):
            for meta_character in other._meta_characters:
                self._add(meta_character)
            self._max_count += other._max_count
            self._min_count += other._min_count
            added = True
        return added

    @property
    def exact_match(self):
        return self._exact_match

    @property
    def optional(self):
        return self._optional

    def get_string(self, type='Category'):
        use_brackets = False
        string = ""
        if ("Category" == type):
            if (len(self._meta_characters) > 1):
#                print self._meta_characters
#                print self._categories
                sub_string, is_range = characters.get_categories_as_range(
                    self._categories)
                count = 0
                if (characters.Char.UNKNOWN in self._categories):
                    for missed_character in self._meta_characters:
                        if (missed_character.get_category() == 
                                characters.Char.UNKNOWN):
                            sub_string += missed_character.get_string()
                            count += 1
                if (((count == 1) and (len(sub_string) > 0)) or (count > 1)):
                    is_range = True
                string = sub_string
                use_brackets = is_range
            elif (len(self._meta_characters) == 1): 
                string = self.first_meta_character.get_string()
            else:
                raise Exception("Invalid aggregation!")
#                return string
        elif ("MetaCategory" == type):
            if (len(self._meta_characters) > 1): 
                sub_string, is_range = characters.get_categories_as_range(
                    self._meta_categories)
                count = 0
                if (characters.Char.UNKNOWN in self._categories):
                    for missed_character in self._meta_characters:
                        if (missed_character.get_category() == 
                                characters.Char.UNKNOWN):
                            sub_string += missed_character.get_string()
                            count += 1
                if (((count == 1) and (len(sub_string) > 0)) or (count > 1)):
                    is_range = True
                string = sub_string
                use_brackets = is_range
            elif (len(self._meta_characters) == 1): 
                string = self.first_meta_character.get_string()
            else:
                raise Exception("Invalid aggregation!")
#                return string
        elif ("MetaCharacter" == type):
            count = 0
            last_char = None
            range_count = 0
            last_char_pending = False
            for char in map(
                lambda x: x.get_string(), sorted(self._meta_characters)):
                if (0 == range_count):
                    string += char
                    range_count = 1
                else:
                    if (2 == range_count):
                        string += "-"
#                    print "compare last_char='%s' with char='%s'" % (last_char, char)
                    if (len(last_char) > 1):
                        c_last_char = last_char[1]
                    else:
                        c_last_char = last_char
                    if (len(char) > 1):
                        c_char = char[1]
                    else:
                        c_char = char
                    if (ord(c_last_char) + 1 == ord(c_char)):
                        range_count += 1
                        last_char_pending = True
                    else:
                        if (range_count > 1):
                            string += last_char
                            last_char_pending = False
                        string += char
                        range_count = 1
                last_char = char
                count += 1
            if (last_char_pending):
                string += last_char
            use_brackets = (count > 1)
        if (use_brackets):
            string = "[" + string + "]"
        if (self._max_count != self._min_count):
            if ((0 == self._min_count) and (1 == self._max_count)):
                repetitions = "?"
            else:
                repetitions = "{%s,%s}" % (self._min_count, self._max_count)
        else:
            if (1 == self._min_count):
                repetitions = ""
            else:
                repetitions = "{%s}" % (self._min_count)
        return string + repetitions

    def __str__(self):
        return ("".join(map(str, self._meta_characters)) +
             " {%s,%s}" % (self._min_count, self._max_count))

class Range(object):
    """Just under node Choice. Contains contiguous objects of type MetaChar. 
    A range may contain only one MetaChar."""
    def __init__(self, meta_char):
        self._meta_characters = [meta_char]

    @property
    def meta_characters(self):
        return self._meta_characters

#    @property
#    def category(self):
#        return self._meta_characters[0].get_category()

    def add(self, meta_character):
        added = False
        if (meta_character in self._meta_characters):
            added = True
        else:
            if (self._meta_characters[0].just_greater_than(meta_character)):
                self._meta_characters.insert(0, meta_character)
                added = True
            elif (self._meta_characters[-1].just_lower_than(meta_character)):
                self._meta_characters.append(meta_character)
                added = True
        return added

#    def _grow(self, node):
#        # insert in a sorted way (prevent calling sort afterwards)
#        bisetc.insort(self._nodes, node)

    def is_after(self, meta_character):
        return (self._meta_characters[0].greater_than_just_greater_than(
            meta_character))

    def __lt__(self, other):
        return (self._meta_characters[-1] < self._meta_characters[0])

    def get(self, method='strict'):
        """`method`: 'strict'|'lax'"""
        if ("strict" == method):
            if (len(self._meta_characters) > 1):
                return (('[%s-%s]' 
                    % (self._meta_characters[0].get_string(),
                        self._meta_characters[-1].get_string())), 1)
            else:
                return ('%s' % (self._meta_characters[0].get_string()), 1)
        elif ("lax" == method):
            sequence = None
            count = 0
            for meta_character in self._meta_characters:
                if (not meta_character.empty):
                    if (sequence is None):
                        sequence = generator.Sequence(meta_character)
                        count = 1
                    else:
                        sequence.append_char(meta_character)
#            print "Range: meta_character = '%s' ; count = %s" % (meta_character, count)
            return sequence, count
        else:
            raise Exception("Unknown method: '%s'." % method)

    def __str__(self):
        if (len(self._meta_characters) > 1):
            return ('Range: [%s-%s]' 
                % (self._meta_characters[0], self._meta_characters[-1]))
        else:
            return 'Range: [%s]' % (self._meta_characters[0])

class Choice(object):
    """Category wrapper. Just under node MetaChoice."""
    def __init__(self, meta_character):
        self._category = meta_character.get_category()
        self._ranges = [Range(meta_character)]

    @property
    def category(self):
        return self._category

    @property
    def meta_characters(self):
        meta_characters = []
        for range in self._ranges:
            for meta_character in range.meta_characters:
                meta_characters.append(meta_character)
        return meta_characters

    def add(self, meta_character):
        added = False
        range_added = None
        for index, range in enumerate(self._ranges):
            if (added):
                new_range = try_merge_contiguous_ranges(range_added, range)
                if (new_range is not None):
                    # replace the node to which the meta character was added 
                    # and the current one by one that contains both ranges
                    self._ranges[index - 1] = new_range
                    self.nodes.pop(index)
                # we do not want to mess with iteration and we are done
                break
            else:
                if (range.is_after(meta_character)):
                    # no need to check other ranges
                    self._ranges.insert(index, Range(meta_character))
                    added = True
                    break
                else:
                    added = range.add(meta_character)
        if (not added):
            self._ranges.append(Range(meta_character))
            added = True
        return added

    def get(self, method='strict', sub_method='strict'):
        """`method`: 'strict'|'lax ; 'strict' is faster'
        `sub_method`: 'strict'|'lax' ; used for get_string on type 
        MultiSequence to decide whether we expand ranges or not. Only used if 
        #method is set to 'lax'."""
        if ("strict" == method):
            string = ""
            count = 0
            for range in self._ranges:
                sub_string, sub_count = range.get(method)
                if (sub_count > 0):
                    if (count > 0):
                        string += "|"
                    count += sub_count
                    string += sub_string
            return string, count
        elif ("lax" == method):
            sequence = generator.MultiSequence()
            count = 0
            for range in self._ranges:
                sub_sequence, sub_count = range.get(method)
                if (sub_count > 0):
#                    count += sub_count
                    count += 1
                    sequence.append_sequence(sub_sequence)
            if (count > 1):
#                map(lambda x: x.set_contained(), sequence.)
                sequence.merge()
                count = 1
            string = sequence.get_string(sub_method)
#            print "Choice: string = '%s' ; count = %s" % (string, count)
            return string, count
        else:
            raise Exception("Unknown method: '%s'." % method)

    def __str__(self):
        return 'Choice:\n\t\t\t%s' % "\n\t\t\t".join(map(str, self._ranges))

class MetaChoice(object):
    """MetaCategory wrapper. Just under the root (Element)."""
    def __init__(self, meta_character):
        self._meta_category = meta_character.get_meta_category()
        self._choices = [Choice(meta_character)]

    @property
    def meta_category(self):
        return self._meta_category

    @property
    def meta_characters(self):
        meta_characters = []
        for choice in self._choices:
            for meta_character in choice.meta_characters:
                meta_characters.append(meta_character)
        return meta_characters

    def add(self, meta_character):
        """Try to add a MetaChar (it has to be of the same MetaCategory).
        Return True if and only if #meta_character has been added."""
        added = False
        if (self._meta_category == meta_character.get_meta_category()):
            for choice in self._choices:
                if (choice.add(meta_character)):
                    added = True
                    break
            if (not added):
                # there is no wrapper for the Category of meta_character yet
                self._choices.append(Choice(meta_character))
                added = True
        return added

    def get(self, method='strict', sub_method='strict'):
        """`method`: 'strict'|'lax'
        `sub_method`: 'strict'|'lax' ; see #Choice.get()"""
        string = ""
        count = 0
        for choice in self._choices:
            sub_string, sub_count = choice.get(method, sub_method)
            if (sub_count > 0):
                if (count > 0):
                    string += "|"
                count += sub_count 
                string += sub_string
#        print "MetaChoice: string = '%s' ; count = %s" % (string, count)
        return string, count

    def __str__(self):
        return 'MetaChoice:\n\t\t%s' % "\n\t\t".join(map(str, self._choices))

class Element(object):
    """Root of the tree."""
    def __init__(self):
        self._meta_choices = []
        self._is_optional = False

    @property
    def meta_choices(self):
        return itertools.iterator(self._meta_choices)

    @property
    def optional(self):
        return self._is_optional

    @property
    def meta_characters(self):
        meta_characters = []
        for meta_choice in self._meta_choices:
            for meta_character in meta_choice.meta_characters:
                meta_characters.append(meta_character)
        return meta_characters

    def add(self, meta_character):
        added = False
        if (meta_character.empty):
            self._is_optional = True
            added = True
        if (not added):
            for mc in self._meta_choices:
                if (mc.add(meta_character)):
                    added = True
                    break
            if (not added):
                # the MetaCategory of meta_char is not wrapped yet
                self._meta_choices.append(MetaChoice(meta_character))
                added = True
        # will always return True
        return added

    def get(self, method='strict', sub_method='strict'):
        """`method`: 'strict'|'lax'"""
        string = ""
        count = 0
        for meta_choice in self._meta_choices:
            sub_string, sub_count = meta_choice.get(method, sub_method)
            if (sub_count > 0):
                if (count > 0):
                    string += "|"
                count += sub_count
                string += sub_string
        if (count > 0):
            if (count > 1):
                string = '(' + string + ')'
#            if (self._is_optional):
#                string += '?'
#        print "Element: string = '%s' ; count = %s" % (string, count)
        return string, count

    def __str__(self):
        if (self._is_optional):
            optional = '?'
        else:
            optional = ''
        return 'Element:' + optional + '\n\t%s' % '\n\t'.join(
            map(str, self._meta_choices))

class Enum(object):
    def __init__(self, *args, **kwargs):
        for arg in args:
            self.__setattr__(str(arg), arg)
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __iter__(self):
        return self._values.values()

    def __getitem__(self, key):
        return self._values[key]

Discriminent = Enum('MetaChar', 'Range', 'Category', 'MetaCategory')

class Criterion(object):
    def __init__(self, matching_functions):
        """`matching_functions`: dictionnary. Key: value of enum #Discriminent. 
        Value: function returning True if and only if the two passed objects 
        are considered to match (they are of type #Element). 
        """
        self._matching_functions = matching_functions


    def _accept(self, item, functions):
        for matching_function in functions:
            if (matching_function(meta_character)):
                return True
        return False 

    def accept_meta_char(self, meta_character):
        functions = self._matching_functions[Discriminent.MetaChar]
        return self._accept(meta_character, functions)

    def accept_choice(self, choice):
        functions = self._matching_functions[Discriminent.Choice]
        return self._accept(choice, functions)

    def accept_meta_choice(self, meta_choice):
        functions = self._matching_functions[Discriminent.MetaChoice]
        return self._accept(meta_choice, functions)

#        if (Discriminent.Character == self._discriminent):
#            return (item.get_char() in self._values)
#        elif (Discriminent.Category == self._discriminent):
#            return (item.get_category() in self._values)
#        elif (Discriminent.MetaCategory == self._discriminent):
#            return (item.get_meta_category() in self._values)
#        else:
#            raise Exception("Discriminent '%s' is not handled!" 
#                % self._discriminent)

    def contains(self, other):
        assert(isinstance(other, type(self))) 
        if (self._discriminent == other._discriminent):
            does_contain = True
            for value in other._values:
                if (value not in self._values):
                    does_contain = False
                    break
        else:
            does_contain = False
        return does_contain

#class Combination(object):
#    """`one` and `other_one` should be sets. Each set should contain objects of 
#    type #Criterion and telling which characters to match. Each may match """
#
#class Selector(object):
#    def __init__(self):
#        self._combinations = []
#
#class ElementWrapper(object):
#    """
#    Wrap #Element to be able to chain elements and make repetitions. The 
#    interesting part is that it can make [a-z]r grow to [a-z]{2} and even the 
#    over way arround (r[a-z] -> [a-z]{2}).
#    I can also wrap itself to make a tree when two pieces do not add together
#    (like [a-z] and 1). It should be possible to decide if [A-Z][a-z] should 
#    become friend and generate something like [A-Za-z]{2}.
#    """
#    def __init__(self, element=None):
#        self._element = element
#        self._next = collections.defaultdict(list)

class Regexp(object):
    def __init__(self):
        self._elements = []
    
    def append(self, meta_characters):
        sorted_meta_characters = sorted(set(meta_characters))
        if ((len(sorted_meta_characters) == 1) and
            (sorted_meta_characters[0].empty)):
            return
        element = Element()
        for meta_character in sorted_meta_characters:
            element.add(meta_character)
        self._elements.append(element)
        if (len(element.meta_characters) == 0):
            pass

    def aggregate(self):
        aggregators = []
        last_aggregator = None
        for element in self._elements:
            if (element.optional):
                min_count = 0
            else:
                min_count = 1
            aggregator = Aggregator(
                element.meta_characters, min_count=min_count,
                optional=element.optional)
            aggregator.set_match_function(
                match_if_no_different_category)
#                match_if_no_different_meta_category)
            if ((last_aggregator is None) or 
                (not last_aggregator.add(aggregator))):
                aggregators.append(aggregator)
                last_aggregator = aggregator
        return aggregators

    def get(self, method="strict", sub_method='strict'):
        """`method`: 'strict'|'lax'
        `sub_method`: 'strict'|'lax' ; see #Choice.get()"""
        string = ""
        accumulator = ""
        accumulated = 0
        min_accumulated = 0
        for element in self._elements:
            sub_string, count = element.get(method, sub_method)
            if (count > 0):
                if (0 == accumulated):
                    # start accumulating
                    accumulator = sub_string
                    accumulated = 1
                    if (element.optional):
                        min_accumulated = 0
                    else:
                        min_accumulated = 1
                else:
                    if (accumulator == sub_string):
                        accumulated += 1
                        if (not element.optional):
                            min_accumulated += 1
                    else:
                        # finish accumulation
                        if (accumulated > 1):
                            if (min_accumulated != accumulated):
                                repetitions = ("{%s,%s}" 
                                    % (min_accumulated, accumulated))
                            else:
                                repetitions = "{%s}" % (accumulated)
                        else:
                            repetitions = "?"
                        string += accumulator + repetitions
                        # restart accumulating
                        accumulator = sub_string
                        accumulated = 1
                        if (element.optional):
                            min_accumulated = 0
                        else:
                            min_accumulated = 1
#                print "string = '%s'" % string
        # finish accumulation
        if (accumulated > 0):
            if (accumulated > 1):
                if (min_accumulated != accumulated):
                    repetitions = ("{%s,%s}" 
                        % (min_accumulated, accumulated))
                else:
                    repetitions = "{%s}" % (accumulated)
            else:
                repetitions = "?"
            string += accumulator + repetitions
#        print "accumulator = %s" % accumulator
        return string

    def __str__(self):
        return ('Regex:\n%s' % "\n".join(map(str, self._elements)))

def generate_with_char(sample_strings):
    """
    Generate a regular expression (as a string) that will match the strings in 
    #sample_strings.
    >>> print generate_with_char(['a', 'b', 'c', 'd']).get()
    '[a-d]'
    """
    analyzed = map(analyse.analyse, sample_strings)
    max_length = max(map(len, analyzed))
    meta_characters = []
    for meta_char_list in analyzed:
        meta_characters.append(meta_char_list.get_meta_characters())
    return generate(meta_characters, max_length)

def generate(meta_characters, max_length=None):
#    print "meta_characters = %s" % meta_characters
    if (max_length is None):
        max_length = max(map(len, meta_characters))
    regexp = Regexp()
    for mc in meta_characters:
        length = len(mc)
        for i in range(length, max_length):
            mc.append(analyse.MetaChar(None))
#    print 'zipping'
    for row in zip(*meta_characters):
#        print "type(row) = %s" % type(row)
#        l_char = []
#        for char in row:
#            print "type(char) = %s" % type(char)
#            print "char = %s" % char
#            l_char.append(char)
        regexp.append(row)
#        regexp.append(l_char)
#    logging.debug(regexp)
    return regexp
