

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
import collections
import copy
import re
import characters
import analyse
import generator

import numpy

class Node(object):
    def __init__(self, count):
        self._count = count 

    def _get_height(self):
        if (1 == self._count):
            height = 1
        else: 
            height = (self._count - 1) * 2 + 1
        return height

    def set_count(self, count):
        if (count > self._count):
            self._count = count

    def get_count(self):
        return self._count

    def __str__(self):
        return "\n".join(self.get_str())

    def get_str(self):
        return ""

class Choice(Node):
    def __init__(self, strings, count=None):
        self._length = len(strings)
        if (count is None):
            count = self._length
        else:
            assert(count >= self._length)
        Node.__init__(self, count)
        self._strings = strings

    def __repr__(self):
        return "strings = %s ; count = %s" % (self._strings, self._count)

    def get_str(self):
        if (1 > self._count):
            return None
        strings = []
        max_length = max(map(len, self._strings))
        width = max_length + 4
        h = 1
        if (1 == self._length):
            strings.append("--- " + self._strings[0] + " ---")
        else:
            strings.append(
                "-+- " + self._strings[0].rjust(max_length) + " -+-")
            for i in range(1, self._length):
                strings.append(" |" + " " * width + "| ") 
                strings.append(
                    " +- " + self._strings[i].rjust(max_length) + " -+ ")
                h += 2
        for i in range(h, self._get_height()):
            strings.append(" " * width)
        return strings

class Common(Node):
    def __init__(self, string, count=1):
        assert(count > 0)
        Node.__init__(self, count)
        self._string = string

    def __repr__(self):
        return "string = %s ; count = %s" % (self._string, self._count)

    def get_str(self):
        width = len(self._string) + 4 + 4
        strings = ["--- " + self._string + " ---"]
        for i in range(1, self._get_height()):
            strings.append(" " * width)
        return strings

def split(string, desired_length):
    if (1 > desired_length):
        return None
    length = len(string)
    if (length < desired_length):
        return None
    sub_string = []
    for i in range(0, length - desired_length + 1):
        current = string[i:i + desired_length]
        if (current not in sub_string):
            sub_string.append(current)
    return sub_string

def all_indices(string, sub, offset=0):
    listindex = []
    i = string.find(sub, offset)
    while (i >= 0):
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex

def combine(indexes):
    """`indexes`: [[...], [...], [...]].
    Pick one index in each sub list and return all the combinations."""
    length = len(indexes)
    if (0 == length):
        return []
    elif (1 == length):
        combinations = []
        for index in indexes[0]:
            combinations.append([index])
        return combinations
    else:
        combinations = []
        for pick in indexes[0]:
            head = [pick]
            subs = combine(indexes[1:])
            for sub in subs:
                combination = head + sub
                combinations.append(combination)
        return combinations

# Define a named tuple to store a pattern and the indexes where it was found
Match = collections.namedtuple("Match", ['pattern', 'indexes'])

def compare_strings(s):
    logging.info("compare_strings(%s)" % s)
    s_length = len(s)
    mega_map = {}
    for i in range(1, len(s[0]) + 1):
        list_all = []
        for index, pattern in enumerate(split(s[0], i)):
            found_all = [[index] + all_indices(s[0], pattern, index + 1)]
            for j in range(1, len(s)):
                found = all_indices(s[j], pattern)
                if (len(found) > 0):
                    logging.debug("pattern '%s' found in s[%s] '%s' at %s" %
                        (pattern, j, s[j], found))
                    found_all.append(found)
            if (len(found_all) == s_length):
                logging.debug("'%s' found in all: %s" % (pattern, found_all))
                list_all.append(Match(pattern, found_all))
        if (len(list_all) > 0):
            mega_map[i] = list_all
    # mega_map now contains patterns that are found in all the strings at 
    # different indexes
    logging.info("mega_map = %s" % mega_map)
    # sort the patterns by indexes
    index_to_pattern = []
    # sort the indexes by pattern
    pattern_to_index = []
    # create the objects
    for i in range(0, s_length):
        line = []
        for j in range(0, len(s[i])):
            line.append([])
        index_to_pattern.append(line)
        pattern_to_index.append(collections.defaultdict(list))
    # fill the objects
    for _, matches in mega_map.items():
        for match in matches:
            for i, indexes in enumerate(match.indexes):
                for index in indexes:
                    index_to_pattern[i][index].append(match.pattern)
                    pattern_to_index[i][match.pattern].append(index)
    logging.info("index_to_pattern = %s" % index_to_pattern)
    logging.info("pattern_to_index = %s" % pattern_to_index)
    solutions = []
    for index, patterns in enumerate(index_to_pattern[0]):
        for pattern in patterns:
            # find where this pattern can be found in the other strings
            where = []
            for i in range(0, s_length):
                where.append(pattern_to_index[i][pattern])
            combinations = combine(where)
            for combination in combinations:
                # combination[0] contains the index for string in s[0] ;
                # all the characters before the index combination[0] must be 
                # integrated on the left part, but will not match all the 
                # strings. It should be possible to make all the left parts
                # could be compared and grouped but this will be ignored for 
                # now (as being complex).
                pass


