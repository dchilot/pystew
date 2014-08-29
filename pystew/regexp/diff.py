r"""Objects and functions used to perform regular expressions based diff.

The syntax to make a piece of text act as a regular expression is to
enclose it between brackets.

Examples::

    {\d}
    {[A-Z] some text [a-z]}

The python regular expressions are used but you cannot use everything
as each regular expression is independent.
Each regular expression is for at most one line.
Regular expressions are case sensitive.
"""

import re
import difflib
import logging

if (True):
    logging.basicConfig(level=logging.WARNING)
else:  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG)


class ReString(object):

    """Class that behaves a little a :class:`str`."""

    re_finder = re.compile(r"""(^|[^\\])\{(([^{}]+(\{[^}]+\})?)+)\}""")

    def __init__(self, string):
        """
        Constructor.

        :param string:
            The :class:`str` to be analysed and wrapped.
        """
        self._string = string
        self._has_re = False
        self._build = []
        last_index = 0
        for matcher in ReString.re_finder.finditer(string):
            last_index = self.__extract(string, matcher, last_index)
        if ((self._has_re) and (last_index < len(string))):
            self._build.append(string[last_index:])
        logging.debug(
            "string = " + string + "\n" +
            str(self._build))

    def __extract(self, string, matcher, last_index):
        self._has_re = True
        offseted_string = string[last_index:matcher.start()] + matcher.group(1)
        logging.debug(
            "'" + offseted_string + "'\n"
            "'" + string[matcher.start() +
                         len(matcher.group(1)):matcher.end()] + "'")
        if (len(offseted_string) > 0):
            self._build.append(offseted_string)
        if ('*' == matcher.group(2)):
            next_index = matcher.end()
            if (next_index < len(string)):
                next_char = string[next_index]
                pattern = '[^{next_char}]*'.format(next_char=next_char)
            else:
                pattern = '.*'
        else:
            pattern = matcher.group(2)
        regex = "(" + pattern + ").*"
        regex = regex.replace("(local)", "")
        logging.debug("build regex: " + regex)
        user_regex = re.compile(regex)
        self._build.append(user_regex)
        last_index = matcher.end()
        logging.debug(
            "matcher.start()" + str(matcher.start()) + "\n"
            "matcher.group(2)" + str(matcher.group(2)) + "\n"
            'user_regex.pattern =' + str(user_regex.pattern))
        return last_index

    def _rebuild_string(self):
        self._string = ""
        for regex_string in self._build:
            if (type(regex_string) is str):
                self._string += regex_string
            else:
                self._string += "{" + regex_string.pattern[1:-3] + "}"

    def expandtabs(self, tabsize):
        """Like method from :class:`str` (:func:`str.expandtabs`)."""
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
        """Like method from :class:`str` (:func:`str.rstrip`)."""
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
        """Like method from :class:`str` (:func:`str.replace`)."""
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
        """Wronly implemented :meth:`__repr__`."""
        return self._string

    def __str__(self):
        """Implemented :meth:`__str__`."""
        logging.debug("__str__ = " + self._string)
        return self._string

    def __hash__(self):
        """Implemented :meth:`__hash__`."""
        logging.debug(
            "__hash__(" + self._string + ") = " + str(self._string.__hash__()))
        return self._string.__hash__()

    def __add__(self, other):
        """Implementation of the operator."""
        logging.debug("__add__ = " + self._string + repr(other))
        return str(self) + other

    def __radd__(self, other):
        """Implementation of the operator."""
        logging.debug("__radd__ = " + repr(other) + self._string)
        return other + str(self)

    @staticmethod
    def __regular_expression_eq(regex, real_string):
        last_index = 0
        for regex_string in regex:
            if (type(regex_string) is str):
                # standard comparison
                logging.debug("standard comparison")
                new_index = last_index + len(regex_string)
                sub_real_string = real_string[last_index:new_index]
                logging.debug(
                    "'" + sub_real_string + "'\n" +
                    "'" + regex_string + "'")
                eq = (sub_real_string == regex_string)
                last_index = new_index
            else:
                logging.debug(
                    "regex comparison\n" +
                    str(regex_string) + "\n" +
                    str(regex_string.pattern) + "\n" +
                    "'" + real_string[last_index:] + "'")
                found = regex_string.match(real_string[last_index:])
                if (found is not None):
                    last_index += len(found.group(1))
                    eq = True
                else:
                    eq = False
                new_index = last_index
            if (not eq):
                logging.debug("Not matching")
                return False
        logging.debug(
            "new_index = " + str(new_index) + "\n" +
            "real_string = " + real_string + "\n" +
            "len(real_string) = " + str(len(real_string)) + "\n" +
            "__eq__ = " + str((new_index == len(real_string))))
        return (new_index == len(real_string))

    def __eq__(self, other):
        """Implementation of the operator."""
        logging.debug("\n__eq__('{self}', '{other}')".format(
            self=self, other=other))
        if (self._has_re):
            if (other._has_re):
                logging.debug("__eq__ = " + str(self._string == other._string))
                return (self._string == other._string)
            else:
                regex = self._build
                real_string = other._string
        else:
            if (other._has_re):
                regex = other._build
                real_string = self._string
            else:
                logging.debug("__eq__ = " + str(self._string == other._string))
                return (self._string == other._string)
        # now we can check using regular expressions ...
        return ReString.__regular_expression_eq(regex, real_string)


