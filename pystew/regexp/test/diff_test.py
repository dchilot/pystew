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

import unittest
import StringIO

# make sure the local version is used instead of the one in the python lib folder
# http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
import os
import sys
import inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "..", "..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import pystew.regexp

#from nose.tools import raises
from nose.tools import assert_equal
from nose.tools import assert_not_equal


class ReStringTests(unittest.TestCase):
    def test_1(self):
        re_string = pystew.regexp.ReString("Toto")
        assert_equal("Toto", str(re_string))

    def test_2(self):
        re1 = pystew.regexp.ReString("This is a string")
        re2 = pystew.regexp.ReString("This is a string")
        re3 = pystew.regexp.ReString("This is a different string")
        assert_equal(re1, re2)
        assert_not_equal(re1, re3)

    def test_3(self):
        re1 = pystew.regexp.ReString("This is a string with something.")
        re2 = pystew.regexp.ReString("This is a string with {\w+}.")
        re3 = pystew.regexp.ReString("This is a string with {\w+}.")
        re4 = pystew.regexp.ReString("This is a string with something that does not match.")
        assert_equal(re1, re2)
        assert_equal(re1, re3)
        assert_not_equal(re2, re4)

    def test_4(self):
        re1 = pystew.regexp.ReString("Some text.")
        re2 = pystew.regexp.ReString("{.*}")
        assert_equal(re1, re2)

    def test_expandtabs(self):
        strings = ["	tabs in here	", "No tabs here"]
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.expandtabs(2), str(restring.expandtabs(2)))

    def test_expandtabs_2(self):
        strings = ["\ttabs in here\t", "No tabs here"]
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.expandtabs(2), str(restring.expandtabs(2)))

    def test_expandtabs_3(self):
        restring = pystew.regexp.ReString("""{\w.*}\t""")
        assert_equal("{\w.*}     ", str(restring.expandtabs(5)))

    def test_rstrip(self):
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
        assert_equal("{.*}", str(pystew.regexp.ReString("{.*} ").rstrip()))
        assert_equal("{.*} ", str(pystew.regexp.ReString("{.*} ").rstrip('x')))
        assert_equal("}{{.*}", str(pystew.regexp.ReString("}{{.*}").rstrip('}')))
        assert_equal("}{{.*}", str(pystew.regexp.ReString("}{{.*}}").rstrip('}')))
        assert_equal("}{{.*}", str(pystew.regexp.ReString("}{{.*}}}}}}").rstrip('}')))

    def test_replace(self):
        strings = ["lorem ipsum ", "lor em ipsum", "rem {.*} rem", "{toto\d+}r"]
        for string in strings:
            restring = pystew.regexp.ReString(string)
            assert_equal(string.replace('rem', 'x'), str(restring.replace('rem', 'x')))

    def test_replace_2(self):
        assert_equal("{.*}", str(pystew.regexp.ReString("{.*}").replace("{.*}", "-")))
        assert_equal("-{.*}-", str(pystew.regexp.ReString(".*{.*}.*").replace(".*", "-")))


