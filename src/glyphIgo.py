#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto@albertopettarin.it)'
__copyright__   = '2012-2014 Alberto Pettarin (alberto@albertopettarin.it)'
__version__     = 'v2.0.1'
__date__        = '2014-03-08'
__description__ = 'glyphIgo is a Swiss Army knife for dealing with fonts and EPUB eBooks'


### BEGIN changelog ###
#
# 2.0.1 2014-03-08 Minor code cleanup
# 2.0.0 2014-03-07 Moved to GitHub, released under MIT license
# 1.21  2014-02-16 Added discover function (-d and -D)
# 1.20  2013-08-04 Added fuzzy Unicode name match
# 1.19  2013-04-02 Bug fix: when parsing X(HT)ML pages (inside EPUB), force UTF-8 decoding
# 1.18  2013-03-24 Added character count function
# 1.17  2013-03-23 Added character lookup function
# 1.16  2013-03-16 Fixed a bug with genEPUB
# 1.15  2013-03-15 Added output to EPUB
# 1.14  2013-02-23 Added (default) stripping of X(HT)ML tags when using -e option
# 1.13  2013-02-22 Better verbose output
# 1.12  2013-02-22 Fixed a bug when using verbose output
# 1.11  2013-02-21 Code clean up
# 1.10  2013-02-15 Code clean up
# 1.09  2013-02-14 Better parameter handling
# 1.08  2013-02-11 Added counter of missing glyphs
# 1.07  2013-02-10 Removed debug mode, added quiet mode
# 1.06  2012-10-29 Added option to specify minimized font name
# 1.05  2012-10-26 Added code for reading list of glyphs
# 1.04  2012-10-04 Better output, added exit codes
# 1.03  2012-10-03 Better code for minimizing font
# 1.02  2012-07-31 Added automatic unpacking of EPUB files
# 1.01  2012-07-30 Initial release
#
### END changelog ###

import codecs, collections, getopt, fontforge, os, re, sys, unicodedata, zipfile
from htmlentitydefs import name2codepoint

### BEGIN read_command_line_parameters ###
# read_command_line_parameters(argv)
# read the command line parameters given in argv, and return a suitable dict()
def read_command_line_parameters(argv):

    try:
        optlist, free = getopt.getopt(argv[1:], 'chmqsvud:D:e:f:g:l:L:o:p:', ['discover=', 'Discover=', 'ebook=', 'font=', 'glyphs=', 'lookup=', 'Lookup=', 'output=', 'plain=', 'count', 'help', 'minimize', 'preserve', 'quiet', 'sort', 'verbose', 'epub'])
    #Python2#
    except getopt.GetoptError, err:
    #Python3#    except getopt.GetoptError as err:
        print_error(str(err))

    return dict(optlist)
### END read_command_line_parameters ###