def add(a, b):
    return a + b

def prepend(a, b):
    return [a] + b

def s(a, b):
    """Simplification of the similarity matrix."""
    if (a != b):
        return 0
    else:
        return 1

kGoLeft = 1
kGoUp = -1
kGoDiag = 0



# http://en.wikipedia.org/wiki/Needleman-Wunsch_algorithm
def nw_algorithm(a, b, concatenate=add, null='', gap='-', similarity=s, 
    gap_cost=-1):
    """
    Compare two strings (`s1` and `s2`) using Needleman-Wunsch algorithm.
    See http://en.wikipedia.org/wiki/Needleman-Wunsch_algorithm
    """
    f_matrix = []

    def f(i, j, value):
        for _ in range(len(f_matrix), i + 1):
            f_matrix.append([])
        for _ in range(len(f_matrix[i]), j + 1):
            f_matrix[i].append(0)
        f_matrix[i][j] = value

    for i in range(len(a) + 1):
        f(i, 0, gap_cost * i)
    for j in range(len(b) + 1):
        f(0, j, gap_cost * j)

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            match = f_matrix[i - 1][j - 1] + similarity(a[i - 1], b[j - 1])
            delete = f_matrix[i - 1][j] + gap_cost
            insert = f_matrix[i][j - 1] + gap_cost
            f(i, j, max([match, delete, insert]))
