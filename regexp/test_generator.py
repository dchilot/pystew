###############################################################################
#                                                                             #
#                           Ugly tests part follows                           #
#                                                                             #
###############################################################################
import generator
import logger
import logging

def check_equal(expected, gotten):
    """`expected`: string containing the expected result.
    `gotten`: string containing what has realy been computed.
    Logs "OK" if `expected` and `gotten` are equal, and an error message 
    otherwise."""
    if (expected != gotten):
        logging.error("Error: expected '" + str(expected) + "' but found '" + 
            str(gotten) + "'")
    else:
        logging.info("OK")

def test_generate(data, regexp_type, expected = None):
    """`data`: list of strings used to generate the regular expression.
    `regexp_type`: "strict" | "lax"
    `expected`: if provided, string containing the expected regular expression.
    """
    exp = generator.generate(data, regexp_type)
    logging.info(str(data) +  " -> " + exp)
    if (None != expected):
        check_equal(expected, exp)

test_generate([ "5", "2" ], "lax", "\d")
test_generate([ "A", "2" ], "lax", "[2A]")
test_generate([ "A", "2" ], "strict", "[2A]")
test_generate([ "Le petit chat dort.", "11/02/2004" ], "strict", 
    "[1L][1e][ /][0p][2e][t/][2i][0t][0 ][4c]h?a?t? ?d?o?r?t?\.?")
test_generate([ "Le petit chat dort.", "11/02/2004" ], "lax", 
    "[1L][1e][ /][0p][2e][t/][2i][0t][0 ][4c]h?a?t? ?d?o?r?t?\.?")
test_generate([ "AAAA", "11" ], "lax", "[1A]{2}A{0,2}")
test_generate([ "1 2 3", "abcdefg" ], "lax", "[1a][b ][2c][d ][3e]f?g?")
test_generate([ "   ", "1/2" ], "lax", "[1 ][ /][2 ]")
test_generate([ " ", "/" ], "lax", "[ /]")
test_generate([ "1", "12" ], "lax", "12?")
test_generate([ " ", "  " ], "lax", " {1,2}")
test_generate([ "1", "11" ], "lax", "1{1,2}")
test_generate([ "1", "11", "234", "999 " ], "lax", "\d{1,3} ?")

test_generate([ "j", "N", "Z", "t" ], "lax", "\w")
test_generate([ "x", "J", "B", "H" ], "lax", "\w")
test_generate([ "2", "c", "y" ], "strict", "[2cy]")

def get_random_string(desired_length):
    """Returns a random string of length `desired_length` containing digits, 
    letters, punctuation or space like characters."""
    import string #TODO: find a replacment for this module
    import random
    import sre_parse
    return "".join([random.choice(string.letters + string.digits + 
            string.punctuation + sre_parse.CATEGORY_SPACE) 
        for _ in range(0, desired_length)]) 

def get_random_string_light(desired_length):
    """Returns a random string of length `desired_length` containing digits, 
    some special or space like characters."""
    import string #TODO: find a replacment for this module
    import random
    import sre_parse
    return "".join([random.choice(string.letters + string.digits + "[]-?+*" + 
            sre_parse.CATEGORY_SPACE) 
        for _ in range(0, desired_length)]) 

r1 = [get_random_string(12), get_random_string(12), 
    get_random_string(12), get_random_string(12)]
r2 = [get_random_string(12), get_random_string(11), 
    get_random_string(10), get_random_string(9)]
r3 = [get_random_string(40), get_random_string(40), get_random_string(40), 
    get_random_string(40), get_random_string(40), get_random_string(40)]
test_generate(r1, "lax")
test_generate(r1, "strict")
test_generate(r2, "lax")
test_generate(r2, "strict")
test_generate(r3, "lax")
test_generate(r3, "strict")

test_generate(
    ['L13|KgRZ?iK', '2*mu`/pdoyF', '{5RRg3J|L*1', 'hxEl^V!@1fY'], "lax")
test_generate(
    ['L13|KgRZ?iK', '2*mu`/pdoyF', '{5RRg3J|L*1', 'hxEl^V!@1fY'], "strict")
test_generate(
    ['^L-p0]cft(&', '0IFrP%xp$M', ')`yg%!5F+', 'z0ho)L{*'], "lax")
test_generate(
    ['^L-p0]cft(&', '0IFrP%xp$M', ')`yg%!5F+', 'z0ho)L{*'], "strict")
