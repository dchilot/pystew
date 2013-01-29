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

import re
import difflib


class ReString(object):
    re_finder = re.compile("\{(([^{}]+(\{[^}]+\})?)+)\}")

    def __init__(self, string):
        self._string = string
        self._has_re = False
        self._build = []
        last_index = 0
        for matcher in ReString.re_finder.finditer(string):
            self._has_re = True
            #print "'" + string[last_index:matcher.start()] + "'"
            #print "'" + string[matcher.start():matcher.end()] + "'"
            if (matcher.start() > 0):
                self._build.append(string[last_index:matcher.start()])
            regex = "(" + matcher.group(1) + ").*"
            #print "build regex: " + regex
            self._build.append(re.compile(regex))
            last_index = matcher.end()
            #print matcher.start()
            #print matcher.group(1)
        if ((self._has_re) and (last_index < len(string))):
            self._build.append(string[last_index:])
        #print "string = " + string
        #print self._build

    def __str__(self):
        return self._string

    def __hash__(self):
        return self._string.__hash__()

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

    #def __lt__(self, other):
        #print "__lt__('{self}', '{other}')".format(self=self, other=other)
        #return False

    #def __cmp__(self, other):
        #print "__cmp__('{self}', '{other}')".format(self=self, other=other)
        #return 0

    def __eq__(self, other):
        #print "__eq__('{self}', '{other}')".format(self=self, other=other)
        if (self._has_re):
            if (other._has_re):
                return (self._string == other._string)
            else:
                regex = self._build
                real_string = other._string
        else:
            if (other._has_re):
                regex = other._build
                real_string = self._string
            else:
                return (self._string == other._string)
        # now we can check using regular expressions ...
        #print "The fun begins"
        last_index = 0
        for regex_string in regex:
            if (type(regex_string) is str):
                # standard comparison
                #print "standard comparison"
                new_index = last_index + len(regex_string)
                sub_real_string = real_string[last_index:new_index]
                #print "'" + sub_real_string + "'"
                #print "'" + regex_string + "'"
                eq = (sub_real_string == regex_string)
                last_index = new_index
            else:
                #print "regex comparison"
                #print regex_string
                #print "'" + real_string[last_index:] + "'"
                found = regex_string.match(real_string[last_index:])
                if (found is not None):
                    last_index += len(found.group(1))
                    eq = True
                else:
                    eq = False
            if (not eq):
                #print "Not matching"
                return False
        return (new_index == len(real_string))


def diff(text, reference):
    re_text = map(ReString, text.split('\n'))
    re_reference = map(ReString, reference.split('\n'))
    #print re_text
    #print re_reference
    difference = difflib.unified_diff(re_text, re_reference)
    #difference = difflib.ndiff(re_text, re_reference)
    #print difference
    return '\n'.join(list(difference))


def diff2(text, reference):
    re_text = map(str, text.split('\n'))
    re_reference = map(str, reference.split('\n'))
    #print re_text
    #print re_reference
    #difference = difflib.unified_diff(re_text, re_reference)
    difference = difflib.ndiff(re_text, re_reference)
    #print difference
    return '\n'.join(list(difference))


def equal(text, reference):
    return (len(diff(text, reference)) == 0)


def main():
    import sys
    if (len(sys.argv) == 3):
        with open(sys.argv[1]) as file1:
            with open(sys.argv[2]) as file2:
                print diff(file1.read(), file2.read())

if ("__main__" == __name__):
    main()
