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
#import generator
#import collections
import sys
import time

import logger

import analyse
import characters
import comparator
import regexp
import re


def s(a, b):
    if (a == b):
        if (a.get_category() == characters.OTHERS):
            return 20
        elif (a.empty):
            return 14
        elif (a.get_category() == characters.SPECIALS):
            return 14
        else:
            return 13
    elif (a.get_category() == b.get_category()):
        return 12
    elif (a.get_meta_category() == b.get_meta_category()):
        return 11
    elif ((a.empty) or (b.empty)):
        return 10
    else:
        if ((a.get_category() == characters.OTHERS) or
            (b.get_category() == characters.OTHERS)):
            return -10
        else:
            return -1


def s2(a, b):
    if (a == b):
        if (a.get_category() == characters.OTHERS):
            return 20
        elif (a.empty):
            return 14
        elif (a.get_category() == characters.SPECIALS):
            return 20
        else:
            return 13
    elif (a.get_category() == b.get_category()):
        return 12
    elif (a.get_meta_category() == b.get_meta_category()):
        return 11
    elif ((a.empty) or (b.empty)):
        return 10
    else:
        if ((a.get_category() == characters.OTHERS) or
            (b.get_category() == characters.OTHERS) or
            (a.get_category() == characters.SPECIALS) or
            (b.get_category() == characters.SPECIALS)):
            return -10
        else:
            return -1

def meta_test(test, similarity=s, gap_cost=-1):
    test_meta = []
    for t in test:
        line = map(analyse.MetaChar, t)
        test_meta.append(line) 
    compared = comparator.multi_nw_algorithm(
        test_meta,
        gap=analyse.MetaChar(None), null=[], 
        concatenate=comparator.prepend,
        similarity=similarity, gap_cost=gap_cost)
    print "\n".join(map(str, compared))
    for c in compared:
        string = ""
        for meta_char in c:
            if (meta_char.empty):
                string += '_'
            else:
                string += meta_char.get_char()
#        print string
    youpi = regexp.generate(compared)
#    print youpi
#    print youpi.get()
#    print youpi.get('lax')
#    print youpi.get('lax', 'lax')
    return youpi


def assert_match(re_string, samples):
    print "assert :" + re_string
    compiled_matcher = re.compile(re_string)
    failures = 0
    for lr in samples:
        if (compiled_matcher.match(lr) is None):
            print "this one does not match but was used as sample:\n  %s" % lr
            failures += 1
    if (failures > 0):
        import sys
        sys.exit(0)

def big_check(big, similarity=s, gap_cost=-1):
    print ""
    print big
    start = time.time()
    generated_regexp = meta_test(big, similarity, gap_cost)
    stop = time.time()
    print('time: %fs' % (stop - start))

    aggregated = generated_regexp.aggregate()
    print "MetaCharacter: "
    meta_character_re = regexp.generate_from_aggregators(
        aggregated, 'MetaCharacter')
    assert_match(meta_character_re, big)
    print "Category: "
    category_re = regexp.generate_from_aggregators(aggregated, 'Category')
    assert_match(category_re, big)
    print "MetaCategory: "
    meta_category_re = regexp.generate_from_aggregators(
        aggregated, 'MetaCategory')
    assert_match(meta_category_re, big)
    return generated_regexp


# deactivate running tests
if (True):

    def test_generate(sample):
        print '<<<<'
        for s in sample:
            print s
        regexpr = regexp.generate_with_char(sample)
        print '----'
        re_string = regexpr.get()
        print re_string
        compiled = re.compile(re_string)
        ko = False
        for s in sample:
            if (compiled.match(s) is None):
                print "KO: '%s' does not match '%s'" % (re_string, s)
                ko = True 
        if (not ko):
            print "OK"
        else:
            print regexpr
        print '>>>>'

    #test_generate(['a1`', 'b2', 'c3', 'd'])

    #test_generate(["L", "I", "L"])

    #test_generate(["L", "I", " "])

    sample = ([
        "La pluie tombe sur les arbres.",
        "Il fait froid.",
        "Le petit chat dort.",
        ])
    test_generate(sample)
    big_check(sample)
    big_check(sample, gap_cost=-6)

    t = meta_test(["Ce test est simple.", "Vraiment tres simple.", "Pif paf pouf."])
    print t.get()
    print t.get('lax')
    print t.get('lax', 'lax')

    lorem_ipsum = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Nunc adipiscing elit eget sapien lacinia eu fringilla dolor pretium.",
    #"Duis tempor velit sit amet quam condimentum eget tempus augue pretium.",
    #"Vivamus cursus elit vitae enim euismod quis consequat felis pretium.",
    #"Aliquam sit amet lorem ut neque condimentum sodales ut vel lorem.",
    "Proin sed lorem id lacus luctus tincidunt.",
    "Suspendisse a nisl id tellus fermentum tristique vitae sed sapien.",
    "Duis ultrices est vitae dolor hendrerit eu iaculis felis laoreet.",
    #"Curabitur quis lectus nec mauris pharetra elementum.",
    #"Duis nec lectus nulla, non gravida erat.",
    #"Proin molestie posuere turpis, ac mollis nisl malesuada eu.",
    #"Nulla dictum malesuada massa, eget tincidunt eros volutpat eget.",
    #"Integer sed magna tellus, pulvinar aliquam eros.",
    #"Maecenas convallis ornare ipsum, sed consequat enim porttitor bibendum.",
    #"Mauris nec augue ac leo consectetur tempus nec mattis tellus.",
    "In dictum urna ac eros convallis volutpat.",
    #"Duis at nunc eget enim vehicula pulvinar.",
    "Morbi quis ante id dui pellentesque fermentum.",
    #"Nulla sit amet massa lacinia tortor egestas molestie.",
    #"Nunc scelerisque vulputate risus, at venenatis eros consectetur vel.",
    "Sed at magna vestibulum est auctor sagittis.",
    #"Donec vehicula sollicitudin arcu, at tempus nisl hendrerit sit amet.",
    #"Sed mollis massa vitae felis ullamcorper convallis.",
    #"Praesent in justo in urna adipiscing varius.",
    #"Vivamus gravida eros non mi laoreet ac imperdiet arcu iaculis.",
    #"Ut aliquam tincidunt arcu, eu venenatis leo tempus ac.",
    #"Curabitur quis augue mauris, non dignissim nibh.",
    #"Donec fringilla justo eget massa dignissim semper.",
    #"Fusce iaculis leo vitae velit vulputate adipiscing.",
    #"Proin et libero in quam molestie porttitor non at odio.",
    ]

    generated_regexp = big_check(lorem_ipsum)