#    for row in f_matrix:
#        logging.debug("%s" % row)
    print_array = numpy.array(f_matrix)
    logging.debug("\n%s" % print_array)
    alignement_a = null
    alignement_b = null
    link = ''
    i = len(a)
    j = len(b)
    while ((i > 0) and (j > 0)):
        score = f_matrix[i][j]
        score_diag = f_matrix[i - 1][j - 1]
        score_up = f_matrix[i][j - 1]
        score_left = f_matrix[i - 1][j]

        sim = similarity(a[i - 1], b[j - 1])
        score_diag += sim
        score_left += gap_cost
        score_up += gap_cost

        logging.debug("score = %i" % score)
        logging.debug("score_diag = %i ; sim = %i" %(score_diag, sim))
        logging.debug("score_left = %i" %(score_left))
        logging.debug("score_up = %i" %(score_up))


        go = None
        last_go = None
        if (False):
            if (score == score_diag):
                go = kGoDiag
            if (score == score_left + gap_cost):
                go = kGoLeft
            elif (score == score_up + gap_cost):
                go = kGoUp    
        else:
            equalities = []
            if (score == score_left):
                equalities.append(kGoLeft)
            if (score == score_up):
                equalities.append(kGoUp)
            if (score == score_diag):
                equalities.append(kGoDiag)
            len_equalities = len(equalities)
            if (1 == len_equalities):
                go = equalities[0]
            else:
                if (False):
                    logging.debug("funny alternative 1")
                    equalities = []
                    if (score == score_left):
                        equalities.append(kGoLeft)
                    if (score == score_up):
                        equalities.append(kGoUp)
                    if (score == score_diag):
                        equalities.append(kGoDiag)
                    len_equalities = len(equalities)
                    if (1 == len_equalities):
                        go = equalities[0]
                    elif (1 < len_equalities):
                        if (i > j):
                            if (kGoLeft in equalities):
                                go = kGoLeft
                            else:
                                go = kGoDiag
                        elif (i < j):
                            if (kGoUp in equalities):
                                go = kGoUp
                            else:
                                go = kGoDiag
                        else:
                            if (kGoDiag in equalities):
                                go = kGoDiag
                            else:
                                if ((last_go is not None) and
                                    (kGoDiag != last_go)):
                                    go = -last_go
                                else:
                                    go = kGoUp
                else:
                    logging.debug("funny alternative 2 (comparing further)")
                    equalities = []
                    if (score == score_left):
                        equalities.append(kGoLeft)
                    if (score == score_up):
                        equalities.append(kGoUp)
                    if (score == score_diag):
                        equalities.append(kGoDiag)
                    len_equalities = len(equalities)
                    i_2 = i
                    j_2 = j
                    count_no_up = 0
                    count_no_left = 0
                    while (go is None):
                        if (1 == len(equalities)):
                            go = equalities[0]
                        else:
                            if (j_2 < 2):
                                if (kGoUp in equalities):
                                    equalities.remove(kGoUp)
                                    i_2 -= 1
                                    count_no_up = 0
                                    count_no_left = 0
                                elif (count_no_up > 0):
                                    if (kGoDiag in equalities):
                                        equalities.remove(kGoDiag)
                                        i_2 -= 1
                                        j_2 -= 1
                                else:
                                    count_no_up += 1
                            elif (i_2 < 2):
                                if (kGoLeft in equalities):
                                    equalities.remove(kGoLeft)
                                    j_2 -= 1
                                elif (count_no_left > 0):
                                    if (kGoDiag in equalities):
                                        equalities.remove(kGoDiag)
                                        i_2 -= 1
                                        j_2 -= 1
                                else:
                                    count_no_left += 1
                            else:
                                similarity_up = similarity(
                                    b[j_2 - 1], b[j_2 - 2])
                                similarity_left = similarity(
                                    a[i_2 - 2], a[i_2 - 1])                                
                                if (similarity_left > similarity_up):
                                    if (kGoUp in equalities):
                                        equalities.remove(kGoUp)
                                        i_2 -= 1
                                        count_no_up = 0
                                        count_no_left = 0
                                    elif (count_no_left > 0):
                                        if (kGoDiag in equalities):
                                            equalities.remove(kGoDiag)
                                            i_2 -= 1
                                            j_2 -= 1
                                    else:
                                        count_no_left += 1
                                elif (similarity_left < similarity_up):
                                    if (kGoLeft in equalities):
                                        equalities.remove(kGoLeft)
                                        j_2 -= 1
                                        count_no_up = 0
                                        count_no_left = 0
                                    elif (count_no_up > 0):
                                        if (kGoDiag in equalities):
                                            equalities.remove(kGoDiag)
                                            i_2 -= 1
                                            j_2 -= 1
                                    else:
                                        count_no_up += 1
                                else:
                                    if (kGoUp in equalities):
                                        equalities.remove(kGoUp)
                                    if (kGoLeft in equalities):
                                        equalities.remove(kGoLeft)
        if (kGoDiag == go):
            alignement_a = concatenate(a[i - 1], alignement_a)
            alignement_b = concatenate(b[j - 1], alignement_b)
            if (a[i - 1] == b[j - 1]):
                link = '|' + link
            else:
                link = '#' + link
            i -= 1
            j -= 1
        elif (kGoLeft == go):
            alignement_a = concatenate(a[i - 1], alignement_a)
            alignement_b = concatenate(gap, alignement_b)
            link = ' ' + link
            i -= 1
        elif (kGoUp == go):
            alignement_a = concatenate(gap, alignement_a)
            alignement_b = concatenate(b[j - 1], alignement_b)
            j -= 1
            link = ' ' + link
        last_go = go
        print_array[i][j] = '-0'
    while (i > 0):
        alignement_a = concatenate(a[i - 1], alignement_a)
        alignement_b = concatenate(gap, alignement_b)
        link = 'g' + link
        i -= 1
        print_array[i][j] = '-0'
    while (j > 0):
        alignement_a = concatenate(gap, alignement_a)
        alignement_b = concatenate(b[j - 1], alignement_b)
        link = 'G' + link
        j -= 1
        print_array[i][j] = '-0'
    logging.debug("path taken:\n%s" % print_array)
    def charify(x):
        if (type(x) == type("")):
            if (len(x) == 0):
                return '_'
            return x
        elif ((x is None) or (x.get_char() is None) or
            (len(x.get_char()) == 0)):
            return '_'
        else:
            return x.get_char()
    debug_alignement_a = "".join(map(charify, alignement_a))
    debug_alignement_b = "".join(map(charify, alignement_b))
    logging.debug("alignement_a = %s" % debug_alignement_a)
    logging.debug("              >%s" % link)
    logging.debug("alignement_b = %s" % debug_alignement_b)
    return alignement_a, alignement_b, link

def multi_nw_algorithm_old(strings, concatenate=add, null='', gap='-',
    similarity=s, gap_cost=-1):
    s_length = len(strings)
    if (s_length < 2):
        return strings
    maximum = -1
    index = 0
    for i, string in enumerate(strings):
        if (len(string) > maximum):
            maximum = len(string)
            longest = string
            index = i
    all_pairs = []
    # apply the same confusing algo to the indexes so that we are able to know
    # the index of each string at the end
    order_all_pairs = []
    working = []
    order_working = []
