# glyphIgo

**glyphIgo** is a Swiss Army knife for dealing with fonts and EPUB eBooks

* Version: 3.0.3
* Date: 2015-06-07
* Developer: [Alberto Pettarin](http://www.albertopettarin.it/) ([contact](http://www.albertopettarin.it/contact.html))
* License: the MIT License (MIT), see LICENSE.md

There are seven main usage scenarios:

1. **check** whether a given font file contains all the glyphs needed to properly display the given EPUB or plain text file,
2. **convert** a font file from/to TTF/OTF/WOFF format,
3. **count** the number of characters in an EPUB file or a plain text UTF-8 file,
4. **list** all Unicode characters used in an EPUB file or a plain text UTF-8 file or all Unicode glyphs present in a TTF/OTF/WOFF font file,
5. **lookup** for information about a given Unicode character, including heuristic name matching,
6. (de)**obfuscate** a font, with either the IDPF or the Adobe algorithm, and
7. **subset** a given font file, that is, create a new font file containing only the subset of glyphs of a given font that are contained in a EPUB or plain text file.

Optionally, you can export a list of Unicode glyphs/characters,
produced by the above commands,
as an EPUB file for quick testing on an eReader.

## IMPORTANT NOTICE

*2016-06-30* I planned to deeply restructure glyphIgo during the 2016 summer.
In particular, to update it to use the new fontforge and fonttools libraries,
and to add better documentation. Thank you for your patience.

*2016-10-05* ... and of course I have not had time to work on glyphIgo,
since my plans for the 2016 summer went out of the window.
However, I have some more time now (October 2016),
and I would like to address the following issues:

1. use `fonttools` instead of `fontforge` as the core font library;
2. restructure the code as a library, usable in third-party code;
3. fix the command line parsing (`argcomplete` is problematic);
4. release on PyPI;
5. better documentation.

Stay tuned (and/or have a look at the `v4` branch)!

*2016-12-22* ... and of course I have not worked on glyphIgo.
I am sorry about that.
I am not sure when I will have the time for it.

## Usage

```
$ ./glyphIgo.py check|convert|count|list|lookup|obfuscate|subset [options]

optional arguments:
  -h, --help            show this help message and exit
  --version             print version and exit
  -c CHARACTER, --character CHARACTER
                        lookup CHARACTER, specified as name, partial name,
                        dec/hex codepoint, or Unicode character
  -d DECODE, --decode DECODE
                        use DECODE encoding to decode the input EBOOK or PLAIN
                        file
  -e EBOOK, --ebook EBOOK
                        ebook file, in EPUB/ZIP format
  -f FONT, --font FONT  font file, in TTF/OTF/WOFF format
  -g GLYPHS, --glyphs GLYPHS
                        font file, specified as a list of decimal Unicode
                        codepoints contained in plain text file GLYPHS, one
                        codepoint per line
  -i ID, --id ID        (de)obfuscate FONT using ID to compute the obfuscation
                        key
  -o OUTPUT, --output OUTPUT
                        create OUTPUT file
  -p PLAIN, --plain PLAIN
                        ebook file, in plain text format
  -r RANGE, --range RANGE
                        range, in '0x????-0x????' or '????-????' format
  -q, --quiet           quiet output
  -s, --sort            sort output by character count instead of character
                        codepoint
  -u, --epub            output an EPUB file containing the Unicode characters
                        in the input file(s)
  -v, --verbose         verbose output
  -w, --nohumanreadable
                        verbose output without human readable messages
  --adobe               use Adobe obfuscation algorithm
  --blocks              print range and name of Unicode blocks
  --compact             compact lookup output (Unicode character, name, and
                        codepoint only)
  --exact               use exact Unicode lookup (default)
  --exclude             exclude the characters in EBOOK or PLAIN from the
                        output
  --full                full lookup output (default)
  --heuristic           use heuristic Unicode lookup
  --idpf                use IDPF obfuscation algorithm (default)
  --preserve            preserve X(HT)ML tags instead of stripping them away

exit codes:
  0 = no error
  1 = RESERVED
  2 = invalid command line argument(s)
  4 = missing glyphs in the font file to correctly display the given ebook or file
  8 = failure while executing the requested command
```

### Examples

```
   1. Print this usage message
      $ ./glyphIgo.py -h

   2. Check whether all the characters in ebook.epub can be displayed by font.ttf
      $ ./glyphIgo.py check -f font.ttf -e ebook.epub

   3. As above, but use font_glyph_list.txt containing a list of decimal codepoints for the font glyphs
      $ ./glyphIgo.py check -g font_glyph_list.txt -e ebook.epub

   4. As above, but sort missing characters (if any) by their count (in ebook.epub) instead of by Unicode codepoint
      $ ./glyphIgo.py check -f font.ttf -e ebook.epub -s

   5. As above, but also create missing.epub containing the list of missing Unicode characters
      $ ./glyphIgo.py check -f font.ttf -e ebook.epub -u -o missing.epub

   6. Convert font.ttf (TTF) into font.otf (OTF)
      $ ./glyphIgo.py convert -f font.ttf -o font.otf

   7. Count the number of characters in ebook.epub
      $ ./glyphIgo.py count -e ebook.epub

   8. As above, but preserve tags
      $ ./glyphIgo.py count -e ebook.epub --preserve

   9. Print the list of glyphs in font.ttf
      $ ./glyphIgo.py list -f font.ttf

  10. As above, but just output the decimal codepoints
      $ ./glyphIgo.py list -f font.ttf -q

  11. Print the list of characters in ebook.epub
      $ ./glyphIgo.py list -e ebook.epub

  12. As above, but also create list.epub containing the list of Unicode characters
      $ ./glyphIgo.py list -e ebook.epub -u -o list.epub

  13. Print the list of characters in page.xhtml
      $ ./glyphIgo.py list -p page.xhtml

  14. Print the list of characters in the range 0x2200-0x22ff (Mathematical Operators)
      $ ./glyphIgo.py list -r 0x2200-0x22ff
      $ ./glyphIgo.py list -r "Mathematical Operators"

  15. Print the range and name of Unicode blocks
      $ ./glyphIgo.py list --blocks

  16. Lookup for information for Unicode character
      $ ./glyphIgo.py lookup -c 8253
      $ ./glyphIgo.py lookup -c 0x203d
      $ ./glyphIgo.py lookup -c ‽
      $ ./glyphIgo.py lookup -c "INTERROBANG"

  17. As above, but print compact output
      $ ./glyphIgo.py lookup --compact -c 8253
      $ ./glyphIgo.py lookup --compact -c 0x203d
      $ ./glyphIgo.py lookup --compact -c ‽
      $ ./glyphIgo.py lookup --compact -c "INTERROBANG"

  18. Heuristic lookup for information for Unicode characters which are Greek omega letters with oxia
      $ ./glyphIgo.py lookup --heuristic -c "GREEK OMEGA OXIA"

  19. (De)obfuscate font.otf into obf.font.otf using the given id and the IDPF algorithm
      $ ./glyphIgo.py obfuscate -f font.otf -i "urn:uuid:9a0ca9ab-9e33-4181-b2a3-e7f2ceb8e9bd" -o obf.font.otf

  20. As above, but use Adobe algorithm
      $ ./glyphIgo.py obfuscate -f font.otf -i "urn:uuid:9a0ca9ab-9e33-4181-b2a3-e7f2ceb8e9bd" -o obf.font.otf --adobe

  21. Subset font.ttf into min.font.otf by copying only the glyphs appearing in ebook.epub
      $ ./glyphIgo.py subset -f font.ttf -e ebook.epub -o min.font.otf

  22. Subset font.ttf into rem.font.ttf by removing the glyphs appearing in list.txt
      $ glyphIgo.py subset -f font.ttf -p list.txt -o rem.font.ttf --exclude
```

Please see [OUTPUT.md](OUTPUT.md) for usage examples with their actual output.


## License

**glyphIgo** is released under the MIT License since version 2.0.0 (2014-03-07).

Previous versions, hosted in a Google Code repo, were released under the GNU GPL 3 License.


## Autocompletion

**glyphIgo** uses `argcomplete` for autocompleting options/filenames.
Please refer to the [`argcomplete` documentation](https://argcomplete.readthedocs.org/en/latest/)
for directions on how to enable it.


## Technical Notes

**glyphIgo** requires Python 2.7 (or later Python 2.x), and Python module `fontforge`.

On Ubuntu/Debian, you can install the `python-fontforge` package: `apt-get install python-fontforge`.
On other OSes... I do not know, I use it on Debian only. Feel free to let me know, I will add your installation notes here.

For the sake of speed and code clarity, the given EPUB is not "fully parsed".
In particular:

* the list of Unicode characters is extracted by inspecting all files inside the ZIP archive whose lowercased name ends in `xhtml`, `html`, and `xml` (except those in `META-INF/`, which are skipped), and
* the book pages are not parsed (e.g., a Unicode character appearing inside a comment will be accounted for).

Please observe that these approximations err on the "conservative" side, possibly generating "false-positives" but never generating "false-negatives".

You can also pass a ZIP archive, containing several XHTML/HTML/XML pages, using the `-e` switch.

By default, **glyphIgo** assumes that all files are encoded in UTF-8.
You can change the encoding used while decoding plain text files
by specifying the `-d` (or `--decode`) parameter.

Conversion from entity (named or not) to Unicode codepoint is supported.

Unfortunately, there is no `python-fontforge` module for Python 3 in the stable Debian repo (as of 2014-03-07), so you must use Python 2.7 (or later Python 2.x) to run **glyphIgo**.

To use `-u` or `--epub` switch, you also need to download `genEPUB.py` and put it into the same directory of `glyphIgo.py`.


## Limitations and Missing Features

* Support for Unicode modifiers
* Full EPUB parsing
* Font obfuscation: parse the uid directly from a given EPUB
* Support for autocompleting via `argcomplete`
* Shortcuts (e.g., `"-C" == "count -e"`)


## Trivia

### What does "glyphIgo" mean?

Most people think that `glyphIgo = "glyph I go"`.

Instead, the name comes from `glyph` and `figo` (Italian slang for `cool`).

### Why did you code glyphIgo?

I needed to perform the "font checking" on nearly 100,000 EPUB files at once, for a large project. Then, I felt bad having this little piece of code sitting idly, so I decided to publish it on Google Code. In March 2014, I moved it to GitHub.

