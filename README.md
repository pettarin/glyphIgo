# glyphIgo

**glyphIgo** is a Swiss Army knife for dealing with fonts and EPUB eBooks

* Version: 2.0.3
* Date: 2014-07-29
* Developer: [Alberto Pettarin](http://www.albertopettarin.it/) ([contact](http://www.albertopettarin.it/contact.html))
* License: the MIT License (MIT), see LICENSE.md

There are nine main usage scenarios:

1. list all Unicode characters used in an EPUB file or a plain text UTF-8 file,
2. list all Unicode glyphs present in a TTF/OTF/WOFF font file,
3. check whether a given font file contains all the glyphs needed to properly display the given EPUB or plain text file,
4. minimize (subset) a given font file, that is, create a new font file containing only the subset of glyphs of a given font that are contained in a EPUB or plain text file,
5. convert a font file from/to TTF/OTF/WOFF format,
6. export one of the above lists of Unicode characters as an EPUB file, for quick testing on an eReader,
7. lookup for information about a given Unicode character, including fuzzy name matching,
8. count the number of characters in an EPUB file or a plain text UTF-8 file, and
9. (de)obfuscate a font, with either the IDPF or the Adobe algorithm.

### Important updates

* 2014-07-30 I plan to **heavily refactor** the code (it is really needed!), and release the result as **v2.1.0**. That version will use `argparse` instead of `getopt`, and _might_ change some of the switch/parameters names.


## Usage

```
$ python glyphIgo.py [ARGUMENTS]

Arguments:
 -h, --help            : print this usage message and exit
 -f, --font <font>     : font file, in TTF/OTF/WOFF format
 -g, --glyphs <list>   : use this list of glyphs instead of opening a font file
 -e, --ebook <ebook>   : ebook in EPUB format
 -p, --plain <ebook>   : ebook file, in plain text UTF-8 format
 -m, --minimize        : retain only the glyphs of <font> that appear in <ebook>
 -k, --key <uid>       : (de)obfuscate <font> using <uid> to compute the obfuscation key
 --adobe               : use Adobe obfuscation algorithm
 --idpf                : use IDPF obfuscation algorithm (default)
 -o, --output <name>   : use <name> for the font to be created
 --preserve            : preserve X(HT)ML tags instead of stripping them away
 -s, --sort            : sort output by character count instead of character codepoint
 -q, --quiet           : quiet output
 -v, --verbose         : verbose output of Unicode codepoints
 -u, --epub            : output an EPUB file containing the Unicode characters in the input file(s)
 -l, --lookup <char>   : lookup Unicode information for character <char>, given as Unicode char or dec/hex code or exact name
 -d, --discover <char> : same as -l, but only print the Unicode char and name
 -L, --Lookup <name>   : lookup Unicode information for character <name>, with fuzzy name lookup (WARNING: very slow!)
 -D, --Discover <name> : same as -L, but only print the Unicode char and name
 -c, --count           : count the number of characters in the text of <ebook> (specified with -e or -p)

Exit codes:

 0 = no error / no missing glyphs in the font file
 1 = invalid argument(s) error
 2 = missing glyphs in the font file to correctly display the given file/ebook
 4 = minimization/conversion failed
 8 = lookup failed
```

### Examples

```
  1. Print this usage message
     $ python glyphIgo.py -h

  2. Print the list of glyphs in font.ttf
     $ python glyphIgo.py -f font.ttf

  3. Print the list of characters in ebook.epub
     $ python glyphIgo.py -e ebook.epub

  4. Print the list of characters in page.xhtml
     $ python glyphIgo.py -p page.xhtml

  5. Check whether all the characters in ebook.epub can be displayed by font.ttf
     $ python glyphIgo.py -f font.ttf -e ebook.epub

  6. As above, but use font_glyph_list.txt containing a list of decimal codepoints for the font glyphs
     $ python glyphIgo.py -g font_glyph_list.txt -e ebook.epub

  7. As in Example 5, but sort missing characters (if any) by their count (in ebook.epub) instead of by Unicode codepoint
     $ python glyphIgo.py -f font.ttf -e ebook.epub -s

  8. Create min.font.otf containing only the glyphs of font.ttf that also appear in ebook.epub
     $ python glyphIgo.py -m -f font.ttf -e ebook.epub -o min.font.otf

  9. Convert font.ttf (TTF) into font.otf (OTF)
     $ python glyphIgo.py -f font.ttf -o font.otf

 10. As in Example 3, but also create ebook.epub.epub containing the list of Unicode characters
     $ python glyphIgo.py -e ebook.epub -u

 11. As in Example 5, but also create missing.epub containing the list of missing Unicode characters
     $ python glyphIgo.py -f font.ttf -e ebook.epub -u

 12. Lookup for information for Unicode character
     $ python glyphIgo.py -l d8253
     $ python glyphIgo.py -l x203d
     $ python glyphIgo.py -l ‽
     $ python glyphIgo.py -l "INTERROBANG"

 13. Count the number of characters in ebook.epub
     $ python glyphIgo.py -c -e ebook.epub

 14. Fuzzy lookup for information for Unicode characters which are Greek omega letters with oxia
     $ python glyphIgo.py -L "GREEK OMEGA OXIA"

 15. (De)obfuscate font.otf using the given key and the IDPF algorithm
     $ python glyphIgo.py -f font.otf -k "urn:uuid:9a0ca9ab-9e33-4181-b2a3-e7f2ceb8e9bd"
```

Please see [OUTPUT.md](OUTPUT.md) for usage examples with their actual output.


## License

**glyphIgo** is released under the MIT License since version 2.0.0 (2014-03-07).

Previous versions, hosted in a Google Code repo, were released under the GNU GPL 3 License.


## Technical Notes

**glyphIgo** requires Python 2.7 (or later Python 2.x), and Python modules:

* `python-fontforge`,
* `python-htmlentitydefs`, and
* `python-unicodedata`.

For the sake of speed and code clarity, the given EPUB is not "fully parsed".
In particular:

* the list of Unicode characters is extracted by inspecting all files inside the ZIP archive whose lowercased name ends in `xhtml`, `html`, and `xml` (except those in `META-INF/`, which are skipped), and
* the book pages are not parsed (e.g., a Unicode character appearing inside a comment will be accounted for).

Please observe that these approximations err on the "conservative" side, possibly generating "false-positives" but never generating "false-negatives".

You can also pass a ZIP archive, containing several XHTML/HTML/XML pages, using the `-e` switch.

**glyphIgo** assumes that all files are encoded in UTF-8.

Conversion from entity (named or not) to Unicode codepoint is supported.

Unfortunately, there is no `python-fontforge` module for Python 3 in the stable Debian repo (as of 2014-03-07), so you must use Python 2.7 (or later Python 2.x) to run **glyphIgo**. In the source code I have already commented the places where changes will be required to port **glyphIgo** to Python 3.

To use `-u` or `--epub` switch, you also need to download `genEPUB.py` and put it into the same directory of `glyphIgo.py`.


## Limitations and Missing Features 

* Let the user specify the source file encoding
* Support for Unicode modifiers
* Full EPUB parsing
* Font obfuscation: parse the uid directly from a given EPUB


## Trivia

### What does "glyphIgo" mean?

Most people think that `glyphIgo = "glyph I go"`.

Instead, the name comes from `glyph` and `figo` (Italian slang for `cool`).

### Why did you code glyphIgo?

I needed to perform the "font checking" on nearly 100,000 EPUB files at once, for a large project. Then, I felt bad having this little piece of code sitting idly, so I decided to publish it on Google Code. In March 2014, I moved it to GitHub.

[![Analytics](https://ga-beacon.appspot.com/UA-52776738-1/glyphIgo)](http://www.albertopettarin.it)
