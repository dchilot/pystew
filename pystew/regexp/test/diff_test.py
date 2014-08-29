"""Tests for diff module."""

import unittest
import StringIO
import os
import sys
import inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
    inspect.getfile(inspect.currentframe()))[0], "..", "..")))

import pystew.regexp

from nose.tools import assert_equal
from nose.tools import assert_not_equal


class SpaceFinder(unittest.TestCase):

    """
    Base class for the tests.

    The sole purpose of this class is to know if an extra space
    has to be inserted in the diffs.
    """

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(SpaceFinder, self).__init__(*args, **kwargs)
        import difflib
        diff = difflib.unified_diff([""], [" "], lineterm='')
        self._spaces = diff.next()[3:]


class ReStringTests(SpaceFinder):
    """Test for :class:`ReString`."""

    def test_1(self):
        """Equality for simple string."""
        re_string = pystew.regexp.ReString("Toto")
        assert_equal("Toto", str(re_string))

    def test_2(self):
        """Equality for simple objects."""
        re1 = pystew.regexp.ReString("This is a string")
        re2 = pystew.regexp.ReString("This is a string")
        re3 = pystew.regexp.ReString("This is a different string")
        assert_equal(re1, re2)
        assert_not_equal(re1, re3)

    def test_3(self):
        """Equality with regular expressions."""
        re1 = pystew.regexp.ReString("This is a string with something.")
        re2 = pystew.regexp.ReString("This is a string with {\w+}.")
        re3 = pystew.regexp.ReString("This is a string with {\w+}.")
        re4 = pystew.regexp.ReString(
            "This is a string with something that does not match.")
        assert_equal(re1, re2)
        assert_equal(re1, re3)
        assert_not_equal(re2, re4)

    def test_4(self):
        """Special test to match everything."""
        re1 = pystew.regexp.ReString("Some text.")
        re2 = pystew.regexp.ReString("{.*}")
        assert_equal(re1, re2)

    def test_expandtabs(self):
        """Make sure expandtabs does nothing if nothing has to be expanded."""
        strings = ["    tabs in here    ", "No tabs here"]
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.expandtabs(2), str(restring.expandtabs(2)))

    def test_expandtabs_2(self):
        """Simple tabulation expansion."""
        strings = ["\ttabs in here\t", "No tabs here"]
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.expandtabs(2), str(restring.expandtabs(2)))

    def test_expandtabs_3(self):
        """Tabulation expansion with a regular expression."""
        restring = pystew.regexp.ReString("""{\w.*}\t""")
        assert_equal("{\w.*}     ", str(restring.expandtabs(5)))

    def test_rstrip(self):
        """Test rstrip with simple strings."""
        strings = ["lorem ipsum ", "lorem ipsum"]
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.rstrip(), str(restring.rstrip()))
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.rstrip('m'), str(restring.rstrip('m')))
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.rstrip('x'), str(restring.rstrip('x')))

    def test_rstrip_2(self):
        """Test rstrip with regular expressions."""
        assert_equal(
            "{.*}",
            str(pystew.regexp.ReString("{.*} ").rstrip()))
        assert_equal(
            "{.*} ",
            str(pystew.regexp.ReString("{.*} ").rstrip('x')))
        assert_equal(
            "}{{.*}",
            str(pystew.regexp.ReString("}{{.*}").rstrip('}')))
        assert_equal(
            "}{{.*}",
            str(pystew.regexp.ReString("}{{.*}}").rstrip('}')))
        assert_equal(
            "}{{.*}",
            str(pystew.regexp.ReString("}{{.*}}}}}}").rstrip('}')))

    def test_replace(self):
        """Test replace behaves as expected."""
        strings = [
            "lorem ipsum ",
            "lor em ipsum",
            "rem {.*} rem",
            "{toto\d+}r"
        ]
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(
                string.replace('rem', 'x'),
                str(restring.replace('rem', 'x')))

    def test_replace_2(self):
        """Make sure replacement are not performed in regular expressions."""
        assert_equal(
            "{.*}",
            str(pystew.regexp.ReString("{.*}").replace("{.*}", "-")))
        assert_equal(
            "-{.*}-",
            str(pystew.regexp.ReString(".*{.*}.*").replace(".*", "-")))