#    start = time.time()
#    generated_regexp = meta_test(lorem_ipsum)
#    stop = time.time()
#    print('time: %fs' % (stop - start))
#
#    aggregated = generated_regexp.aggregate()
#    meta_character_re = generate_from_aggregators(aggregated, 'MetaCharacter')
#    print "MetaCharacter: "
#    assert_match(meta_character_re, lorem_ipsum)
#    category_re = generate_from_aggregators(aggregated, 'Category')
#    print "Category: "
#    assert_match(category_re, lorem_ipsum)
#    meta_category_re = generate_from_aggregators(aggregated, 'MetaCategory')
#    print "MetaCategory: "
#    assert_match(meta_category_re, lorem_ipsum)

    lorem_ipsum_2 = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Donec eu odio tortor, eget fringilla odio.",
    "Curabitur egestas libero at metus laoreet ac tincidunt justo placerat.",
    "Nunc dapibus urna sit amet nisi gravida vel tempus leo tristique.",
    "Phasellus non tortor ligula, eu dignissim urna.",
    "Vestibulum vitae lacus a ligula aliquam malesuada.",
    "Vestibulum rhoncus euismod ipsum, eu condimentum tortor mattis vitae.",
    "Proin non risus quis tellus iaculis aliquet.",
    "Nullam pulvinar libero non erat tempus tincidunt.",
    "Nullam dapibus lacus a dolor hendrerit ut fermentum quam pharetra.",
    "Proin a turpis nec leo convallis interdum id quis augue.",
    "Nam hendrerit nisi mauris, in sodales lectus.",
    "Aliquam viverra elit nec nisi pulvinar vehicula.",
    "Sed ut diam a velit dignissim aliquam sit amet luctus neque.",
    "Etiam posuere lacinia ante, eu dictum ligula lobortis ut.",
    "Suspendisse et lorem consequat urna faucibus convallis.",
    "Quisque blandit odio id nibh ultrices ut aliquam elit dapibus.",
    "Mauris elementum dui eu leo commodo a auctor diam accumsan.",
    "Sed vestibulum sem ut mauris luctus id tempus mauris molestie.",
    "Etiam at purus ut orci aliquet condimentum a eu orci.",
    "Mauris ut ligula vitae leo suscipit convallis eget eu metus.",
    "Proin vitae dui non lectus malesuada gravida.",
    "Nullam dapibus leo eget lectus ullamcorper consequat.",
    "Etiam iaculis arcu egestas orci rutrum id laoreet purus porta.",
    "Nunc pellentesque enim non sem vehicula sed ultricies purus dignissim.",
    "Proin a tortor mattis nibh viverra vulputate.",
    "Nam sed tortor sed nibh dignissim posuere in a leo.",
    "Fusce ultrices dui vel velit ornare quis auctor leo posuere.",
    "Quisque a ante felis, at posuere nunc.",
    "Aliquam tristique orci at justo tincidunt volutpat.",
    "Nunc posuere consequat nibh, a iaculis metus gravida at.",
    "Vestibulum in nulla lorem, in pretium libero.",
    "Vivamus non enim risus, vitae venenatis justo.",
    "Vestibulum dictum rutrum dolor, vitae accumsan erat lacinia id.",
    "Ut sed erat commodo sapien auctor auctor id at magna.",
    "Nam sit amet leo ac sapien mattis ultrices.",
    "Etiam vestibulum sapien at lorem ullamcorper laoreet.",
    "Aenean vitae tortor blandit erat cursus adipiscing nec vel turpis.",
    "Mauris pharetra nisl egestas quam ultricies varius.",
    "Etiam nec nisl arcu, eu gravida metus.",
    "Sed luctus magna sit amet nunc cursus sodales quis ut massa.",
    "Quisque in lectus nulla, sed feugiat ipsum.",
    "Fusce vel tellus sed nibh interdum ultricies at eget leo.",
    "Praesent bibendum lobortis augue, vitae varius risus dignissim interdum.",
    "Sed ullamcorper risus et enim iaculis viverra.",
    "Morbi porta mi quis eros mattis at aliquet velit dignissim.",
    "Etiam hendrerit justo nec tellus mattis accumsan.",
    "Donec commodo malesuada ante, quis fermentum orci adipiscing id.",
    "Ut commodo libero ut mauris bibendum eget bibendum dui dictum.",
    "Sed consequat nibh vitae erat mollis porttitor sollicitudin felis rhoncus.",
    "Morbi vel massa ac diam suscipit porttitor commodo facilisis orci.",
    "Vestibulum porta iaculis arcu, in adipiscing lorem mollis in.",
    "Duis et mi a urna mattis suscipit.",
    "Vivamus rutrum neque quis nibh egestas gravida.",
    "Curabitur suscipit tristique orci, sagittis mattis mauris suscipit et.",
    "Proin rhoncus mauris at diam sodales commodo.",
    "Integer id turpis eu sem imperdiet ultricies.",
    "Praesent non mauris odio, et consequat purus.",
    "Pellentesque blandit tempor orci, ac pulvinar leo sollicitudin in.",
    "Vivamus in ante nulla, ut congue nulla.",
    "Pellentesque varius metus a orci ultricies pretium.",
    "Nunc at est nec mi aliquam suscipit.",
    "Nunc vel tellus nec quam suscipit faucibus id et nisl.",
    "Ut eu ipsum mauris, sed egestas lorem.",
    "Donec nec quam id sem tempus posuere id sed sapien.",
    "Quisque rutrum ipsum at massa eleifend eget aliquet odio placerat.",
    "In fringilla congue elit, eget pharetra nibh eleifend luctus.",
    "Quisque vel massa erat, eu vehicula nisl.",
    "Proin ut velit odio, non commodo ligula.",
    "Nulla et diam sed risus feugiat dictum.",
    "Suspendisse tincidunt magna dapibus tellus auctor convallis.",
    "Aenean lobortis eros vel sem sollicitudin vulputate sit amet ut metus.",
    "Integer sit amet lorem eu ligula facilisis tincidunt sit amet ut velit.",
    "Phasellus ac enim dolor, vitae ultricies diam.",
    "Donec consectetur nisl tempus urna varius tristique.",
    "Sed ac elit eget mi interdum ultricies nec et enim.",
    "Donec vitae augue odio, consectetur tristique justo.",
    "Aenean pharetra turpis eget tellus tempus sodales.",
    "Nunc posuere sollicitudin lectus, et tincidunt est pretium non.",
    "Sed malesuada aliquam leo, sed fringilla massa pulvinar nec.",
    "Le petit chat dort.",
    "Il fait beau et chaud",
    "La pluie tombe sur les arbres.",]

    re_string = generated_regexp.get('lax', 'lax')

    def check(re_string, strings):
        print '============================================='
        print re_string
        compiled_matcher = re.compile(re_string)
        failures = 0
        for lr2 in strings:
    #        print "try: %s" % lr2
            if (compiled_matcher.match(lr2) is None):
    #            print "this one does not match:\n  %s" % lr2
                failures += 1
        print("%s failures out of %s -> %s" 
            % (failures, len(strings), failures / float(len(strings))))
        print "based on %s samples" % len(lorem_ipsum)


    #check(meta_character_re, lorem_ipsum_2)
    #check(category_re, lorem_ipsum_2)
    #check(meta_category_re, lorem_ipsum_2)
    check(re_string, lorem_ipsum_2)

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

    big_check(big)

    big_check(["abc", "abc123az"])

# this one does not work !!! infinite loop

    big = ([
        " Column 1    | Column 2   | Last Column",
        " something   | else       | is written ",
        " it is not   | mandatory  | to fill    ",
        " the last    | column     |",
        " you can     | put a lot  | of chars   ",
        ])
    big_check(big)
#
#start = time.time()
#generated_regexp = meta_test(big)
#stop = time.time()
#print('time: %fs' % (stop - start))
#
#aggregated = generated_regexp.aggregate()
#meta_character_re = generate_from_aggregators(aggregated, 'MetaCharacter')
#print "MetaCharacter: "
#assert_match(meta_character_re, big)
#category_re = generate_from_aggregators(aggregated, 'Category')
#print "Category: "
#assert_match(category_re, big)
#meta_category_re = generate_from_aggregators(aggregated, 'MetaCategory')
#print "MetaCategory: "
#assert_match(meta_category_re, big)


big_check([
    "ABC,",
    "DE,",
    ])

big_check([
    "ABC",
    "DE,",
    ])

big_check([
    "ABC,",
    "DE,",
    "F,",
    "ghi,",
    "jk,",
    "l,",
    ])


big_check([
    "ABC,XV12AB1C",
    "AB,HJ1",
    ])