#    reference = []
#    order_reference = []
    for i, string in enumerate(strings):
        if (i != index):
            working.append(string)
            order_working.append(i)
#            reference.append(string)
#            order_reference.append(i)
    removed = []
    order_removed = [] 
    while (len(working) > 0):
        string = working.pop(0)
        order_string = order_working.pop(0)
        removed.append(string)
        order_removed.append(order_string)
        pair = nw_algorithm(longest, string, concatenate, null, gap)
        new_length = len(pair[0])
        if (new_length > maximum):
            maximum = new_length
            for item in removed:
                working.append(item)
            for item in order_removed:
                order_working.append(item)
            removed = []
            order_removed = []
            all_pairs = []
            order_all_pairs = []
            longest = pair[0]
        else:
            all_pairs.append(pair)
            order_all_pairs.append(order_string)

    result = []
    result.append(all_pairs[0][0])
    for pair in all_pairs:
        logging.debug(pair[0])
        logging.debug(pair[2])
        logging.debug(pair[1])
        result.append(pair[1])
    # the algo has mixed the order of the string so we can put them baack now
    order_result = [index] + order_all_pairs
    sorted = []
#    print "result = %s" % result
#    print "order_result = %s" % order_result 
    for o in order_result:
#        print "  result[o] = %s" % result[o]
        sorted.append(result[o])
    logging.debug("exiting multi_nw_algorithm")
    logging.debug(result)
    logging.debug(sorted)
#    print "sorted = %s" % sorted
#    return result
    return sorted

def multi_nw_algorithm(strings, concatenate=add, null='', gap='-',
    similarity=s, gap_cost=-1):
    s_length = len(strings)
    if (s_length < 2):
        return strings
    maximum = -1
    index = 0
    for i, string in enumerate(strings):
        if (len(string) > maximum):
            maximum = len(string)
            index = i
    all = copy.deepcopy(strings)
    all_compared = False
    while (not all_compared):
        loop = True
        i = 0
        while (loop):
            if (index != i):
                s1, s2, pattern = nw_algorithm(
                    all[index], all[i], concatenate, null, gap, similarity, 
                    gap_cost)
                all[index] = s1
                all[i] = s2
                if (len(pattern) > maximum):
                    # the reference (longest) string has changed
                    maximum = len(pattern)
                    # we have to restart all the comparisons
                    loop = False
#                    index = i
                else:
                    i += 1
            else:
                i += 1
            if (s_length == i):
                loop = False
                all_compared = True
    return all

def factorize(analyzed, super_analyzed, categories, custom_gap):
    print "super_analyzed = "
    for sa in super_analyzed:
        string = str(sa)
        print "(%i) %s" % (len(string), string)
    count = len(analyzed)
    indexes = [0] * count
    total_generated = ''
    for k, elements in enumerate(zip(*super_analyzed)):
#        print "^^ " + str(elements)
        restricted = set(elements[:count])
#        print "restricted = %s" % restricted
        differences = len(restricted) - 1
        if (0 == differences):
            if (custom_gap == elements[0]):
                raise Exception("This can not happen: all gap")
        values = []
        increase = []
        for i, index in enumerate(indexes):
            if (custom_gap == elements[i]):
                values.append('')
            else:
                logging.debug("i = %s ; index = %s ; indexes = %s " 
                    % (i, index, indexes))
                logging.debug(categories[i])
                values.append("".join(
                    categories[i][index].get().get_characters()))
                # goto next category
                increase.append(i)
        for inc in increase:
            indexes[inc] += 1
        logging.debug("values = %s" % values)
#        print type(values)
        # for now use default type, tail hanlder and tail type
        #generated = generator.generate(values)
        # more fun
        generated = generator.generate(values, "lax", 
            generator.make_generated_tail, "lax", super_merge=True)
        logging.debug("%% " + generated)
        total_generated += generated
    return total_generated


def translate_categories(categories):
    return map(characters.get_category_as_letter, 
        map(str, categories))

def super_analyze(strings):
    custom_gap = '-'
    analyzed = []
    categories = []
    for string in strings:
        a = analyse.analyse(string)
        analyzed.append(a)
        categories.append(a.get_categories())

    uber_analyzed = multi_nw_algorithm(map(translate_categories, categories), 
        gap=custom_gap, null=[], concatenate=prepend)

    generated = factorize(analyzed, uber_analyzed, categories, custom_gap)
    return generated


def custom_s(a, b):
    if (a == b):
        if (' ' == a):
            return 5
        else:
            return 1
    else:
        if ((' ' == a) or (' ' == b)):
            return -2
        else:
            return 0