### BEGIN usage ###
# usage()
# print script usage
def usage():
    #Python2#
    e = "python"
    #Python2#
    s = "glyphIgo.py"
    #Python3#    e = "python3"
    #Python3#    s = "glyphIgo3.py"
    print_("")
    print_("$ %s %s [ARGUMENTS]" % (e, s))
    print_("")
    print_("Arguments:")
    print_(" -h, --help            : print this usage message and exit")
    print_(" -f, --font <font>     : font file, in TTF/OTF/WOFF format")
    print_(" -g, --glyphs <list>   : use this list of glyphs instead of opening a font file")
    print_(" -e, --ebook <ebook>   : ebook in EPUB format")
    print_(" -p, --plain <ebook>   : ebook file, in plain text UTF-8 format")
    print_(" -m, --minimize        : retain only the glyphs of <font> that appear in <ebook>")
    print_(" -o, --output <name>   : use <name> for the font to be created")
    print_(" --preserve            : preserve X(HT)ML tags instead of stripping them away")
    print_(" -s, --sort            : sort output by character count instead of character codepoint")
    print_(" -q, --quiet           : quiet output")
    print_(" -v, --verbose         : verbose output of Unicode codepoints")
    print_(" -u, --epub            : output an EPUB file containing the Unicode characters in the input file(s)")
    print_(" -l, --lookup <char>   : lookup Unicode information for character <char>, given as Unicode char or dec/hex code or exact name")
    print_(" -d, --discover <char> : same as -l, but only print the Unicode char and name")
    print_(" -L, --Lookup <name>   : lookup Unicode information for character <name>, with fuzzy name lookup (WARNING: very slow!)")
    print_(" -D, --Discover <name> : same as -L, but only print the Unicode char and name")
    print_(" -c, --count           : count the number of characters in the text of <ebook> (specified with -e or -p)")
    print_("")
    print_("Exit codes:")
    print_("")
    print_(" 0 = no error / no missing glyphs in the font file")
    print_(" 1 = invalid argument(s) error")
    print_(" 2 = missing glyphs in the font file to correctly display the given file/ebook")
    print_(" 4 = minimization/conversion failed")
    print_(" 8 = lookup failed")
    print_("")
    print_("Examples:")
    print_("")
    print_("  1. Print this usage message")
    print_("     $ %s %s -h" % (e, s))
    print_("")
    print_("  2. Print the list of glyphs in font.ttf")
    print_("     $ %s %s -f font.ttf" % (e, s))
    print_("")
    print_("  3. Print the list of characters in ebook.epub")
    print_("     $ %s %s -e ebook.epub" % (e, s))
    print_("")
    print_("  4. Print the list of characters in page.xhtml")
    print_("     $ %s %s -p page.xhtml" % (e, s))
    print_("")
    print_("  5. Check whether all the characters in ebook.epub can be displayed by font.ttf")
    print_("     $ %s %s -f font.ttf -e ebook.epub" % (e, s))
    print_("")
    print_("  6. As above, but use font_glyph_list.txt containing a list of decimal codepoints for the font glyphs")
    print_("     $ %s %s -g font_glyph_list.txt -e ebook.epub" % (e, s))
    print_("")
    print_("  7. As in Example 5, but sort missing characters (if any) by their count (in ebook.epub) instead of by Unicode codepoint")
    print_("     $ %s %s -f font.ttf -e ebook.epub -s" % (e, s))
    print_("")    
    print_("  8. Create new.font.otf containing only the glyphs of font.ttf that also appear in ebook.epub")
    print_("     $ %s %s -m -f font.ttf -e ebook.epub -o new.font.otf" % (e, s))
    print_("")
    print_("  9. Convert font.ttf (TTF) into font.otf (OTF)")
    print_("     $ %s %s -f font.ttf -o font.otf" % (e, s))
    print_("")
    print_(" 10. As in Example 3, but also create ebook.epub.epub containing the list of Unicode characters")
    print_("     $ %s %s -e ebook.epub -u" % (e, s))
    print_("")
    print_(" 11. As in Example 5, but also create missing.epub containing the list of missing Unicode characters")
    print_("     $ %s %s -f font.ttf -e ebook.epub -u" % (e, s))
    print_("")
    print_(" 12. Lookup for information for Unicode character")
    print_("     $ %s %s -l d8253" % (e, s))
    print_("     $ %s %s -l x203d" % (e, s))
    print_("     $ %s %s -l ‽" % (e, s))
    print_("     $ %s %s -l \"INTERROBANG\"" % (e, s))
    print_("")
    print_(" 13. Count the number of characters in ebook.epub")
    print_("     $ %s %s -c -e ebook.epub" % (e, s))
    print_("")
    print_(" 14. Fuzzy lookup for information for Unicode characters which are Greek omega letters with oxia")
    print_("     $ %s %s -L \"GREEK OMEGA OXIA\"" % (e, s))
    print_("")
### END usage ###


### BEGIN check_existence ###
# check_existence(filename)
# checks whether filename exists
def check_existence(filename):
    if filename == None:
        return False
    return os.path.isfile(filename)
### END check_existence ###


### BEGIN print_error ###
# print_error(error, displayusage=True)
# print the given error, call usage, and exit
# optional displayusage to skip usage
def print_error(error, displayusage = True, exitcode = 1):
    sys.stderr.write("[ERROR] " + error + " Aborting.\n")
    if displayusage :
        usage()
    sys.exit(exitcode)
### END print_error ###


### BEGIN print_info ###
# print_info(info, quiet)
# print the given info string
def print_info(info, quiet):
    if (not quiet):
        print("[INFO] " + info)
### END print_info ###


### BEGIN print_ ###
# print_(info)
# print the given string
def print_(info):
    print(info)
### END print_ ###


### BEGIN get_font_char_list ###
# get_font_char_list(fontFile)
# return the list of glyhs in the given font file
def get_font_char_list(fontFile):
    font = fontforge.open(fontFile)
    chars = []
    for x in font.glyphs():
        if (x.unicode > -1):
            try:
                c = unichr(x.unicode)
                chars += [ c ]
            except:
                # error
                c = -1
    return chars