def raw_diff(text, reference, lines_of_context=3):
    """Return the unified difference as a generator.

    :param text: The text to be compared.
    :type text: :class:`str`

    :param reference: The text to compare to.
    :type text: :class:`str`

    :return: Unified diff.
    :rtype: generator (:class:`str`)
    """
    re_text = map(lambda x: ReString(x + '\n'), text.split('\n'))
    re_reference = map(lambda x: ReString(x + '\n'), reference.split('\n'))
    difference = difflib.unified_diff(re_text, re_reference,
                                      n=lines_of_context)
    return difference


def diff(text, reference, lines_of_context=3):
    """Return the unified difference as a big string.

    :param text: The text to be compared.
    :type text: :class:`str`

    :param reference: The text to compare to.
    :type reference: :class:`str`

    :return: Unified diff.
    :rtype: :class:`str`
    """
    return ''.join(list(raw_diff(text, reference, lines_of_context)))


def raw_diff2(text, reference):
    """Return the numbered difference as a big string.

    ..Warning:
        This is not a raw diff (probably wrongly named after experimenting).

    :param text: The text to be compared.
    :type text: :class:`str`

    :param reference: The text to compare to.
    :type reference: :class:`str`

    :return: Numbered diff.
    :rtype: generator (:class:`str`)
    """
    re_text = map(lambda x: ReString(x + '\n'), text.split('\n'))
    re_reference = map(lambda x: ReString(x + '\n'), reference.split('\n'))
    difference = difflib.ndiff(re_text, re_reference)
    return ''.join(list(difference))


def diff2(text, reference):
    """Useless."""
    return ''.join(list(raw_diff2(text, reference)))


def raw_diff3(text, reference, lines_of_context=5):
    """Return the HTML difference as a generator.

    :param text: The text to be compared.
    :type text: :class:`str`

    :param reference: The text to compare to.
    :type reference: :class:`str`

    :return: HTML diff.
    :rtype: generator (:class:`str`)
    """
    re_text = map(lambda x: ReString(x + '\n'), text.split('\n'))
    re_reference = map(lambda x: ReString(x + '\n'), reference.split('\n'))
    difference = difflib.HtmlDiff().make_file(re_text, re_reference,
                                              numlines=lines_of_context)
    return difference


def diff3(text, reference, lines_of_context=3):
    """Return the HTML difference as a big string.

    :param text: The text to be compared.
    :type text: :class:`str`

    :param reference: The text to compare to.
    :type reference: :class:`str`

    :return: HTML diff.
    :rtype: :class:`str`
    """
    return ''.join(list(raw_diff3(text, reference, lines_of_context)))


def raw_diff4(text, reference, lines_of_context=3):
    """Return the contextual difference as a generator.

    :param text: The text to be compared.
    :type text: :class:`str`

    :param reference: The text to compare to.
    :type reference: :class:`str`

    :return: contextual diff.
    :rtype: generator (:class:`str`)
    """
    re_text = map(lambda x: ReString(x + '\n'), text.split('\n'))
    re_reference = map(lambda x: ReString(x + '\n'), reference.split('\n'))
    difference = difflib.context_diff(re_text, re_reference,
                                      n=lines_of_context)
    return difference


def diff4(text, reference, lines_of_context=3):
    """Return the contextual difference as a big string.

    :param text: The text to be compared.
    :type text: :class:`str`

    :param reference: The text to compare to.
    :type reference: :class:`str`

    :return: contextual diff.
    :rtype: generator (:class:`str`)
    """
    return ''.join(list(raw_diff4(text, reference, lines_of_context)))


def equal(text, reference):
    """Utility fonction to check that there are no differences."""
    return (len(diff(text, reference)) == 0)


def main():
    """Parse the input and display the result of the diff performed."""
    import sys
    import os
    import optparse

    parser = optparse.OptionParser(usage='usage: %prog file1 file2',
                                   description='Compute the difference '
                                   'between two files, one of which can '
                                   'contain emeded regular expressions '
                                   'between angle brackets (python re), '
                                   'like "Today is {\w+}.".')
    parser.add_option('--diff-mode', default="1")
    (options, arguments) = parser.parse_args()

    def is_file_missing(file_name):
        if (not os.path.exists(file_name)):
            sys.stderr.write(
                "No such file or directory: '" + file_name + "'\n")
            return True
        return False
    if (len(arguments) == 2):
        quit = is_file_missing(arguments[0])
        quit |= is_file_missing(arguments[1])
        if (quit):
            sys.exit(1)
        with open(sys.argv[1]) as file1:
            with open(sys.argv[2]) as file2:
                # The extra line added alows to have a match at the end to
                # make the algorithm compute extra differences (and a better
                # match in the end).
                if ("2" == options.diff_mode):
                    print ''.join(list(diff2(file1.read(), file2.read())))
                elif ("3" == options.diff_mode):
                    print ''.join(list(diff3(file1.read(), file2.read())))
                elif ("4" == options.diff_mode):
                    print ''.join(list(diff4(file1.read(), file2.read())))
                else:
                    print diff(file1.read(), file2.read())
    else:
        sys.stderr.write("Sorry the program does not understand the "
                         "parameters.\nThe expected syntax is :\n" +
                         sys.argv[0] + " file1 file2\n")
        sys.exit(1)

if ("__main__" == __name__):  # pragma: no cover
    main()