class Tests(unittest.TestCase):
    def test_1(self):
        import datetime
        now = datetime.datetime.now()
        text = """This is a fake text.
Today is {now} and this should not prevent a match.
Let's add some text at the end.""".format(now=now)
        reference = """This is a fake text.
Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and this should not prevent a match.
Let's add some text at the end."""
        print text
        print reference
        assert(pystew.regexp.equal(text, reference))
        nearly = """This is a fake text.
Today is 2012-12-15 15:42:43.60400 and this should not prevent a match.
Let's add some text at the end.""".format(now=now)
        assert(not pystew.regexp.equal(nearly, reference))
        assert_equal(pystew.regexp.diff(nearly, reference), """\
--- """ + """

+++ """ + """

@@ -1,3 +1,3 @@

 This is a fake text.
-Today is 2012-12-15 15:42:43.60400 and this should not prevent a match.
+Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and this should not prevent a match.
 Let's add some text at the end.""")
        reference2 = """This is a fake text.
Added line !
Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and this should not prevent a match.
Let's add some text at the end."""
        print "diff with added line"
        assert_equal(pystew.regexp.diff(text, reference2), """\
--- """ + """

+++ """ + """

@@ -1,3 +1,4 @@

 This is a fake text.
+Added line !
 Today is {now} and this should not prevent a match.
 Let's add some text at the end.""".format(now=now))
        print "diff with added line the revenge"
        assert_equal(pystew.regexp.diff(reference2, text), """\
--- """ + """

+++ """ + """

@@ -1,4 +1,3 @@

 This is a fake text.
-Added line !
 Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and this should not prevent a match.
 Let's add some text at the end.""")
        text2 = """This is a fake text.
This is a new line !
Today is {now} and this should not prevent a match.
Let's add some text at the end.""".format(now=now)
        print "diff with added line 2"
        assert_equal(pystew.regexp.diff(text2, reference), """\
--- """ + """

+++ """ + """

@@ -1,4 +1,3 @@

 This is a fake text.
-This is a new line !
 Today is {now} and this should not prevent a match.
 Let's add some text at the end.""".format(now=now))
        print "diff with added line the revenge 2"
        assert_equal(pystew.regexp.diff(reference, text2), """\
--- """ + """

+++ """ + """

@@ -1,3 +1,4 @@

 This is a fake text.
+This is a new line !
 Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and this should not prevent a match.
 Let's add some text at the end.""")
        print "diff with added line 3"
        assert_equal(pystew.regexp.diff(text2, reference2), """\
--- """ + """

+++ """ + """

@@ -1,4 +1,4 @@

 This is a fake text.
-This is a new line !
+Added line !
 Today is {now} and this should not prevent a match.
 Let's add some text at the end.""".format(now=now))
        print "diff with added line the revenge 3"
        assert_equal(pystew.regexp.diff(reference2, text2), """\
--- """ + """

+++ """ + """

@@ -1,4 +1,4 @@

 This is a fake text.
-Added line !
+This is a new line !
 Today is {\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}} and this should not prevent a match.
 Let's add some text at the end.""")
        #assert(False)

    def test_2(self):
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
        display_text = "  " + text.replace("\n", "\n  ")
        assert_equal(display_text, pystew.regexp.diff2(text, text2))


class TestMain(unittest.TestCase):
    def setUp(self):
        self._sys_argv = sys.argv
        self._sys_stderr = sys.stderr
        sys.stderr = StringIO.StringIO()
        self._sys_stdout = sys.stdout
        sys.stdout = StringIO.StringIO()

    def tearDown(self):
        sys.argv = self._sys_argv
        sys.stderr.close()
        sys.stderr = self._sys_stderr
        sys.stdout.close()
        sys.stdout = self._sys_stdout

    def test_errors(self):
        # there must be a better way to give arguments ...
        sys.argv = ["diff"]
        with self.assertRaises(SystemExit):
            pystew.regexp.main()
        with self.assertRaises(SystemExit):
            sys.argv.append("a")
            pystew.regexp.main()
        with self.assertRaises(SystemExit):
            sys.argv.append(os.path.join(cmd_subfolder, "regexp", "diff.py"))
            pystew.regexp.main()
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
        f1 = os.path.join('test', 'reference.txt')
        f2 = os.path.join('test', 'compared.txt')
        sys.argv = ["diff", f1, f2]
        pystew.regexp.main()
        assert_equal("\n", sys.stdout.getvalue())
        assert_equal("", sys.stderr.getvalue())


class TestBin(unittest.TestCase):
    def test_equal(self):
        import subprocess
        f1 = os.path.join('test', 'reference.txt')
        f2 = os.path.join('test', 'compared.txt')
        call = subprocess.Popen(["python.exe", "diff.py", f1, f2], stdout=subprocess.PIPE)
        stdout, stderr = call.communicate()
        print stdout
        print "----"
        print stderr
        #assert_equal('', stdout)
        assert_equal('\r\n', stdout)

    def test_different(self):
        import subprocess
        f1 = os.path.join('test', 'reference.txt')
        f2 = os.path.join('test', 'different.txt')
        call = subprocess.Popen(["python.exe", "diff.py", f1, f2], stdout=subprocess.PIPE)
        stdout, stderr = call.communicate()
        print stdout
        print "----"
        print stderr
        assert_equal('--- \r\n\r\n+++ \r\n\r\n@@ -1,6 +1,5 @@\r\n\r\n Line 1 {\\d+}\r\n Line 2 {\\d{1,2}}\r\n Line 3 {\\d{1}}\r\n-Line 4 {\\d{1}}\r\n {.*}\r\n <EOF>\r\n', stdout)