### END get_font_char_list ###

### BEGIN get_glyphs_char_list ###
# get_glyphs_char_list(fontFile)
# return the list of glyhs in the given font file
def get_glyphs_char_list(glyphsFile):
    #Python2#
    f = codecs.open(glyphsFile, 'r', 'utf-8', 'ignore')
    #Python3#    f = open(glyphsFile, 'r', 'utf-8', 'ignore')
    glyphsText = f.read()
    f.close()

    chars = []
    for g in glyphsText.splitlines():
        if ((len(g) > 0) and (g[0] != "#")):
            try:
                if ((len(g) > 2) and (g[0:2] == "0x")):
                    c = unichr(int(g[2:], 16))
                elif ((len(g) > 1) and (g[0] == "x")):
                    c = unichr(int(g[1:], 16))
                else:
                    c = unichr(int(g))
                chars += [ c ]
            except:
                # error
                c = -1
    return chars
### END get_glyphs_char_list ###

### BEGIN minimize_font ###
# minimize_font(fontFile, charList, newFontFile)
# create newFontFile containing only the glyphs in charList
# returns the list of actually present chars
def minimize_font(fontFile, charList, newFontFile):
    found = []
    font_chars = get_font_char_list(fontFile)
    font = fontforge.open(fontFile)
    font.selection.none()
    for c in charList:
        if c[0] in font_chars:
            font.selection.select(("more", "unicode"), ord(c[0]))
            found.append(c[0])
    font.selection.invert()
    font.clear()
    font.generate(newFontFile)
    return found
### END get_font_char_list ###

### BEGIN convert_font ###
# convert_font(fontFile, newFontFile)
# create newFontFile containing all the glyphs in charList
def convert_font(fontFile, newFontFile):
    font = fontforge.open(fontFile)
    font.selection.all()
    font.generate(newFontFile)
### END convert_font ###