long_list = []
for i in range(25):
    long_list.append(get_random_string_light(3))
logging.info("test_generate: long_list")
test_generate(long_list, "lax")
test_generate(long_list, "strict")


test_generate(['c6cG]NHp7', 'Epx5acgex', 'tGe8+HjSY', 'y0plbKtsO', 
    'BXYo+2Qwe', 'atKrnM?Iy', '2Xo]Yw5w5', '5LxOy*yfs', 'drt9DHm[Q', 
    'yonZGT?Sx', 'wwt-pcdlH', 'ok1Fdh97J', '[VIhgFga[', 'BKsYDQOEa', 
    'LJmcz9c2_', 'XK*Lyw-ry', 'C1dAte1L3', 'usTHKf4yy', '7lO20QOWY', 
    'aJ6Ytcccm', 'a2+8GV627', 'xlX?a[k+c', 'ZaocQm20z', 'WyRRBcVyc', 
    'Myrat]AeQ', 'xpVjq6PPV', 'HZcou_7+f', 'zCdsoaByp', 'cbV5?vUFj', 
    ']8e]aV6AB', 'rBae2rcNN', 'EZdcaeYgM', 'YppByMesA', 'L7F*mh9bw', 
    '5l4I[ceX4', '0sTgV]myM', 'dczeSGz0X', 'IeWMkszba', 'RD55AOyOb', 
    '7cuJhTSOL', '6vEtConwR', 'BhD?LncF1', 'vD]SEEcj+', 'jjypAfece', 
    'JAa7znpd0', 'VJE?pKH?O', '*RoZsQPte', '1tVcftDAV', 'VI**riyLP', 
    'vl*hee2r5'], "strict", 
"[0-25-7acdjort-zBCEH-JLMRV-Z\]\*\[][0-26-8a-cehj-lopr-tvwyA-DGI-LRVXZ][14-6ac\
-em-pr-ux-zD-FIKORTV-Y\]\*\+][257-9aceghjlopr-tABF-JLMORSYZ\-\]\*\?][02abd-hkm\
-uyzA-EGKLQSVY\]\+\?\[][269acefhim-or-tvw_E-HKM-OQTV\]\*\[][124-79c-egjkmnptyz\
ABDHO-QSUVY\-\?][027a-gjlpr-twyAEFILN-PSWX\+\?\[][013-57a-cefjmpsw-z_ABHJL-RVX\
Y\+\[]")


