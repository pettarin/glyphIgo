#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto@albertopettarin.it)'
__copyright__   = '2012-2015 Alberto Pettarin (alberto@albertopettarin.it)'
__version__     = 'v3.0.3'
__date__        = '2015-06-07'
__description__ = 'glyphIgo is a Swiss Army knife for dealing with fonts and EPUB eBooks'


### BEGIN changelog ###
#
# 3.0.3 2015-06-07 Added option to remove the char set while subsetting a font
# 3.0.2 2014-10-19 Support for bash/zsh autocompletion via argcomplete
# 3.0.1 2014-10-08 Better hex/dec char lookup, added range option to list command
# 3.0.0 2014-07-31 Heavy code refactoring, switched to argparse, changed CLI names
# 2.0.3 2014-07-29 Font obfuscation/deobfuscation
# 2.0.2 2014-04-18 Fixed bug #3
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



try:
    import argcomplete
except ImportError:
    pass 

import argparse
import codecs
import collections
import fontforge
import hashlib
import htmlentitydefs
import os
import re
import sys
import unicodedata
import zipfile


class CustomParser:
    
    COMMAND_CHECK = "check"
    COMMAND_CONVERT = "convert"
    COMMAND_COUNT = "count"
    COMMAND_LIST = "list"
    COMMAND_LOOKUP = "lookup"
    COMMAND_OBFUSCATE = "obfuscate"
    COMMAND_SUBSET = "subset"
    COMMAND_ALL = [
        COMMAND_CHECK,
        COMMAND_CONVERT,
        COMMAND_COUNT,
        COMMAND_LIST,
        COMMAND_LOOKUP,
        COMMAND_OBFUSCATE,
        COMMAND_SUBSET
    ]
    COMMAND_DEFAULT = COMMAND_LIST 
    
    COMMAND_REQUIRED_PARAMETERS = {
        COMMAND_CHECK: [ ["ebook", "plain"], ["font", "glyphs"] ],
        COMMAND_CONVERT: [ ["font"], ["output"] ],
        COMMAND_COUNT: [ ["ebook", "plain"] ],
        COMMAND_LIST: [ ["blocks", "ebook", "font", "glyphs", "plain", "range"] ],
        COMMAND_LOOKUP: [ ["character"] ],
        COMMAND_OBFUSCATE: [ ["font"], ["id"] ],
        COMMAND_SUBSET: [ ["ebook", "plain"], ["font"] ]
    } 
    
    DESCRIPTION = __description__
    
    EXAMPLES = [
        {
            "msg": "Print this usage message",
            "cmd": ["-h"]
        },
        {
            "msg": "Check whether all the characters in ebook.epub can be displayed by font.ttf",
            "cmd": ["check -f font.ttf -e ebook.epub"]
        },
        {
            "msg": "As above, but use font_glyph_list.txt containing a list of decimal codepoints for the font glyphs",
            "cmd": ["check -g font_glyph_list.txt -e ebook.epub"]
        },
        {
            "msg": "As above, but sort missing characters (if any) by their count (in ebook.epub) instead of by Unicode codepoint",
            "cmd": ["check -f font.ttf -e ebook.epub -s"]
        },
        {
            "msg": "As above, but also create missing.epub containing the list of missing Unicode characters",
            "cmd": ["check -f font.ttf -e ebook.epub -u -o missing.epub"]
        },
        {
            "msg": "Convert font.ttf (TTF) into font.otf (OTF)",
            "cmd": ["convert -f font.ttf -o font.otf"]
        },
        {
            "msg": "Count the number of characters in ebook.epub",
            "cmd": ["count -e ebook.epub"]
        },
        {
            "msg": "As above, but preserve tags",
            "cmd": ["count -e ebook.epub --preserve"]
        },
        {
            "msg": "Print the list of glyphs in font.ttf",
            "cmd": ["list -f font.ttf"]
        },
        {
            "msg": "As above, but just output the decimal codepoints",
            "cmd": ["list -f font.ttf -q"]
        },
        {
            "msg": "Print the list of characters in ebook.epub",
            "cmd": ["list -e ebook.epub"]
        },
        {
            "msg": "As above, but also create list.epub containing the list of Unicode characters",
            "cmd": ["list -e ebook.epub -u -o list.epub"]
        },
        {
            "msg": "Print the list of characters in page.xhtml",
            "cmd": ["list -p page.xhtml"]
        },
        {
            "msg": "Print the list of characters in the range 0x2200-0x22ff (Mathematical Operators)",
            "cmd": ["list -r 0x2200-0x22ff", "list -r \"Mathematical Operators\""]
        },
        {
            "msg": "Print the range and name of Unicode blocks",
            "cmd": ["list --blocks"]
        },
        {
            "msg": "Lookup for information for Unicode character",
            "cmd": ["lookup -c 8253", "lookup -c 0x203d", "lookup -c ‽", "lookup -c \"INTERROBANG\""]
        },
        {
            "msg": "As above, but print compact output",
            "cmd": ["lookup --compact -c 8253", "lookup --compact -c 0x203d", "lookup --compact -c ‽", "lookup --compact -c \"INTERROBANG\""]
        },
        {
            "msg": "Heuristic lookup for information for Unicode characters which are Greek omega letters with oxia",
            "cmd": ["lookup --heuristic -c \"GREEK OMEGA OXIA\""]
        },
        {
            "msg": "(De)obfuscate font.otf into obf.font.otf using the given id and the IDPF algorithm",
            "cmd": ["obfuscate -f font.otf -i \"urn:uuid:9a0ca9ab-9e33-4181-b2a3-e7f2ceb8e9bd\" -o obf.font.otf"]
        },
        {
            "msg": "As above, but use Adobe algorithm",
            "cmd": ["obfuscate -f font.otf -i \"urn:uuid:9a0ca9ab-9e33-4181-b2a3-e7f2ceb8e9bd\" -o obf.font.otf --adobe"]
        },
        {
            "msg": "Subset font.ttf into min.font.otf by copying only the glyphs appearing in ebook.epub",
            "cmd": ["subset -f font.ttf -e ebook.epub -o min.font.otf"]
        },
        {
            "msg": "Subset font.ttf into rem.font.ttf by removing the glyphs appearing in list.txt",
            "cmd": ["subset -f font.ttf -p list.txt -o rem.font.ttf --exclude"]
        },
        {
            "msg": "",
            "cmd": [""]
        }
    ]

    EXIT_CODE_OK = 0
    EXIT_CODE_RESERVED = 1
    EXIT_CODE_INVALID_ARGUMENT = 2 # argparse default
    EXIT_CODE_MISSING_GLYPHS = 4
    EXIT_CODE_COMMAND_FAILED = 8
    EXIT_CODES = [
        {
            "value": EXIT_CODE_OK,
            "description": "no error"
        },
        {
            "value": EXIT_CODE_RESERVED,
            "description": "RESERVED"
        },
        {
            "value": EXIT_CODE_INVALID_ARGUMENT,
            "description": "invalid command line argument(s)"
        },
        {
            "value": EXIT_CODE_MISSING_GLYPHS,
            "description": "missing glyphs in the font file to correctly display the given ebook or file"
        },
        {
            "value": EXIT_CODE_COMMAND_FAILED,
            "description": "failure while executing the requested command"
        }
    ]

    OPTIONAL_PARAMETERS = [
        {
            "short": "-c",
            "long": "--character",
            "help": "lookup CHARACTER, specified as name, partial name, dec/hex codepoint, or Unicode character",
            "action": "store"
        },
        {
            "short": "-d",
            "long": "--decode",
            "help": "use DECODE encoding to decode the input EBOOK or PLAIN file",
            "action": "store"
        },
        {
            "short": "-e",
            "long": "--ebook",
            "help": "ebook file, in EPUB/ZIP format",
            "action": "store"
        },
        {
            "short": "-f",
            "long": "--font",
            "help": "font file, in TTF/OTF/WOFF format",
            "action": "store"
        },
        {
            "short": "-g",
            "long": "--glyphs",
            "help": "font file, specified as a list of decimal Unicode codepoints contained in plain text file GLYPHS, one codepoint per line",
            "action": "store"
        },
        {
            "short": "-i",
            "long": "--id",
            "help": "(de)obfuscate FONT using ID to compute the obfuscation key",
            "action": "store"
        },
        {
            "short": "-o",
            "long": "--output",
            "help": "create OUTPUT file",
            "action": "store"
        },
        {
            "short": "-p",
            "long": "--plain",
            "help": "ebook file, in plain text format",
            "action": "store"
        },
        {
            "short": "-r",
            "long": "--range",
            "help": "range, in '0x????-0x????' or '????-????' format",
            "action": "store"
        },
        {
            "short": "-q",
            "long": "--quiet",
            "help": "quiet output",
            "action": "store_true"
        },
        {
            "short": "-s",
            "long": "--sort",
            "help": "sort output by character count instead of character codepoint",
            "action": "store_true"
        },
        {
            "short": "-u",
            "long": "--epub",
            "help": "output an EPUB file containing the Unicode characters in the input file(s)",
            "action": "store_true"
        },
        {
            "short": "-v",
            "long": "--verbose",
            "help": "verbose output",
            "action": "store_true"
        },
        {
            "short": "-w",
            "long": "--nohumanreadable",
            "help": "verbose output without human readable messages",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--adobe",
            "help": "use Adobe obfuscation algorithm",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--blocks",
            "help": "print range and name of Unicode blocks",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--compact",
            "help": "compact lookup output (Unicode character, name, and codepoint only)",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--exact",
            "help": "use exact Unicode lookup (default)",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--exclude",
            "help": "exclude the characters in EBOOK or PLAIN from the output",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--full",
            "help": "full lookup output (default)",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--heuristic",
            "help": "use heuristic Unicode lookup",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--idpf",
            "help": "use IDPF obfuscation algorithm (default)",
            "action": "store_true"
        },
        {
            "short": None,
            "long": "--preserve",
            "help": "preserve X(HT)ML tags instead of stripping them away",
            "action": "store_true"
        }
    ]

    OPTIONAL_PARAMETERS_CONFLICTS = [
        [ "blocks", "character", "ebook", "plain", "range" ],
        [ "blocks", "character", "font", "glyphs", "range" ],
        [ "quiet", "verbose", "nohumanreadable" ],
        [ "adobe", "idpf" ],
        [ "compact", "full" ],
        [ "exact", "heuristic" ]
    ]

    VERSION = __version__

    def __check_arguments(self, args):
        # check conflicts between optional parameters
        for group in self.OPTIONAL_PARAMETERS_CONFLICTS:
            count = 0
            found = []
            for parameter in group:
                if (parameter in args):
                    count += 1
                    found.append(parameter)
            if (count > 1):
                msg = "Conflicting optional arguments: %s\n" % (str(found))
                return False, msg
        
        # check arguments required by the given command 
        for condition in self.COMMAND_REQUIRED_PARAMETERS[args.command]:
            found = False
            for parameter in condition:
                found = found or (parameter in args)
            if (not found):
                msg = "After command '%s' you must specify %s\n" % (args.command, self.__get_pretty_or_string(condition))
                return False, msg
        
        # all OK
        return True, None

    def __get_pretty_or_string(self, array):
        if (len(array) == 1):
            return "'--%s'" % (array[0])
        s = ""
        for a in array[:-1]:
            s += "'--%s' or " % (a)
        s += "'--%s'" % (array[-1])
        return s

    def __get_description_string(self):
        return self.DESCRIPTION
   
    def __get_exit_codes_string(self):
        codes = self.EXIT_CODES
        s = "exit codes:\n"
        trailing_characters = "  " 
        value_separator = " = "
        tot = len(str(codes[-1]["value"]))
        for c in codes:
            value = str(c["value"])
            description = c["description"]
            n = trailing_characters + " " * (tot - len(value))
            s += n + value + value_separator + description + "\n"
        return s

    def __get_examples_string(self):
        examples = self.EXAMPLES
        s = "examples:\n"
        trailing_characters = "  " 
        number_separator = ". "
        i = 1
        tot = len(str(len(examples)))
        for e in examples:
            msg = e["msg"]
            cmd = e["cmd"]
            if (len(msg) > 0):
                n = str(i)
                n = trailing_characters + " " * (tot - len(n)) + n
                s += n + number_separator + msg + "\n"
                for c in cmd:
                    s += trailing_characters + (" " * (tot + len(number_separator))) + "$ " + sys.argv[0] + " " + c + "\n"
                s += "\n"
            else:
                s += trailing_characters + "\n"
            i += 1
        return s

    def __get_optional_parameters(self):
        return self.OPTIONAL_PARAMETERS

    def __get_usage(self):
        return "$ " + sys.argv[0] + " " + "|".join(self.COMMAND_ALL) + " [options]"

    def __get_version(self):
        return self.VERSION

    def get_arguments(self):
        program_usage = self.__get_usage()
        program_description = self.__get_description_string()
        program_epilog = self.__get_exit_codes_string() + "\n" + self.__get_examples_string()

        parser = argparse.ArgumentParser(
            usage=program_usage,
            description=program_description,
            epilog=program_epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
                "command",
                help="command", 
                action="store",
                default=self.COMMAND_DEFAULT,
                choices=self.COMMAND_ALL
        )
        parser.add_argument(
                "--version",
                help="print version and exit",
                action="version",
                version=self.__get_version())

        for param in self.__get_optional_parameters():
            if (param["short"]):
                parser.add_argument(
                    param["short"],
                    param["long"],
                    help=param["help"],
                    action=param["action"],
                    default=argparse.SUPPRESS
                )
            elif (param["long"]):
                parser.add_argument(
                    param["long"],
                    help=param["help"],
                    action=param["action"],
                    default=argparse.SUPPRESS
                )

        # try using argcomplete
        try:
            argcomplete.autocomplete(parser)
        except:
            pass 
       
        # parse arguments
        args = parser.parse_args()
        
        # standard ArgumentParser checker is cumbersome and limited
        isOK, msg = self.__check_arguments(args)
        if (not isOK):
            msg = "[ERROR] " + msg
            parser.exit(status=self.EXIT_CODE_INVALID_ARGUMENT, message=msg)
        
        return args



