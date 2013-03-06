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

DEBUG = False


class ReString(object):
    re_finder = re.compile("\{(([^{}]+(\{[^}]+\})?)+)\}")

    def __init__(self, string):
        self._string = string
        self._has_re = False
        self._build = []
        last_index = 0
        for matcher in ReString.re_finder.finditer(string):
            self._has_re = True
            if (DEBUG):  # pragma: no cover
                print "'" + string[last_index:matcher.start()] + "'"
                print "'" + string[matcher.start():matcher.end()] + "'"
            if (matcher.start() > 0):
                self._build.append(string[last_index:matcher.start()])
            regex = "(" + matcher.group(1) + ").*"
            if (DEBUG):  # pragma: no cover
                print "build regex: " + regex
            self._build.append(re.compile(regex))
            last_index = matcher.end()
            if (DEBUG):  # pragma: no cover
                print "matcher.start()", matcher.start()
                print "matcher.group(1)", matcher.group(1)
        if ((self._has_re) and (last_index < len(string))):
            self._build.append(string[last_index:])
        if (DEBUG):  # pragma: no cover
            print "string = " + string
            print self._build

    def _rebuild_string(self):
        self._string = ""
        for regex_string in self._build:
            if (type(regex_string) is str):
                self._string += regex_string
            else:
                self._string += "{" + regex_string.pattern[1:-3] + "}"

    def expandtabs(self, tabsize):
        copied = ReString(self._string)
        if (self._has_re):
            for index, regex_string in enumerate(copied._build):
                if (type(regex_string) is str):
                    copied._build[index] = regex_string.expandtabs(tabsize)
            copied._rebuild_string()
        else:
            copied._string = copied._string.expandtabs(tabsize)
        return copied

    def rstrip(self, char=' '):
        copied = ReString(self._string)
        if (self._has_re):
            regex_string = copied._build[-1]
            if (type(regex_string) is str):
                copied._build[-1] = regex_string.rstrip(char)
            copied._rebuild_string()
        else:
            copied._string = copied._string.rstrip(char)
        return copied

    def replace(self, org, to):
        copied = ReString(self._string)
        if (self._has_re):
            for index, regex_string in enumerate(copied._build):
                if (type(regex_string) is str):
                    copied._build[index] = regex_string.replace(org, to)
            copied._rebuild_string()
        else:
            copied._string = self._string.replace(org, to)
        return copied

    def __repr__(self):
        return self._string

    def __str__(self):
        if (DEBUG):  # pragma: no cover
            print "__str__ =", self._string
        return self._string

    def __hash__(self):
        if (DEBUG):  # pragma: no cover
            print "__hash__(" + self._string + ") =", self._string.__hash__()
        return self._string.__hash__()

    def __add__(self, other):
        if (DEBUG):  # pragma: no cover
            print "__add__ =", self._string + repr(other)
        return str(self) + other

    def __radd__(self, other):
        if (DEBUG):  # pragma: no cover
            print "__radd__ =", repr(other) + self._string
        return other + str(self)

    #def __gt__(self, other):
        #print "__gt__('{self}', '{other}')".format(self=self, other=other)
        #return True

    #def __lt__(self, other):
        #print "__lt__('{self}', '{other}')".format(self=self, other=other)
        #return False

    #def __cmp__(self, other):
        #print "__cmp__('{self}', '{other}')".format(self=self, other=other)
        #return 0

    def __eq__(self, other):
        if (DEBUG):  # pragma: no cover
            print "\n__eq__('{self}', '{other}')".format(self=self, other=other)
        if (self._has_re):
            if (other._has_re):
                if (DEBUG):  # pragma: no cover
                    print "__eq__ =", (self._string == other._string)
                return (self._string == other._string)
            else:
                regex = self._build
                real_string = other._string
        else:
            if (other._has_re):
                regex = other._build
                real_string = self._string
            else:
                if (DEBUG):  # pragma: no cover
                    print "__eq__ =", (self._string == other._string)
                return (self._string == other._string)
        # now we can check using regular expressions ...
        #print "The fun begins"
        last_index = 0
        for regex_string in regex:
            if (type(regex_string) is str):
                # standard comparison
                if (DEBUG):  # pragma: no cover
                    print "standard comparison"
                new_index = last_index + len(regex_string)
                sub_real_string = real_string[last_index:new_index]
                if (DEBUG):  # pragma: no cover
                    print "'" + sub_real_string + "'"
                    print "'" + regex_string + "'"
                eq = (sub_real_string == regex_string)
                last_index = new_index
            else:
                if (DEBUG):  # pragma: no cover
                    print "regex comparison"
                    print regex_string
                    print "'" + real_string[last_index:] + "'"
                found = regex_string.match(real_string[last_index:])
                if (found is not None):
                    last_index += len(found.group(1))
                    eq = True
                else:
                    eq = False
                new_index = last_index
            if (not eq):
                if (DEBUG):  # pragma: no cover
                    print "Not matching"
                return False
        if (DEBUG):  # pragma: no cover
            print "new_index =", new_index
            print "real_string =", real_string
            print "len(real_string) =", len(real_string)
            print "__eq__ =", (new_index == len(real_string))
        return (new_index == len(real_string))


def diff(text, reference):
    re_text = map(ReString, text.split('\n'))
    re_reference = map(ReString, reference.split('\n'))
    #print re_text
    #print re_reference
    #print "\n//START DIFF\\\\\n"
    difference = difflib.unified_diff(re_text, re_reference)
    #difference = difflib.ndiff(re_text, re_reference)
    return '\n'.join(list(difference))


def diff2(text, reference):
    re_text = map(ReString, text.split('\n'))
    re_reference = map(ReString, reference.split('\n'))
    #print re_text
    #print re_reference
    #difference = difflib.unified_diff(re_text, re_reference)
    difference = difflib.ndiff(re_text, re_reference)
    return '\n'.join(list(difference))


def diff3(text, reference):
    re_text = map(ReString, text.split('\n'))
    re_reference = map(ReString, reference.split('\n'))
    #print re_text
    #print re_reference
    #difference = difflib.unified_diff(re_text, re_reference)
    difference = difflib.HtmlDiff().make_file(re_text, re_reference)
    return difference


def equal(text, reference):
    return (len(diff(text, reference)) == 0)


def main():
    import sys
    import os
    import optparse

    parser = optparse.OptionParser(usage='usage: %prog file1 file2',
                                   description='Compute the difference '
                                   'between two files, one of which can '
                                   'contain emeded regular expressions '
                                   'between angle brackets (python re), '
                                   'like "Today is {\w+}.". Warning: an extra '
                                   'line containing "<EOF>" is added to have '
                                   'better matches (but the principle is not '
                                   'nice).')
    (options, arguments) = parser.parse_args()

    def is_file_missing(file_name):
        if (not os.path.exists(file_name)):
            sys.stderr.write("No such file or directory: '" + file_name + "'\n")
            return True
        return False
    if (len(sys.argv) == 3):
        quit = is_file_missing(arguments[0])
        quit |= is_file_missing(arguments[1])
        if (quit):
            sys.exit(1)
        with open(sys.argv[1]) as file1:
            with open(sys.argv[2]) as file2:
                # The extra line added alows to have a match at the end to
                # make the algorithm compute extra differences (and a better
                # match in the end).
                print diff(file1.read() + "\n<EOF>", file2.read() + "\n<EOF>")
    else:
        sys.stderr.write("Sorry the program does not understand the "
                         "parameters.\nThe expected syntax is :\n" +
                         sys.argv[0] + " file1 file2\n")
        sys.exit(1)

if ("__main__" == __name__):  # pragma: no cover
    main()