class Tests(SpaceFinder):

    """Tests for the module functions."""

    def test_1(self):
        """Simple regular expression differences."""
        import datetime
        now = datetime.datetime.now()
        text = """This is a fake text.
Today is {now} and still matches.
Let's add some text at the end.""".format(now=now)
        reference = """This is a fake text.
Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and still matches.
Let's add some text at the end."""
        print text
        print reference
        assert(pystew.regexp.equal(text, reference))
        nearly = """This is a fake text.
Today is 2012-12-15 15:42:43.60400 and still matches.
Let's add some text at the end.""".format(now=now)
        assert(not pystew.regexp.equal(nearly, reference))
        assert_equal(pystew.regexp.diff(nearly, reference), """\
---""" + self._spaces + """
+++""" + self._spaces + """
@@ -1,3 +1,3 @@
 This is a fake text.
-Today is 2012-12-15 15:42:43.60400 and still matches.
+Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and still matches.
 Let's add some text at the end.
""")
        reference2 = """This is a fake text.
Added line !
Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and still matches.
Let's add some text at the end."""
        print "diff with added line"
        assert_equal(pystew.regexp.diff(text, reference2), """\
---""" + self._spaces + """
+++""" + self._spaces + """
@@ -1,3 +1,4 @@
 This is a fake text.
+Added line !
 Today is {now} and still matches.
 Let's add some text at the end.
""".format(now=now))
        print "diff with added line the revenge"
        assert_equal(pystew.regexp.diff(reference2, text), """\
---""" + self._spaces + """
+++""" + self._spaces + """
@@ -1,4 +1,3 @@
 This is a fake text.
-Added line !
 Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and still matches.
 Let's add some text at the end.
""")
        text2 = """This is a fake text.
This is a new line !
Today is {now} and still matches.
Let's add some text at the end.""".format(now=now)
        print "diff with added line 2"
        assert_equal(pystew.regexp.diff(text2, reference), """\
---""" + self._spaces + """
+++""" + self._spaces + """
@@ -1,4 +1,3 @@
 This is a fake text.
-This is a new line !
 Today is {now} and still matches.
 Let's add some text at the end.
""".format(now=now))
        print "diff with added line the revenge 2"
        assert_equal(pystew.regexp.diff(reference, text2), """\
---""" + self._spaces + """
+++""" + self._spaces + """
@@ -1,3 +1,4 @@
 This is a fake text.
+This is a new line !
 Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and still matches.
 Let's add some text at the end.
""")
        print "diff with added line 3"
        assert_equal(pystew.regexp.diff(text2, reference2), """\
---""" + self._spaces + """
+++""" + self._spaces + """
@@ -1,4 +1,4 @@
 This is a fake text.
-This is a new line !
+Added line !
 Today is {now} and still matches.
 Let's add some text at the end.
""".format(now=now))
        print "diff with added line the revenge 3"
        assert_equal(pystew.regexp.diff(reference2, text2), """\
---""" + self._spaces + """
+++""" + self._spaces + """
@@ -1,4 +1,4 @@
 This is a fake text.
-Added line !
+This is a new line !
 Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and still matches.
 Let's add some text at the end.
""")

    def test_2(self):
        """Make sure that a regular expression does not shadow differences."""
        text = """Line 1.
Line 2.
{[A-Z]}onus line
Line 3.
Line 4."""
        text2 = """Line 1.
Line 2.
Bonus line.
Line 3.
Line 4."""
        print "diff1"
        print pystew.regexp.diff(text, text2)
        assert(not pystew.regexp.equal(text, text2))

    def test_3(self):
        """Test output with no differences."""
        text = """Line 1.
Line 2.
Line 3.
Line 4."""
        text2 = """Line 1.
Line 2.
{.*}
Line 4."""
        print "diff1"
        print pystew.regexp.diff(text, text2)
        assert_equal("", pystew.regexp.diff(text, text2))
        assert(pystew.regexp.equal(text, text2))
        print "diff2"
        print pystew.regexp.diff2(text, text2)
        display_text = "  " + text.replace("\n", "\n  ") + '\n'
        assert_equal(display_text, pystew.regexp.diff2(text, text2))