class GlyphIgo:

    # match 0x???? or x???? or ????
    PATTERN_HEX_0x = r"^0x[0-9A-Fa-f]+$"
    PATTERN_HEX_x = r"^x[0-9A-Fa-f]+$"
    PATTERN_DEC = r"^[0-9]+$"

    # match ranges: 0x????-0x???? or x????-x???? or ????-????
    PATTERN_RANGE_HEX_0x = r"^0x([0-9A-Fa-f]+)-0x([0-9A-Fa-f]+)$"
    PATTERN_RANGE_HEX_x = r"^x([0-9A-Fa-f]+)-x([0-9A-Fa-f]+)$"
    PATTERN_RANGE_DEC = r"^([0-9]+)-([0-9]+)$"

    # Unicode blocks from http://www.unicode.org/Public/UNIDATA/Blocks.txt
    # see also the Unicode Terms of Use http://www.unicode.org/copyright.html
    UNICODE_BLOCKS = [
        ["0000", "007f", "Basic Latin"],
        ["0080", "00ff", "Latin-1 Supplement"],
        ["0100", "017f", "Latin Extended-A"],
        ["0180", "024f", "Latin Extended-B"],
        ["0250", "02af", "IPA Extensions"],
        ["02b0", "02ff", "Spacing Modifier Letters"],
        ["0300", "036f", "Combining Diacritical Marks"],
        ["0370", "03ff", "Greek and Coptic"],
        ["0400", "04ff", "Cyrillic"],
        ["0500", "052f", "Cyrillic Supplement"],
        ["0530", "058f", "Armenian"],
        ["0590", "05ff", "Hebrew"],
        ["0600", "06ff", "Arabic"],
        ["0700", "074f", "Syriac"],
        ["0750", "077f", "Arabic Supplement"],
        ["0780", "07bf", "Thaana"],
        ["07c0", "07ff", "NKo"],
        ["0800", "083f", "Samaritan"],
        ["0840", "085f", "Mandaic"],
        ["08a0", "08ff", "Arabic Extended-A"],
        ["0900", "097f", "Devanagari"],
        ["0980", "09ff", "Bengali"],
        ["0a00", "0a7f", "Gurmukhi"],
        ["0a80", "0aff", "Gujarati"],
        ["0b00", "0b7f", "Oriya"],
        ["0b80", "0bff", "Tamil"],
        ["0c00", "0c7f", "Telugu"],
        ["0c80", "0cff", "Kannada"],
        ["0d00", "0d7f", "Malayalam"],
        ["0d80", "0dff", "Sinhala"],
        ["0e00", "0e7f", "Thai"],
        ["0e80", "0eff", "Lao"],
        ["0f00", "0fff", "Tibetan"],
        ["1000", "109f", "Myanmar"],
        ["10a0", "10ff", "Georgian"],
        ["1100", "11ff", "Hangul Jamo"],
        ["1200", "137f", "Ethiopic"],
        ["1380", "139f", "Ethiopic Supplement"],
        ["13a0", "13ff", "Cherokee"],
        ["1400", "167f", "Unified Canadian Aboriginal Syllabics"],
        ["1680", "169f", "Ogham"],
        ["16a0", "16ff", "Runic"],
        ["1700", "171f", "Tagalog"],
        ["1720", "173f", "Hanunoo"],
        ["1740", "175f", "Buhid"],
        ["1760", "177f", "Tagbanwa"],
        ["1780", "17ff", "Khmer"],
        ["1800", "18af", "Mongolian"],
        ["18b0", "18ff", "Unified Canadian Aboriginal Syllabics Extended"],
        ["1900", "194f", "Limbu"],
        ["1950", "197f", "Tai Le"],
        ["1980", "19df", "New Tai Lue"],
        ["19e0", "19ff", "Khmer Symbols"],
        ["1a00", "1a1f", "Buginese"],
        ["1a20", "1aaf", "Tai Tham"],
        ["1ab0", "1aff", "Combining Diacritical Marks Extended"],
        ["1b00", "1b7f", "Balinese"],
        ["1b80", "1bbf", "Sundanese"],
        ["1bc0", "1bff", "Batak"],
        ["1c00", "1c4f", "Lepcha"],
        ["1c50", "1c7f", "Ol Chiki"],
        ["1cc0", "1ccf", "Sundanese Supplement"],
        ["1cd0", "1cff", "Vedic Extensions"],
        ["1d00", "1d7f", "Phonetic Extensions"],
        ["1d80", "1dbf", "Phonetic Extensions Supplement"],
        ["1dc0", "1dff", "Combining Diacritical Marks Supplement"],
        ["1e00", "1eff", "Latin Extended Additional"],
        ["1f00", "1fff", "Greek Extended"],
        ["2000", "206f", "General Punctuation"],
        ["2070", "209f", "Superscripts and Subscripts"],
        ["20a0", "20cf", "Currency Symbols"],
        ["20d0", "20ff", "Combining Diacritical Marks for Symbols"],
        ["2100", "214f", "Letterlike Symbols"],
        ["2150", "218f", "Number Forms"],
        ["2190", "21ff", "Arrows"],
        ["2200", "22ff", "Mathematical Operators"],
        ["2300", "23ff", "Miscellaneous Technical"],
        ["2400", "243f", "Control Pictures"],
        ["2440", "245f", "Optical Character Recognition"],
        ["2460", "24ff", "Enclosed Alphanumerics"],
        ["2500", "257f", "Box Drawing"],
        ["2580", "259f", "Block Elements"],
        ["25a0", "25ff", "Geometric Shapes"],
        ["2600", "26ff", "Miscellaneous Symbols"],
        ["2700", "27bf", "Dingbats"],
        ["27c0", "27ef", "Miscellaneous Mathematical Symbols-A"],
        ["27f0", "27ff", "Supplemental Arrows-A"],
        ["2800", "28ff", "Braille Patterns"],
        ["2900", "297f", "Supplemental Arrows-B"],
        ["2980", "29ff", "Miscellaneous Mathematical Symbols-B"],
        ["2a00", "2aff", "Supplemental Mathematical Operators"],
        ["2b00", "2bff", "Miscellaneous Symbols and Arrows"],
        ["2c00", "2c5f", "Glagolitic"],
        ["2c60", "2c7f", "Latin Extended-C"],
        ["2c80", "2cff", "Coptic"],
        ["2d00", "2d2f", "Georgian Supplement"],
        ["2d30", "2d7f", "Tifinagh"],
        ["2d80", "2ddf", "Ethiopic Extended"],
        ["2de0", "2dff", "Cyrillic Extended-A"],
        ["2e00", "2e7f", "Supplemental Punctuation"],
        ["2e80", "2eff", "CJK Radicals Supplement"],
        ["2f00", "2fdf", "Kangxi Radicals"],
        ["2ff0", "2fff", "Ideographic Description Characters"],
        ["3000", "303f", "CJK Symbols and Punctuation"],
        ["3040", "309f", "Hiragana"],
        ["30a0", "30ff", "Katakana"],
        ["3100", "312f", "Bopomofo"],
        ["3130", "318f", "Hangul Compatibility Jamo"],
        ["3190", "319f", "Kanbun"],
        ["31a0", "31bf", "Bopomofo Extended"],
        ["31c0", "31ef", "CJK Strokes"],
        ["31f0", "31ff", "Katakana Phonetic Extensions"],
        ["3200", "32ff", "Enclosed CJK Letters and Months"],
        ["3300", "33ff", "CJK Compatibility"],
        ["3400", "4dbf", "CJK Unified Ideographs Extension A"],
        ["4dc0", "4dff", "Yijing Hexagram Symbols"],
        ["4e00", "9fff", "CJK Unified Ideographs"],
        ["a000", "a48f", "Yi Syllables"],
        ["a490", "a4cf", "Yi Radicals"],
        ["a4d0", "a4ff", "Lisu"],
        ["a500", "a63f", "Vai"],
        ["a640", "a69f", "Cyrillic Extended-B"],
        ["a6a0", "a6ff", "Bamum"],
        ["a700", "a71f", "Modifier Tone Letters"],
        ["a720", "a7ff", "Latin Extended-D"],
        ["a800", "a82f", "Syloti Nagri"],
        ["a830", "a83f", "Common Indic Number Forms"],
        ["a840", "a87f", "Phags-pa"],
        ["a880", "a8df", "Saurashtra"],
        ["a8e0", "a8ff", "Devanagari Extended"],
        ["a900", "a92f", "Kayah Li"],
        ["a930", "a95f", "Rejang"],
        ["a960", "a97f", "Hangul Jamo Extended-A"],
        ["a980", "a9df", "Javanese"],
        ["a9e0", "a9ff", "Myanmar Extended-B"],
        ["aa00", "aa5f", "Cham"],
        ["aa60", "aa7f", "Myanmar Extended-A"],
        ["aa80", "aadf", "Tai Viet"],
        ["aae0", "aaff", "Meetei Mayek Extensions"],
        ["ab00", "ab2f", "Ethiopic Extended-A"],
        ["ab30", "ab6f", "Latin Extended-E"],
        ["abc0", "abff", "Meetei Mayek"],
        ["ac00", "d7af", "Hangul Syllables"],
        ["d7b0", "d7ff", "Hangul Jamo Extended-B"],
        ["d800", "db7f", "High Surrogates"],
        ["db80", "dbff", "High Private Use Surrogates"],
        ["dc00", "dfff", "Low Surrogates"],
        ["e000", "f8ff", "Private Use Area"],
        ["f900", "faff", "CJK Compatibility Ideographs"],
        ["fb00", "fb4f", "Alphabetic Presentation Forms"],
        ["fb50", "fdff", "Arabic Presentation Forms-A"],
        ["fe00", "fe0f", "Variation Selectors"],
        ["fe10", "fe1f", "Vertical Forms"],
        ["fe20", "fe2f", "Combining Half Marks"],
        ["fe30", "fe4f", "CJK Compatibility Forms"],
        ["fe50", "fe6f", "Small Form Variants"],
        ["fe70", "feff", "Arabic Presentation Forms-B"],
        ["ff00", "ffef", "Halfwidth and Fullwidth Forms"],
        ["fff0", "ffff", "Specials"],
        ["10000", "1007f", "Linear B Syllabary"],
        ["10080", "100ff", "Linear B Ideograms"],
        ["10100", "1013f", "Aegean Numbers"],
        ["10140", "1018f", "Ancient Greek Numbers"],
        ["10190", "101cf", "Ancient Symbols"],
        ["101d0", "101ff", "Phaistos Disc"],
        ["10280", "1029f", "Lycian"],
        ["102a0", "102df", "Carian"],
        ["102e0", "102ff", "Coptic Epact Numbers"],
        ["10300", "1032f", "Old Italic"],
        ["10330", "1034f", "Gothic"],
        ["10350", "1037f", "Old Permic"],
        ["10380", "1039f", "Ugaritic"],
        ["103a0", "103df", "Old Persian"],
        ["10400", "1044f", "Deseret"],
        ["10450", "1047f", "Shavian"],
        ["10480", "104af", "Osmanya"],
        ["10500", "1052f", "Elbasan"],
        ["10530", "1056f", "Caucasian Albanian"],
        ["10600", "1077f", "Linear A"],
        ["10800", "1083f", "Cypriot Syllabary"],
        ["10840", "1085f", "Imperial Aramaic"],
        ["10860", "1087f", "Palmyrene"],
        ["10880", "108af", "Nabataean"],
        ["10900", "1091f", "Phoenician"],
        ["10920", "1093f", "Lydian"],
        ["10980", "1099f", "Meroitic Hieroglyphs"],
        ["109a0", "109ff", "Meroitic Cursive"],
        ["10a00", "10a5f", "Kharoshthi"],
        ["10a60", "10a7f", "Old South Arabian"],
        ["10a80", "10a9f", "Old North Arabian"],
        ["10ac0", "10aff", "Manichaean"],
        ["10b00", "10b3f", "Avestan"],
        ["10b40", "10b5f", "Inscriptional Parthian"],
        ["10b60", "10b7f", "Inscriptional Pahlavi"],
        ["10b80", "10baf", "Psalter Pahlavi"],
        ["10c00", "10c4f", "Old Turkic"],
        ["10e60", "10e7f", "Rumi Numeral Symbols"],
        ["11000", "1107f", "Brahmi"],
        ["11080", "110cf", "Kaithi"],
        ["110d0", "110ff", "Sora Sompeng"],
        ["11100", "1114f", "Chakma"],
        ["11150", "1117f", "Mahajani"],
        ["11180", "111df", "Sharada"],
        ["111e0", "111ff", "Sinhala Archaic Numbers"],
        ["11200", "1124f", "Khojki"],
        ["112b0", "112ff", "Khudawadi"],
        ["11300", "1137f", "Grantha"],
        ["11480", "114df", "Tirhuta"],
        ["11580", "115ff", "Siddham"],
        ["11600", "1165f", "Modi"],
        ["11680", "116cf", "Takri"],
        ["118a0", "118ff", "Warang Citi"],
        ["11ac0", "11aff", "Pau Cin Hau"],
        ["12000", "123ff", "Cuneiform"],
        ["12400", "1247f", "Cuneiform Numbers and Punctuation"],
        ["13000", "1342f", "Egyptian Hieroglyphs"],
        ["16800", "16a3f", "Bamum Supplement"],
        ["16a40", "16a6f", "Mro"],
        ["16ad0", "16aff", "Bassa Vah"],
        ["16b00", "16b8f", "Pahawh Hmong"],
        ["16f00", "16f9f", "Miao"],
        ["1b000", "1b0ff", "Kana Supplement"],
        ["1bc00", "1bc9f", "Duployan"],
        ["1bca0", "1bcaf", "Shorthand Format Controls"],
        ["1d000", "1d0ff", "Byzantine Musical Symbols"],
        ["1d100", "1d1ff", "Musical Symbols"],
        ["1d200", "1d24f", "Ancient Greek Musical Notation"],
        ["1d300", "1d35f", "Tai Xuan Jing Symbols"],
        ["1d360", "1d37f", "Counting Rod Numerals"],
        ["1d400", "1d7ff", "Mathematical Alphanumeric Symbols"],
        ["1e800", "1e8df", "Mende Kikakui"],
        ["1ee00", "1eeff", "Arabic Mathematical Alphabetic Symbols"],
        ["1f000", "1f02f", "Mahjong Tiles"],
        ["1f030", "1f09f", "Domino Tiles"],
        ["1f0a0", "1f0ff", "Playing Cards"],
        ["1f100", "1f1ff", "Enclosed Alphanumeric Supplement"],
        ["1f200", "1f2ff", "Enclosed Ideographic Supplement"],
        ["1f300", "1f5ff", "Miscellaneous Symbols and Pictographs"],
        ["1f600", "1f64f", "Emoticons"],
        ["1f650", "1f67f", "Ornamental Dingbats"],
        ["1f680", "1f6ff", "Transport and Map Symbols"],
        ["1f700", "1f77f", "Alchemical Symbols"],
        ["1f780", "1f7ff", "Geometric Shapes Extended"],
        ["1f800", "1f8ff", "Supplemental Arrows-C"],
        ["20000", "2a6df", "CJK Unified Ideographs Extension B"],
        ["2a700", "2b73f", "CJK Unified Ideographs Extension C"],
        ["2b740", "2b81f", "CJK Unified Ideographs Extension D"],
        ["2f800", "2fa1f", "CJK Compatibility Ideographs Supplement"],
        ["e0000", "e007f", "Tags"],
        ["e0100", "e01ef", "Variation Selectors Supplement"],
        ["f0000", "fffff", "Supplementary Private Use Area-A"],
        ["100000", "10ffff", "Supplementary Private Use Area-B"],
    ]

    __args = None

    def __init__(self, args):
        self.__args = args

    def __print_error(self, s):
        sys.stderr.write("[ERROR] %s\n" % (s))

    def __print_info(self, s):
        if not (("quiet" in self.__args) or ("nohumanreadable" in self.__args)):
            print "[INFO] %s" % (s)

    def __get_ebook_char_list(self):
        # TODO allow full EPUB parsing
        text = ""
        zfile = zipfile.ZipFile(self.__args.ebook)
        for name in zfile.namelist():
            if ((name.lower().endswith(".xhtml")) or
                (name.lower().endswith(".html")) or
                ((name.lower().endswith(".xml")) and (not name.startswith("META-INF")))):
                file_bytes = zfile.read(name)
                try:
                    # TODO check if utf-8 is always ok
                    text += file_bytes.decode('utf-8')
                except:
                    continue
        zfile.close()
        return self.__clean_text(text)

    def __get_font_char_list(self, only_chars=False):
        chars = []
        font = fontforge.open(self.__args.font)
        for x in font.glyphs():
            if (x.unicode > -1):
                c = unichr(x.unicode)
                if (only_chars):
                    chars.append(c)
                else:
                    chars.append([c, 1])
        return chars

    def __get_glyphs_char_list(self, only_chars=False):
        chars = []
        decode = "utf-8"
        if ("decode" in self.__args):
            decode = self.__args.decode
        f = codecs.open(self.__args.glyphs, "r", decode, "ignore")
        text = f.read()
        f.close()
        for g in text.splitlines():
            if ((len(g) > 0) and (g[0] != "#")):
                if ((len(g) > 2) and (g[0:2] == "0x")):
                    c = unichr(int(g[2:], 16))
                elif ((len(g) > 1) and (g[0] == "x")):
                    c = unichr(int(g[1:], 16))
                else:
                    c = unichr(int(g))
                if (only_chars):
                    chars.append(c)
                else:
                    chars.append([c, 1])
        return chars

    def __get_plain_char_list(self):
        decode = "utf-8"
        if ("decode" in self.__args):
            decode = self.__args.decode
        f = codecs.open(self.__args.plain, "r", decode, "ignore")
        text = f.read()
        f.close()
        return self.__clean_text(text)

    def __get_range_char_list(self):
        query = self.__args.range.lower()
        
        opt = [
                [self.PATTERN_RANGE_HEX_0x, 16], 
                [self.PATTERN_RANGE_HEX_x, 16], 
                [self.PATTERN_RANGE_DEC, 10]
              ]

        for o in opt:
            m = re.match(o[0], query)
            if (m != None):
                start = int(m.group(1), o[1])
                stop = int(m.group(2), o[1])
                return self.__get_range(start, stop)
       
        # lookup for Unicode block name
        for b in self.UNICODE_BLOCKS:
            if (b[2].lower() == query):
                start = int(b[0], 16)
                stop = int(b[1], 16)
                return self.__get_range(start, stop)

        return []

    # helper: generate a list of Unicode characters
    # whose codepoint is between start and stop
    def __get_range(self, start, stop):
        chars = []
        for i in range(start, stop + 1):
            chars.append([unichr(i), 1])
        return chars

    # helper: clean text and produce a list of character,
    # each with its number of occurrences
    def __clean_text(self, text):
        def remove_tags(s):
            #TODO improve this?
            s = s.replace("\n", " ")
            s = s.replace("\r", " ")
            s = re.sub(r"[ ]+", " ", s)
            s = re.sub(r"<[^>]+>", "", s)
            return s

        def decode_xml_entities(s):
            def fix(m):
                c = m.group(1)
                # escape the escape sequences
                if (c == "amp"):
                    return "&"
                if (c == "lt"):
                    return "<"
                if (c == "gt"):
                    return ">"
                if (c in htmlentitydefs.name2codepoint):
                    # named entity
                    return unichr(htmlentitydefs.name2codepoint[c])
                else:
                    # TODO this is ugly
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

            return re.sub(r"&([#a-z0-9]+);", fix, s)

        def filter_string(s):
            mydict = collections.defaultdict(int)
            for mychar in s:
                mydict[mychar] += 1
            mylist = []
            for mychar in sorted(mydict.keys()):
                mylist.append([ mychar, mydict[mychar] ])
            return mylist
        
        if (not ("preserve" in self.__args)):
            text = remove_tags(text)
        text = decode_xml_entities(text)
        chars = filter_string(text)
        return chars
   
    # helper: pretty print Unicode blocks list
    def __print_block_list(self):
        self.__print_info("Range\tStart\tStop\tStart\tStop\tName")
        for b in self.UNICODE_BLOCKS:
            print "0x%s-0x%s\t0x%s\t0x%s\t%s\t%s\t%s" % (b[0], b[1], b[0], b[1], int(b[0], 16), int(b[1], 16), b[2])

    # helper: pretty print char list
    def __print_char_list(self, chars):
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
        
        if ("sort" in self.__args):
            chars.sort(key=lambda x: -x[1])
        if ("quiet" in self.__args):
            for c in chars:
                decCodePoint = ord(c[0])
                print "%s" % (decCodePoint)
        else:
            for c in chars:
                name = unicodedata.name(c[0], 'UNKNOWN NAME')
                decCodePoint = ord(c[0])
                hexCodePoint = hex(decCodePoint)
                if (type(c) is list):
                    # c = [ char, count ]
                    count = c[1]
                    print "'%s'\t%s\t%s\t%s\t%s" % (escape(c[0]), decCodePoint, hexCodePoint, name, count)
                else:
                    # c is a char
                    print "'%s'\t%s\t%s\t%s" % (escape(c[0]), decCodePoint, hexCodePoint, name)

    # helper: get the file path for output path
    # either from "output" or from the original input file + prefix
    def __get_name_output_file(self, input_file_path, prefix="", suffix=""):
        if ("output" in self.__args):
            return self.__args.output
        dirname, filename = os.path.split(input_file_path)
        filename = prefix + filename + suffix
        return os.path.join(dirname, filename)

    # helper: obfuscate a font
    def __obfuscate_font(self):
        def get_obfuscation_header_size(idpf_algorithm=True):
            if (idpf_algorithm):
                return [52, 20]
            else:
                return [64, 16]

        def get_obfuscation_key(key, idpf_algorithm=True):
            k = key
            if (idpf_algorithm):
                k = k.replace(u"\u0020", "")
                k = k.replace(u"\u0009", "")
                k = k.replace(u"\u000d", "")
                k = k.replace(u"\u000a", "")
                d = hashlib.sha1(k).digest()
            else:
                k = k.replace(u"urn:uuid:", "")
                k = k.replace(u"-", "")
                k = k.replace(u":", "")
                d = k.decode("hex")
            return str(d)
 
        f = open(self.__args.font, 'rb')
        fontData = bytearray(f.read())
        f.close()
        obfuscatedFontFile = self.__get_name_output_file(self.__args.font, prefix="obfuscated_")
        d = open(obfuscatedFontFile, 'wb')
        idpf_algorithm = True
        algorithm_label = "IDPF"
        if ("adobe" in self.__args):
            idpf_algorithm = False
            algorithm_label = "Adobe"
        keyData = bytearray(get_obfuscation_key(self.__args.id, idpf_algorithm))
        keySize = len(keyData)
        i = 0
        outer = 0
        outer_max, inner_max = get_obfuscation_header_size(idpf_algorithm)
        while (outer < outer_max) and (i < len(fontData)):
            inner = 0
            while (inner < inner_max) and (i < len(fontData)):
                sourceByte = fontData[i]
                keyByte = keyData[inner % keySize]
                obfuscatedByte = sourceByte ^ keyByte
                d.write(chr(obfuscatedByte))
                inner += 1
                i += 1
            outer += 1
        if (i < len(fontData) - 1):
            d.write(fontData[i:])
        d.close()
        self.__print_info("(De)obfuscated font '%s' into '%s' using id '%s' and %s algorithm." % (self.__args.font, obfuscatedFontFile, self.__args.id, algorithm_label))

    def __print_Unicode_info(self, char, short):
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
            print char + "\t" + name + " (U+" + str(hexCodepoint).upper().replace("0X", "") + ")"
        else:
            print "Name          " + name 
            print "Character     " + char 
            print "Dec Codepoint " + str(decCodepoint)
            print "Hex Codepoint " + str(hexCodepoint)
            print "Lowercase     " + lower
            print "Uppercase     " + upper
            print "Category      " + category
            print "Bidirectional " + bidirectional
            print "Mirrored      " + str(mirrored)
            print "NFC           " + nfc
            print "NFD           " + nfd
            print "============="

    # helper: perform a lookup for the given query
    def __lookup_character(self):
        results = []
        query = self.__args.character
        if ("heuristic" in self.__args):
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
        else:
            # try char, codepoint or exact name lookup
            if (len(query) == 1):
                # Unicode char
                results = [ u"" + query ]
            elif (re.match(self.PATTERN_HEX_0x, query) != None):
                # hex
                results = [ unichr(int(query[2:], 16)) ]
            elif (re.match(self.PATTERN_HEX_x, query) != None):
                # hex
                results = [ unichr(int(query[1:], 16)) ]
            elif (re.match(self.PATTERN_DEC, query) != None):
                # decimal
                results = [ unichr(int(query)) ]
            else: 
                # exact name
                results = [ unicodedata.lookup(query) ]
        return results
        
    def __create_epub(self, char_list):
        dec_codepoint_list = map(lambda x: ord(x[0]), char_list)
        font_name = ""
        ebook_name = ""
        if ("font" in self.__args):
            font_name = self.__args.font
        if ("glyphs" in self.__args):
            font_name = self.__args.glyphs
        if ("ebook" in self.__args):
            ebook_name = self.__args.ebook
        if ("plain" in self.__args):
            ebook_name = self.__args.plain
        if ("range" in self.__args):
            ebook_name = self.__args.range   
        if (len(font_name) > 0):
            epub_file_name = self.__get_name_output_file(font_name, suffix=".epub")
            font_name = os.path.split(font_name)[1]
            epub_title = "Glyphs in %s" % (font_name)
        if (len(ebook_name) > 0):
            epub_file_name = self.__get_name_output_file(ebook_name, suffix=".epub")
            ebook_name = os.path.split(ebook_name)[1]
            epub_title = "Characters in %s" % (ebook_name)
        if ((len(font_name) > 0) and (len(ebook_name) > 0)):
            epub_title = "Glyphs missing in %s to display %s" % (font_name, ebook_name)
        from genEPUB import genEPUB
        generator = genEPUB()
        generator.createEPUB(dec_codepoint_list, epub_title, epub_file_name)
        self.__print_info("Created EPUB file '%s'." % (epub_file_name))

    def __do_check(self):
        font_char_list = []
        ebook_char_list = []
        missing_char_list = []
        font_name = ""
        ebook_name = ""
        try:
            if ("font" in self.__args):
                font_name = self.__args.font
                font_char_list = self.__get_font_char_list(only_chars=True)
            if ("glyphs" in self.__args):
                font_name = self.__args.glyphs
                font_char_list = self.__get_glyphs_char_list(only_chars=True)
            if ("ebook" in self.__args):
                ebook_name = self.__args.ebook
                ebook_char_list = self.__get_ebook_char_list()
            if ("plain" in self.__args):
                ebook_name = self.__args.plain
                ebook_char_list = self.__get_plain_char_list()
            missing_char_list = filter(lambda x: (ord(x[0]) > 31) and (x[0] not in font_char_list), ebook_char_list)
        except Exception as e:
            self.__print_error(str(e))
            return CustomParser.EXIT_CODE_COMMAND_FAILED
        if (len(missing_char_list) == 0):
            self.__print_info("Font '%s' contains all the glyphs for displaying ebook '%s'." % (font_name, ebook_name))
            return CustomParser.EXIT_CODE_OK
        else:
            self.__print_info("Font '%s' misses the following glyphs for displaying ebook '%s':" % (font_name, ebook_name))
            self.__print_char_list(missing_char_list)
            if ("epub" in self.__args):
                self.__create_epub(missing_char_list)
            return CustomParser.EXIT_CODE_MISSING_GLYPHS

    def __do_convert(self):
        try:
            font = fontforge.open(self.__args.font)
            font.selection.all()
            font.generate(self.__args.output)
        except Exception as e:
            self.__print_error(str(e))
            return CustomParser.EXIT_CODE_COMMAND_FAILED
        self.__print_info("Converted font '%s' into font '%s'." % (self.__args.font, self.__args.output))
        return CustomParser.EXIT_CODE_OK

    def __do_count(self):
        total = 0
        try:
            char_list = []
            ebook_name = ""
            if ("ebook" in self.__args):
                char_list = self.__get_ebook_char_list()
                ebook_name = self.__args.ebook
            if ("plain" in self.__args):
                char_list = self.__get_plain_char_list()
                ebook_name = self.__args.plain
            count_list = map(lambda x: x[1], char_list)
            total = reduce(lambda x, y: x + y, count_list)
        except Exception as e:
            self.__print_error(str(e))
            return CustomParser.EXIT_CODE_COMMAND_FAILED
        self.__print_info("Number of characters in '%s':" % (ebook_name))
        print total
        return CustomParser.EXIT_CODE_OK

    def __do_list(self):
        char_list = []
        msg = ""
        try:
            if ("blocks" in self.__args):
                msg = "Unicode Blocks"
                self.__print_info(msg)
                self.__print_block_list()
                return CustomParser.EXIT_CODE_OK
            if ("ebook" in self.__args):
                char_list = self.__get_ebook_char_list()
                msg = "Characters in '%s':" % (self.__args.ebook)
            if ("font" in self.__args):
                char_list = self.__get_font_char_list(only_chars=True)
                msg = "Glyphs in '%s':" % (self.__args.font)
            if ("glyphs" in self.__args):
                char_list = self.__get_glyphs_char_list(only_chars=True)
                msg = "Glyphs in '%s':" % (self.__args.glyphs)
            if ("plain" in self.__args):
                char_list = self.__get_plain_char_list()
                msg = "Characters in '%s':" % (self.__args.plain)
            if ("range" in self.__args):
                char_list = self.__get_range_char_list()
                msg = "Characters in range '%s':" % (self.__args.range)
        except Exception as e:
            self.__print_error(str(e))
            return CustomParser.EXIT_CODE_COMMAND_FAILED
        self.__print_info(msg)
        self.__print_char_list(char_list)
        if ("epub" in self.__args):
            self.__create_epub(char_list)
        return CustomParser.EXIT_CODE_OK

    def __do_lookup(self):
        try:
            found = self.__lookup_character()
            if (len(found) == 0):
                self.__print_info("No match found for '%s'" % (self.__args.character))
                return CustomParser.EXIT_CODE_COMMAND_FAILED
            else:
                self.__print_info("Matches found for '%s':" % (self.__args.character))
                for c in found:
                    self.__print_Unicode_info(c, ("compact" in self.__args))
        except Exception as e:
            self.__print_error(str(e))
            return CustomParser.EXIT_CODE_COMMAND_FAILED
        return CustomParser.EXIT_CODE_OK

    def __do_obfuscate(self):
        try:
            self.__obfuscate_font()
        except Exception as e:
            self.__print_error(str(e))
            return CustomParser.EXIT_CODE_COMMAND_FAILED
        return CustomParser.EXIT_CODE_OK

    def __do_subset(self):
        font_char_list = []
        ebook_char_list = []
        found_char_list = []
        font_name = ""
        ebook_name = ""
        output_font_file = ""
        try:
            font_name = self.__args.font
            font_char_list = self.__get_font_char_list(only_chars=True)
            if ("ebook" in self.__args):
                ebook_name = self.__args.ebook
                ebook_char_list = self.__get_ebook_char_list()
            if ("plain" in self.__args):
                ebook_name = self.__args.plain
                ebook_char_list = self.__get_plain_char_list()
            font = fontforge.open(self.__args.font)
            font.selection.none()
            for c in ebook_char_list:
                if (c[0] in font_char_list):
                    font.selection.select(("more", "unicode"), ord(c[0]))
                    found_char_list.append(c[0])
            if (not ("exclude" in self.__args)):
                font.selection.invert()
            font.clear()
            output_font_file = self.__get_name_output_file(self.__args.font, prefix="subset_")
            font.generate(output_font_file)
        except Exception as e:
            self.__print_error(str(e))
            return CustomParser.EXIT_CODE_COMMAND_FAILED
        if ("exclude" in self.__args):
            self.__print_info("Subsetting font '%s' with ebook '%s' into new font '%s', not containing the following glyphs:" % (font_name, ebook_name, output_font_file))
        else:
            self.__print_info("Subsetting font '%s' with ebook '%s' into new font '%s', containing the following glyphs:" % (font_name, ebook_name, output_font_file))
        self.__print_char_list(found_char_list)
        return CustomParser.EXIT_CODE_OK

    def execute(self):
        returnCode = CustomParser.EXIT_CODE_OK
        command = self.__args.command

        if (command == CustomParser.COMMAND_CHECK):
            returnCode = self.__do_check() 

        if (command == CustomParser.COMMAND_CONVERT):
            returnCode = self.__do_convert()

        if (command == CustomParser.COMMAND_COUNT):
            returnCode = self.__do_count()

        if (command == CustomParser.COMMAND_LIST):
            returnCode = self.__do_list()

        if (command == CustomParser.COMMAND_LOOKUP):
            returnCode = self.__do_lookup()

        if (command == CustomParser.COMMAND_OBFUSCATE):
            returnCode = self.__do_obfuscate()

        if (command == CustomParser.COMMAND_SUBSET):
            returnCode = self.__do_subset()

        return returnCode



def main():
    # read command line parameters
    args = CustomParser().get_arguments()
   
    # run glyphIgo
    returnCode = GlyphIgo(args).execute()
    
    # return proper exit code
    sys.exit(returnCode)

if (__name__ == '__main__'):
    # force UTF-8 encoding
    #reload(sys)
    #sys.setdefaultencoding("utf-8")
    main()