### BEGIN remove_tags ###
# remove_tags(s)
# remove X(HT)ML tags from the given string
def remove_tags(s):
    #TODO improve this
    s = s.replace("\n", " ")
    s = s.replace("\r", " ")
    s = re.sub(r"[ ]+", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s
### END remove_tags ###

### BEGIN decode_xml_entities ###
# decode_xml_entities(s)
# substitute all the xml entities in s with the corresponding unicode characters
def decode_xml_entities(s):
    ### END fix ###
    def fix(m):
        c = m.group(1)
        # escape the escape sequences
        if (c == "amp"):
            return "&"
        if (c == "lt"):
            return "<"
        if (c == "gt"):
            return ">"
        if (c in name2codepoint):
            # named entity
            return unichr(name2codepoint[c])
        else:
            if ((c[0] == "#") and len(c) > 1):
                # numeric
                if ((c[1] == "x") and (len(c) > 2)):
                    try:
                        i = int(c[2:], 16)
                        return unichr(i)
                    except:
                        # error
                        return ''
                else:
                    try:
                        i = int(c[1:])
                        return unichr(i)
                    except:
                        # error
                        return ''
            # error!
            return ''
    ### END fix ###

    return re.sub(r"&([#a-z0-9]+);", fix, s)
### END decode_xml_entities ###

### BEGIN filter_string ###
# filter_string(s)
# return a list of (unique) Unicode characters in s, sorted by codepoint, with their count
def filter_string(s):
    mydict = collections.defaultdict(int)
    for mychar in s:
        mydict[mychar] += 1
    mylist = []
    for mychar in sorted(mydict.keys()):
        mylist += [ [ mychar, mydict[mychar] ] ];
    return mylist
### END filter_string ###

### BEGIN get_ebook_char_list ###
# get_ebook_char_list(ebookFile)
# open the given EPUB file, and cat all text together
# TODO: full EPUB parsing 
def get_ebook_char_list(ebookFile, preserveTags):
    ebookText = ""
    zfile = zipfile.ZipFile(ebookFile)
    for name in zfile.namelist():
        if ((name.lower().endswith(".xhtml")) or
            (name.lower().endswith(".html")) or
            ((name.lower().endswith(".xml")) and (not name.lower().startswith("meta-inf")))):
            file_bytes = zfile.read(name)
            try:
                ebookText += file_bytes.decode('utf-8')
            except:
                # do nothing for now
                # TODO: throw exception and catch it at the caller
                continue
    zfile.close()

    if (not preserveTags):
        ebookText = remove_tags(ebookText)

    ebookText = decode_xml_entities(ebookText)
    ebookText = filter_string(ebookText)

    return ebookText
### END get_ebook_char_list ###

### BEGIN get_plain_char_list ###
# get_plain_char_list(plainFile)
# open the given plain file, and return a list of unique unicode characters
def get_plain_char_list(plainFile, preserveTags):
    #Python2#
    f = codecs.open(plainFile, 'r', 'utf-8', 'ignore')
    #Python3#    f = open(plainFile, 'r', 'utf-8', 'ignore')
    plainText = f.read()
    f.close()

    if (not preserveTags):
        plainText = remove_tags(plainText)

    plainText = decode_xml_entities(plainText)
    plainText = filter_string(plainText)

    return plainText
### END get_plain_char_list ###

### BEGIN escape ###
# escape(s)
# escape ASCII sequences
def escape(s):
    repl = [
            ["\0", "\\0"],
            ["\a", "\\a"],
            ["\b", "\\b"],
            ["\t", "\\t"],
            ["\n", "\\n"],
            ["\v", "\\v"],
            ["\f", "\\f"],
            ["\r", "\\r"]
            ]
    for r in repl:
        s = s.replace(r[0], r[1])
    return s
### END escape ###

### BEGIN print_char_list ###
# print_char_list(charList, verbose, sortByCodepoint)
# print a list of decimal codepoints of the given list of Unicode characters
# if verbose = True, print also names and hex codepoints
# if sortByCodepoint = True, sort the list by codepoint, otherwise by counter
def print_char_list(charList, verbose, sortByCodepoint):
    # sort by (descending) number of occurrences, instead of codepoint
    if (not sortByCodepoint):
        charList.sort(key=lambda x: -x[1])

    if verbose:
        for c in charList:
            name = unicodedata.name(c[0], 'UNKNOWN NAME')
            decCodePoint = ord(c[0])
            hexCodePoint = hex(decCodePoint)
            count = c[1]
            print_("'%s'\t%s\t%s\t%s\t%s" % (escape(c[0]), decCodePoint, hexCodePoint, name, count))
    else:
        for c in charList:
            decCodePoint = ord(c[0])
            print_("%s" % decCodePoint)
### END print_char_list ###

### BEGIN print_glyph_list ###
# print_glyph_list(glyphList, verbose)
# print a list of decimal codepoints of the given list of glyphs
# if verbose = True, print also names and hex codepoints
def print_glyph_list(glyphList, verbose):

    if verbose:
        for c in glyphList:
            name = unicodedata.name(c[0], 'UNKNOWN NAME')
            decCodePoint = ord(c[0])
            hexCodePoint = hex(decCodePoint)
            print_("'%s'\t%s\t%s\t%s" % (escape(c[0]), decCodePoint, hexCodePoint, name))
    else:
        for c in glyphList:
            decCodePoint = ord(c[0])
            print_("%s" % decCodePoint)
### END print_glyph_list ###


### BEGIN output_epub ###
# output_epub(dec_codepoint_list, title, epub_filename)
# generate an EPUB file epub_filename
# containing the dec_codepoint_list Unicode characters
# with given title
def output_epub(dec_codepoint_list, title, epub_filename):
    from genEPUB import genEPUB
    d = genEPUB()
    d.createEPUB(dec_codepoint_list, title, epub_filename)
### END output_epub ###


### BEGIN get_dec_list ###
# get_dec_list(gen_list, has_frequencies)
# returns a list of decimal codepoints
# if has_frequencies = True, the list is a list of tuples [ ['c', 11], ['d', 12], ... ]
# if has_frequencies = False, the list is a list of chars [ 'a', 'b', ... ]
def get_dec_list(gen_list, has_frequencies):
    dec_list = []
    if (has_frequencies):
        for e in gen_list:
            dec_list.append(ord(e[0]))
    else:
        for e in gen_list:
            dec_list.append(ord(e))
    return dec_list
### END get_dec_list ###

### BEGIN get_number_characters ###
# get_number_characters(characters)
# returns the total number of characters
# by summing the frequencies of the different characters
def get_number_characters(characters):
    total = 0
    for c in characters:
        total += c[1]
    return total
### END get_number_characters ###

### BEGIN compare ###
# compare(fontList, fileList)
# return a list of Unicode characters (with their counter) that appear in file but not in font
#
# TODO support combine operator to avoid the following problem:
#      font might contain "LATIN SMALL LETTER A" and "MACRON" but not "LATIN SMALL LETTER A WITH MACRON"
#      file might contain "LATIN SMALL LETTER A WITH MACRON"
#      generating a missing glyph warning
#
def compare(fontList, fileList):
    missing = []
    for f in fileList:
        # ignore ASCII characters with codepoint < 32
        if (ord(f[0]) > 31) and (f[0] not in fontList):
            missing += [ f ]
    return missing
### END compare ###


### BEGIN perform_lookup ###
#
# Perform a lookup for the given query
# which might be:
# 1) Unicode character
# 2) Unicode codepoint dec/hex (0x...)
# 3) Unicode description
# If fuzzyLookup == True, results contains the list of Unicode characters
# whose name contains ALL the given query words
# (e.g., "TAMIL", "GREEK CAPITAL", "GREEK OMEGA OXIA", etc.)
# Print the results to stdout
# Returns 0 (successful lookup) or 8 (failed lookup)
# 
def perform_lookup(query, fuzzyLookup, discoverLookup, quiet):
    if ((query == None) or len(query) == 0):
        return 8
    
    results = []
    if (fuzzyLookup):
        # try fuzzy match
        qw = query.upper().split(" ")
        effective_qw = []
        for q in qw:
            if (len(q) > 0):
                effective_qw.append(q)
        # Unicode codepoints range from 0 to 0x10FFFF = 1114111
        for i in range(1114112):
            c = unichr(i)
            name = unicodedata.name(c, "UNKNOWN").split(" ")
            is_match = True
            for e in effective_qw:
                if (not (e in name)):
                    is_match = False
                    break
            if (is_match):
                results.append(c)
        if (len(results) == 0):
            # no match
            return 8
    else:
        # try char, codepoint or exact name lookup
        if (len(query) == 1):
            # Unicode char
            results = [ u"" + query ]
        elif ((query[0] == "d") or (query[0] == "x")):
            # decimal
            try:
                if (query[0] == "d"):
                    # decimal
                    codepoint = int(query[1:])
                else:
                    # hex
                    codepoint = int(query[1:], 16)
                results = [ unichr(codepoint) ]
            except:
                # no match
                return 8
        else: 
            # try exact name lookup
            try:
                results = [ unicodedata.lookup(query) ]
            except:
                # no match
                return 8

    if (discoverLookup):
        for c in results:
            print_Unicode_info(c, discoverLookup)
    else:
        print_info("Lookup results for query '%s'" % (query), quiet)
        for c in results:
            print_info("Matched Unicode character '%s'" % (c), quiet)
            print_Unicode_info(c, discoverLookup)
            print_info("=== === === === === ===", quiet)
    
    return 0
### END perform_lookup ###


### BEGIN print_Unicode_info ###
def print_Unicode_info(char, short):
    name = unicodedata.name(char, "UNKNOWN")
    decCodepoint = ord(char)
    hexCodepoint = hex(decCodepoint)
    lower = char.lower()
    upper = char.upper()
    category = unicodedata.category(char)
    bidirectional = unicodedata.bidirectional(char)
    mirrored = True if (unicodedata.mirrored(char) == 1) else False
    nfc = unicodedata.normalize("NFC", char)
    nfd = unicodedata.normalize("NFD", char)

    if (short):
        print(char + "\t" + name + " (U+" + str(hexCodepoint).upper().replace("0X", "") + ")")
    else:
        print("Name          " + name)
        print("Character     " + char)
        print("Dec Codepoint " + str(decCodepoint))
        print("Hex Codepoint " + str(hexCodepoint))
        print("Lowercase     " + lower)
        print("Uppercase     " + upper)
        print("Category      " + category)
        print("Bidirectional " + bidirectional)
        print("Mirrored      " + str(mirrored))
        print("NFC           " + nfc)
        print("NFD           " + nfd)
### END print_Unicode_info ###


### BEGIN main ###
def main():
    # read command line parameters
    options = read_command_line_parameters(sys.argv)

    verbose = False
    if (('-v' in options) or ('--verbose' in options)):
        verbose = True

    quiet = False
    if (('-q' in options) or ('--quiet' in options)):
        quiet = True

    sortByCodepoint = True
    if (('-s' in options) or ('--sort' in options)):
        sortByCodepoint = False

    preserveTags = False
    if ('--preserve' in options):
        preserveTags = True

    outputEPUB = False
    if (('-u' in options) or ('--epub' in options)):
       outputEPUB  = True

    lookupArgument = None
    fuzzyLookup = False
    discoverLookup = False
    if ('-l' in options):
        lookupArgument = options['-l']
        fuzzyLookup = False
        discoverLookup = False
    if ('--lookup' in options):
        lookupArgument = options['--lookup']
        fuzzyLookup = False
        discoverLookup = False
    if ('-L' in options):
        lookupArgument = options['-L']
        fuzzyLookup = True
        discoverLookup = False
    if ('--Lookup' in options):
        lookupArgument = options['--Lookup']
        fuzzyLookup = True
        discoverLookup = False
    if ('-d' in options):
        lookupArgument = options['-d']
        fuzzyLookup = False
        discoverLookup = True
    if ('--discover' in options):
        lookupArgument = options['--discover']
        fuzzyLookup = False
        discoverLookup = True
    if ('-D' in options):
        lookupArgument = options['-D']
        fuzzyLookup = True
        discoverLookup = True
    if ('--Discover' in options):
        lookupArgument = options['--Discover']
        fuzzyLookup = True
        discoverLookup = True

    countCharacters = False
    if ('-c' in options) or ('--count' in options):
        countCharacters = True 

    fontFile = None
    if ('-f' in options) and ('--font' in options):
        print_error("You cannot specify both '%s' and '%s' parameters." % ('-f', '--font'))
    if ('-f' in options):
        fontFile = options['-f']
    if ('--font' in options):
        fontFile = options['--font']
   
    glyphsFile = None
    if ('-g' in options) and ('--glyphs' in options):
        print_error("You cannot specify both '%s' and '%s' parameters." % ('-g', '--glyphs'))
    if ('-g' in options):
        glyphsFile = options['-g']
    if ('--glyphs' in options):
        glyphsFile = options['--glyphs']

    if ((fontFile != None) and (glyphsFile != None)):
        print_error("You cannot specify both a font file and a glyph list file.")

    ebookFile = None
    if ('-e' in options) and ('--ebook' in options):
        print_error("You cannot specify both '%s' and '%s' parameters." % ('-e', '--ebook'))
    if ('-e' in options):
        ebookFile = options['-e']
    if ('--ebook' in options):
        ebookFile = options['--ebook']

    plainFile = None
    if ('-p' in options) and ('--plain' in options):
        print_error("You cannot specify both '%s' and '%s' parameters." % ('-p', '--plain'))
    if ('-p' in options):
        plainFile = options['-p']
    if ('--plain' in options):
        plainFile = options['--plain']

    if ((ebookFile != None) and (plainFile != None)):
        print_error("You cannot specify both an ebook file and a plain text file.")

    minimize = False
    minimizedFontFile = None
    if ((('-m' in options) or ('--minimize' in options)) and (fontFile != None)):
        minimize = True
        head, tail = os.path.split(fontFile)
        minimizedFontFile = os.path.join(head, "new." + tail)    

    if ((('-o' in options) or ('--output' in options)) and (fontFile != None)):
        if ('-o' in options) and ('--output' in options):
            print_error("You cannot specify both '%s' and '%s' parameters." % ('-o', '--output'))
        if ('-o' in options):
            minimizedFontFile = options['-o']
        if ('--output' in options):
            minimizedFontFile = options['--output']

    # if fontFile, ebookFile, countEbookFile are None, print usage and exit
    if ( (len(options) == 0) or
            ('-h' in options) or
            ('--help' in options) or
            ((fontFile == None) and
                (glyphsFile == None) and
                (ebookFile == None) and
                (plainFile == None) and
                (lookupArgument == None)) ):
        usage()
        sys.exit(0)
    
    # perform lookup?
    if (not lookupArgument == None):
        returnCode = perform_lookup(lookupArgument, fuzzyLookup, discoverLookup, quiet)
        if (returnCode == 8):
            print_info("Lookup for '%s' failed" % (lookupArgument), quiet)
        sys.exit(returnCode)

    # check that the specified file actually exists
    if ((fontFile != None) and (not check_existence(fontFile))):
        print_error("Font file '%s' does not exist or it cannot be read." % fontFile)
   
    if ((glyphsFile != None) and (not check_existence(glyphsFile))):
        print_error("List of glyphs file '%s' does not exist or it cannot be read." % glyphsFile)

    if ((ebookFile != None) and (not check_existence(ebookFile))):
        print_error("Ebook file '%s' does not exist or it cannot be read." % ebookFile)

    if ((plainFile != None) and (not check_existence(plainFile))):
        print_error("Ebook file '%s' does not exist or it cannot be read." % plainFile)

    # exit code to be returned
    returnCode = 0
    fontCharList = []
    # read fontFile
    if (fontFile != None):
        print_info("Reading glyphs contained in '%s'..." % (fontFile), quiet)
        fontCharList = get_font_char_list(fontFile)
        print_info("Reading glyphs contained in '%s'... Done" % (fontFile), quiet)
        if (outputEPUB):
            epub_filename = fontFile + ".epub"
            print_info("Creating '%s'..." % (epub_filename), quiet)
            epub_title = "List of Unicode characters in %s" % (fontFile)
            dec_list = get_dec_list(fontCharList, False)
            output_epub(dec_list, epub_title, epub_filename)
            print_info("Creating '%s'... Done" % (epub_filename), quiet)

    # read glyphsFile
    if (glyphsFile != None):
        print_info("Reading glyphs contained in '%s'..." % (glyphsFile), quiet)
        fontCharList = get_glyphs_char_list(glyphsFile)
        print_info("Reading glyphs contained in '%s'... Done" % (glyphsFile), quiet)
        if (outputEPUB):
            epub_filename = glyphsFile + ".epub"
            print_info("Creating '%s'..." % (epub_filename), quiet)
            epub_title = "List of Unicode characters in %s" % (glyphsFile)
            dec_list = get_dec_list(fontCharList, False)
            output_epub(dec_list, epub_title, epub_filename)
            print_info("Creating '%s'... Done" % (epub_filename), quiet)

    # read ebookFile
    ebookCharList = []
    if (ebookFile != None):
        print_info("Reading characters appearing in '%s'..." % (ebookFile), quiet)
        ebookCharList = get_ebook_char_list(ebookFile, preserveTags) 
        print_info("Reading characters appearing in '%s'... Done" % (ebookFile), quiet)
        if (countCharacters):
            print_info("Number of characters appearing in '%s'..." % (ebookFile), quiet)
            print(str(get_number_characters(ebookCharList)))
            print_info("Number of characters appearing in '%s'... Done" % (ebookFile), quiet)
            sys.exit(0)
        if (outputEPUB):
            epub_filename = ebookFile + ".epub"
            print_info("Creating '%s'..." % (epub_filename), quiet)
            epub_title = "List of Unicode characters in %s" % (ebookFile)
            dec_list = get_dec_list(ebookCharList, True)
            output_epub(dec_list, epub_title, epub_filename)
            print_info("Creating '%s'... Done" % (epub_filename), quiet)
    
    # read plainFile
    plainCharList = []
    if (plainFile != None):
        print_info("Reading characters appearing in '%s'..." % (plainFile), quiet)
        plainCharList = get_plain_char_list(plainFile, preserveTags)
        print_info("Reading characters appearing in '%s'... Done" % (plainFile), quiet)
        if (countCharacters):
            print_info("Number of characters appearing in '%s'..." % (plainFile), quiet)
            print(str(get_number_characters(plainCharList)))
            print_info("Number of characters appearing in '%s'... Done" % (plainFile), quiet)
            sys.exit(0)
        if (outputEPUB):
            epub_filename = plainFile + ".epub"
            print_info("Creating '%s'..." % (epub_filename), quiet)
            epub_title = "List of Unicode characters in %s" % (plainFile)
            dec_list = get_dec_list(plainCharList, True)
            output_epub(dec_list, epub_title, epub_filename)
            print_info("Creating '%s'... Done" % (epub_filename), quiet)

    # let's do what we should do
    comparedWithFont = False
    missing = []
    if ((fontFile != None) and (ebookFile != None)):
        missing = compare(fontCharList, ebookCharList)
        
        if (minimize):
            print_info("Minimizing font '%s' according to the characters appearing in '%s'..." % (fontFile, ebookFile), quiet)
            minimized_font_list = minimize_font(fontFile, ebookCharList, minimizedFontFile)
            print_info("Minimizing font '%s' according to the characters appearing in '%s'... Done" % (fontFile, ebookFile), quiet)
            print_info("Successfully created minimized font '%s'" % (minimizedFontFile), quiet)
            if (outputEPUB):
                epub_filename = minimizedFontFile + ".epub"
                print_info("Creating '%s'..." % (epub_filename), quiet)
                epub_title = "List of Unicode characters in %s" % (minimizedFontFile)
                dec_list = get_dec_list(minimized_font_list, False)
                output_epub(dec_list, epub_title, epub_filename)
                print_info("Creating '%s'... Done" % (epub_filename), quiet)

        if (len(missing) == 0):
            print_info("Your font '%s' contains all the glyphs required to display your ebook '%s'" % (fontFile, ebookFile), quiet)
        else:
            print_info("Your font '%s' does not contain all the glyphs required to display your ebook '%s'" % (fontFile, ebookFile), quiet)
            print_info("BEGIN Missing glyphs", quiet)
            print_char_list(missing, verbose, sortByCodepoint)
            print_info("END", quiet)
            if (outputEPUB):
                epub_filename = "missing.epub"
                print_info("Creating '%s'..." % (epub_filename), quiet)
                epub_title = "List of Unicode characters of %s missing in %s" % (ebookFile, fontFile)
                dec_list = get_dec_list(missing, True)
                output_epub(dec_list, epub_title, epub_filename)
                print_info("Creating '%s'... Done" % (epub_filename), quiet)
            returnCode = 2
        comparedWithFont = True
    
    if ((fontFile != None) and (plainFile != None)):
        missing = compare(fontCharList, plainCharList)
        
        if (minimize):
            print_info("Minimizing font '%s' according to the characters appearing in '%s'..." % (fontFile, plainFile), quiet)
            minimized_font_list = minimize_font(fontFile, ebookCharList, minimizedFontFile)
            print_info("Minimizing font '%s' according to the characters appearing in '%s'... Done" % (fontFile, plainFile), quiet)
            print_info("Successfully created minimized font '%s'" % (minimizedFontFile), quiet)
            if (outputEPUB):
                epub_filename = minimizedFontFile + ".epub"
                print_info("Creating '%s'..." % (epub_filename), quiet)
                epub_title = "List of Unicode characters in %s" % (minimizedFontFile)
                dec_list = get_dec_list(minimized_font_list, False)
                output_epub(dec_list, epub_title, epub_filename)
                print_info("Creating '%s'... Done" % (epub_filename), quiet)

        if (len(missing) == 0):
            print_info("Your font '%s' contains all the glyphs required to display your file '%s'" % (fontFile, plainFile), quiet)
        else:
            print_info("Your font '%s' does not contain all the glyphs required to display your file '%s'" % (fontFile, plainFile), quiet)
            print_info("BEGIN Missing glyphs", quiet)
            print_char_list(missing, verbose, sortByCodepoint)
            print_info("END", quiet)
            if (outputEPUB):
                epub_filename = "missing.epub"
                print_info("Creating '%s'..." % (epub_filename), quiet)
                epub_title = "List of Unicode characters of %s missing in %s" % (plainFile, fontFile)
                dec_list = get_dec_list(missing, True)
                output_epub(dec_list, epub_title, epub_filename)
                print_info("Creating '%s'... Done" % (epub_filename), quiet)
            returnCode = 2
        comparedWithFont = True

    if (not comparedWithFont):
        if ((fontFile != None) and (minimizedFontFile != None)):
            print_info("Converting font '%s' into '%s'..." % (fontFile, minimizedFontFile), quiet)
            convert_font(fontFile, minimizedFontFile)
            print_info("Converting font '%s' into '%s'... Done" % (fontFile, minimizedFontFile), quiet)
        if (fontFile != None):
            print_info("BEGIN Font file '%s' contains the following Unicode characters" % (fontFile), quiet)
            print_glyph_list(fontCharList, verbose)
            print_info("END", quiet)
        if (glyphsFile != None):
            print_info("BEGIN Glyph list file '%s' contains the following Unicode characters" % (glyphsFile), quiet)
            print_glyph_list(fontCharList, verbose)
            print_info("END", quiet)
        if (ebookFile != None):
            print_info("BEGIN Ebook file '%s' contains the following Unicode characters" % (ebookFile), quiet)
            print_char_list(ebookCharList, verbose, sortByCodepoint)
            print_info("END", quiet)
        if (plainFile != None):
            print_info("BEGIN Plain text file '%s' contains the following Unicode characters" % (plainFile), quiet)
            print_char_list(plainCharList, verbose, sortByCodepoint)
            print_info("END", quiet)
   
    if (minimizedFontFile != None):
        if (not check_existence(minimizedFontFile)):
            print_error("Failed to minimize/convert '%s' into '%s'" % (fontFile, minimizedFontFile), False, 4)

    # return proper exit code
    sys.exit(returnCode)
### END main ###



if __name__ == '__main__':
    # TODO let the user specify file encoding instead
    #Python2#
    reload(sys)
    #Python2#
    sys.setdefaultencoding("utf-8")
    main()