class TestMain(SpaceFinder):

    """Tests for the main method."""

    def setUp(self):
        """Run some code when starting each test."""
        self._sys_argv = sys.argv
        self._sys_stderr = sys.stderr
        sys.stderr = StringIO.StringIO()
        self._sys_stdout = sys.stdout
        sys.stdout = StringIO.StringIO()

    def tearDown(self):
        """Run some code when finishing each test."""
        sys.argv = self._sys_argv
        sys.stderr.close()
        sys.stderr = self._sys_stderr
        sys.stdout.close()
        sys.stdout = self._sys_stdout

    def test_errors(self):
        """Test some error cases."""
        # there must be a better way to give arguments ...
        sys.argv = ["diff"]
        self.assertRaises(SystemExit, pystew.regexp.main)
        sys.argv.append("a")
        self.assertRaises(SystemExit, pystew.regexp.main)
        sys.argv.append(os.path.join(cmd_subfolder, "regexp", "diff.py"))
        self.assertRaises(SystemExit, pystew.regexp.main)
        assert_equal("""Sorry the program does not understand the parameters.
The expected syntax is :
diff file1 file2
Sorry the program does not understand the parameters.
The expected syntax is :
diff file1 file2
No such file or directory: 'a'
""", sys.stderr.getvalue())
        assert_equal("", sys.stdout.getvalue())

    def test_ok(self):
        """Test a basic working use."""
        test_dir = os.path.join(cmd_subfolder, 'regexp', 'test')
        f1 = os.path.join(test_dir, 'reference.txt')
        f2 = os.path.join(test_dir, 'compared.txt')
        sys.argv = [os.path.join(cmd_subfolder, 'regexp', "diff.py"), f1, f2]
        pystew.regexp.main()
        assert_equal("\n", sys.stdout.getvalue())
        assert_equal("", sys.stderr.getvalue())


class TestBin(SpaceFinder):

    """Tests for the script."""

    def test_equal(self):
        """Test files that have no differences."""
        import subprocess
        test_dir = os.path.join(cmd_subfolder, 'regexp', 'test')
        f1 = os.path.join(test_dir, 'reference.txt')
        f2 = os.path.join(test_dir, 'compared.txt')
        call = subprocess.Popen(["python",
                                 os.path.join(cmd_subfolder,
                                              'regexp', "diff.py"),
                                 f1, f2],
                                stdout=subprocess.PIPE)
        stdout, stderr = call.communicate()
        print stdout
        print "----"
        print stderr
        if ('win32' == sys.platform):
            eol = '\r\n'
        else:
            eol = '\n'
        assert_equal(eol, stdout)

    def test_different(self):
        """Test files that are different."""
        import subprocess
        test_dir = os.path.join(cmd_subfolder, 'regexp', 'test')
        f1 = os.path.join(test_dir, 'reference.txt')
        f2 = os.path.join(test_dir, 'different.txt')
        call = subprocess.Popen(
            ["python",
             os.path.join(cmd_subfolder, 'regexp', "diff.py"),
             f1, f2],
            stdout=subprocess.PIPE)
        stdout, stderr = call.communicate()
        print stdout
        print "----"
        print stderr
        if ('win32' == sys.platform):
            eol = '\r\n'
        else:
            eol = '\n'
        assert_equal('---' + self._spaces + eol +
                     '+++' + self._spaces + eol +
                     '@@ -2,4 +2,3 @@' + eol +
                     ' Line 2 {\\d{1,2}}' + eol +
                     ' Line 3 {\\d{1}}' + eol +
                     ' Line 4 {\\d{1}}' + eol +
                     '-{.*}' + eol * 2, stdout)