big = ["bigLogXXX_100821_003795.tar.gz",
    "bigLogXXX_100821_015795.tar.gz",
    "bigLogXXX_100821_021795.tar.gz",
    "bigLogXXX_100821_033795.tar.gz",
    "bigLogXXX_100821_046795.tar.gz",
    "bigLogXXX_100821_057795.tar.gz",
    "bigLogXXX_100821_068923.tar.gz",
    "bigLogXXX_100821_072345.tar.gz",
    "bigLogXXX_100821_086495.tar.gz",
    "bigLogXXX_100821_093795.tar.gz",
    "bigLogXXX_100821_107795.tar.gz",
    "bigLogXXX_100821_118923.tar.gz",
    "bigLogXXX_100821_122345.tar.gz",
    "bigLogXXX_100821_136495.tar.gz",
    "bigLogXXX_100821_143795.tar.gz",
    "bigLogXXX_100821_158923.tar.gz",
    "bigLogXXX_100821_162345.tar.gz",
    "bigLogXXX_100821_176495.tar.gz",
    "bigLogXXX_100821_183795.tar.gz",
    "bigLogXXX_100821_198923.tar.gz",
    "bigLogXXX_100821_202345.tar.gz",
    "bigLogXXX_100821_216495.tar.gz",
    "bigLogXXX_100821_223795.tar.gz",
    "bigLogXXX_100821_236495.tar.gz",

    "bigLogXXX_100821_004795.tar.gz",
    "bigLogXXX_100821_016795.tar.gz",
    "bigLogXXX_100821_022795.tar.gz",
    "bigLogXXX_100821_034795.tar.gz",
    "bigLogXXX_100821_047795.tar.gz",
    "bigLogXXX_100821_058795.tar.gz",
    "bigLogXXX_100821_069923.tar.gz",
    "bigLogXXX_100821_073345.tar.gz",
    "bigLogXXX_100821_087495.tar.gz",
    "bigLogXXX_100821_094795.tar.gz",
    "bigLogXXX_100821_108795.tar.gz",
    "bigLogXXX_100821_119923.tar.gz",
    "bigLogXXX_100821_123345.tar.gz",
    "bigLogXXX_100821_137495.tar.gz",
    "bigLogXXX_100821_144795.tar.gz",
    "bigLogXXX_100821_159923.tar.gz",
    "bigLogXXX_100821_163345.tar.gz",
    "bigLogXXX_100821_177495.tar.gz",
    "bigLogXXX_100821_184795.tar.gz",
    "bigLogXXX_100821_199923.tar.gz",
    "bigLogXXX_100821_203345.tar.gz",
    "bigLogXXX_100821_217495.tar.gz",
    "bigLogXXX_100821_224795.tar.gz",
    "bigLogXXX_100821_237495.tar.gz",

    "bigLogXXX_100820_003795.tar.gz",
    "bigLogXXX_100820_015795.tar.gz",
    "bigLogXXX_100820_021795.tar.gz",
    "bigLogXXX_100820_033795.tar.gz",
    "bigLogXXX_100820_046795.tar.gz",
    "bigLogXXX_100820_057795.tar.gz",
    "bigLogXXX_100820_068923.tar.gz",
    "bigLogXXX_100820_072345.tar.gz",
    "bigLogXXX_100820_086495.tar.gz",
    "bigLogXXX_100820_093795.tar.gz",
    "bigLogXXX_100820_107795.tar.gz",
    "bigLogXXX_100820_118923.tar.gz",
    "bigLogXXX_100820_122345.tar.gz",
    "bigLogXXX_100820_136495.tar.gz",
    "bigLogXXX_100820_143795.tar.gz",
    "bigLogXXX_100820_158923.tar.gz",
    "bigLogXXX_100820_162345.tar.gz",
    "bigLogXXX_100820_176495.tar.gz",
    "bigLogXXX_100820_183795.tar.gz",
    "bigLogXXX_100820_198923.tar.gz",
    "bigLogXXX_100820_202345.tar.gz",
    "bigLogXXX_100820_216495.tar.gz",
    "bigLogXXX_100820_223795.tar.gz",
    "bigLogXXX_100820_236495.tar.gz",

    "bigLogXXX_100820_004795.tar.gz",
    "bigLogXXX_100820_016795.tar.gz",
    "bigLogXXX_100820_022795.tar.gz",
    "bigLogXXX_100820_034795.tar.gz",
    "bigLogXXX_100820_047795.tar.gz",
    "bigLogXXX_100820_058795.tar.gz",
    "bigLogXXX_100820_069923.tar.gz",
    "bigLogXXX_100820_073345.tar.gz",
    "bigLogXXX_100820_087495.tar.gz",
    "bigLogXXX_100820_094795.tar.gz",
    "bigLogXXX_100820_108795.tar.gz",
    "bigLogXXX_100820_119923.tar.gz",
    "bigLogXXX_100820_123345.tar.gz",
    "bigLogXXX_100820_137495.tar.gz",
    "bigLogXXX_100820_144795.tar.gz",
    "bigLogXXX_100820_159923.tar.gz",
    "bigLogXXX_100820_163345.tar.gz",
    "bigLogXXX_100820_177495.tar.gz",
    "bigLogXXX_100820_184795.tar.gz",
    "bigLogXXX_100820_199923.tar.gz",
    "bigLogXXX_100820_203345.tar.gz",
    "bigLogXXX_100820_217495.tar.gz",
    "bigLogXXX_100820_224795.tar.gz",
    "bigLogXXX_100820_237495.tar.gz"]


test_generate(["1", "2"], "strict", "[12]")
test_generate(["1", "a"], "strict", "[1a]")
test_generate(["112", "abc"], "strict", "[1a][1b][2c]")
test_generate(["1", "3", "2", "5", "4"], "strict", "[1-5]")
test_generate(["5289", "ecum", "dy"], "strict", "[5de][2cy][8u]?[9m]?")
test_generate(big, "lax", "bigLogX{3}_10{2}82\d_\d{6}\.tar\.gz")
test_generate(big, "strict", 
    "bigLogX{3}_10{2}82[01]_[0-2][0-9][1-9][3479][249][35]\.tar\.gz")

small = ["123", "124", "125", "128", "134"]
test_generate(small, "lax", "1\d{2}")
test_generate(["3", "4"], "lax", "\d")
test_generate(["5", "4"], "lax", "\d")
test_generate(["5", "2"], "lax", "\d")
