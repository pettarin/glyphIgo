#!/usr/bin/env python

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto@albertopettarin.it)'
__copyright__   = '2012-2014 Alberto Pettarin (alberto@albertopettarin.it)'
__version__     = 'v2.0.1'
__date__        = '2014-03-08'
__description__ = 'genEPUB creates an EPUB eBook from a list of Unicode characters'

### BEGIN changelog ###
#
# 2.0.1 2014-03-08 Fixed missing newlines in generated index.xhtml
# 2.0.0 2014-03-07 Moved to GitHub, released under MIT license
# 1.02  2013-03-16 Fixed usage message, added sort
# 1.01  2013-03-15 Initial release
#
### END changelog ###

import codecs, os, shutil, sys, unicodedata, uuid, zipfile

class genEPUB:

    CONTROL_CHARATERS = dict([
            [0, "NUL '\\0'"],
            [1, "SOH (start of heading)"],
            [2, "STX (start of text)"],
            [3, "ETX (end of text)"],
            [4, "EOT (end of transmission)"],
            [5, "ENQ (enquiry)"],
            [6, "ACK (acknowledge)"],
            [7, "BEL '\\a' (bell)"],
            [8, "BS  '\\b' (backspace)"],
            [9, "HT  '\\t' (horizontal tab)"],
            [10, "LF  '\\n' (new line)"],
            [11, "VT  '\\v' (vertical tab)"],
            [12, "FF  '\\f' (form feed)"],
            [13, "CR  '\\r' (carriage ret)"],
            [14, "SO  (shift out)"],
            [15, "SI  (shift in)"],
            [16, "DLE (data link escape)"],
            [17, "DC1 (device control 1)"],
            [18, "DC2 (device control 2)"],
            [19, "DC3 (device control 3)"],
            [20, "DC4 (device control 4)"],
            [21, "NAK (negative ack.)"],
            [22, "SYN (synchronous idle)"],
            [23, "ETB (end of trans. blk)"],
            [24, "CAN (cancel)"],
            [25, "EM  (end of medium)"],
            [26, "SUB (substitute)"],
            [27, "ESC (escape)"],
            [28, "FS  (file separator)"],
            [29, "GS  (group separator)"],
            [30, "RS  (record separator)"],
            [31, "US  (unit separator)"]])

    ### BEGIN createEPUB  ###
    # createEPUB(characters, title, epubFilename)
    # creates the EPUB file epubFilename
    # from the given list of characters
    # with the given title
    def createEPUB(self, characters, title, epubFilename):

        # sort characters by codepoint
        characters = sorted(characters)

        # remove existing file
        if (os.path.exists(epubFilename)):
            os.remove(epubFilename)

        # create tmp directory
        tmpDir = "working"
        if (os.path.exists(tmpDir)):
            shutil.rmtree(tmpDir)
        os.makedirs(tmpDir)

        # create META-INF directory
        metaInfDir = os.path.join(tmpDir, "META-INF")
        os.makedirs(metaInfDir)

        # create new mimetype file
        mimetypeFile = os.path.join(tmpDir, "mimetype")
        f = open(mimetypeFile, "w")
        f.write("application/epub+zip")
        f.close()

        # container file
        contentFileRelative = "content.opf"
        contentFile = os.path.join(tmpDir, contentFileRelative)

        # create new container.xml file
        containerFile = os.path.join(metaInfDir, "container.xml")
        f = open(containerFile, "w") 
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">\n")
        f.write(" <rootfiles>\n")
        f.write("  <rootfile full-path=\"%s\" media-type=\"application/oebps-package+xml\"/>\n" % contentFileRelative)
        f.write(" </rootfiles>\n")
        f.write("</container>")
        f.close()

        # create new style.css file
        styleFile = os.path.join(tmpDir, "style.css")
        f = open(styleFile, "w")
        f.write("@charset \"UTF-8\";\n")
        f.write("body {\n")
        f.write("  margin: 10px 25px 10px 25px;\n")
        f.write("}\n")  
        f.write("h1 {\n")
        f.write("  font-size: 200%;\n")
        f.write("  text-align: left;\n")
        f.write("}\n")
        #f.write("body.index {\n")
        #f.write("  margin: 10px 50px 10px 50px;\n")
        #f.write("}\n")
        f.write("table.character {\n")
        f.write("  width: 96%;\n")
        f.write("}\n")
        f.write("th {\n")
        f.write("  font-weight: bold;\n")
        f.write("  text-align: left;\n")
        f.write("}\n")
        f.write("td {\n")
        f.write("  text-align: left;\n")
        f.write("  font-family: monospace;\n")
        f.write("  font-size: 90%;\n")
        f.write("}\n")
        f.write(".character {\n")
        f.write("  width: 96%;\n")
        f.write("}\n")
        f.write(".sym {\n")
        f.write("  width: 10%;\n")
        f.write("}\n")
        f.write(".dec {\n")
        f.write("  width: 10%;\n")
        f.write("}\n")
        f.write(".hex {\n")
        f.write("  width: 10%;\n")
        f.write("}\n")
        f.write(".nam {\n")
        f.write("  width: 70%;\n")
        f.write("}\n")
        f.close()

        # create index file
        self.outputIndexPage(characters, title, tmpDir)

        # get UUID
        identifier = str(uuid.uuid4()).lower()

        # create toc file
        self.outputToc([["index.xhtml", title]], identifier, title, tmpDir)

        # create opf file
        self.outputOpf(identifier, title, tmpDir)

        # zip epub
        self.zipEPUB(epubFilename, tmpDir)

        # delete tmp directory
        if (os.path.exists(tmpDir)):
            shutil.rmtree(tmpDir)

        return True
    ### END createEPUB ###


    ### BEGIN escape ###
    # escape(s)
    # escapes HTML sequences
    def escape(self, s):
        x = s
        x = x.replace("&", "&amp;")
        x = x.replace(">", "&gt;")
        x = x.replace("<", "&lt;")
        return x
    ### END escape ###

    ### BEGIN check_existence ###
    # check_existence(filename)
    # checks whether filename exists
    def check_existence(self, filename):
        if (filename == None):
            return False

        return os.path.isfile(filename)
    ### END check_existence ###


    ### BEGIN zipEPUB ###
    # zipEPUB(self, filename, tmpDir) 
    # zips directory into filename
    def zipEPUB(self, filename, tmpDir):
        # tmpDir = tmpDir + '/'
        fileEPUB = zipfile.ZipFile(filename, 'w')
        fileEPUB.write(os.path.join(tmpDir, 'mimetype'), 'mimetype', zipfile.ZIP_STORED)

        structure = [ "META-INF/container.xml", "content.opf", "toc.ncx", "style.css", "index.xhtml" ]
        for f in structure:
            fileEPUB.write(os.path.join(tmpDir, f), f, zipfile.ZIP_DEFLATED)

        fileEPUB.close()
    ### END zipEPUB ###


    ### BEGIN readCharactersFromFile ###
    # readCharactersFromFile(listFilename)
    # reads the decimal Unicode codepoints from listFilename,
    # assuming one codepoint per line,
    # and returns the corresponding list of integers
    def readCharactersFromFile(self, listFilename):
        f = codecs.open(listFilename, encoding='utf-8')
        toReturn = []
        for w in f.readlines():
            w = w.rstrip()
            if (len(w) > 0):
                toReturn += [ int(w) ]
        f.close()
        return toReturn
    ### END readCharactersFromFile ###


    ### BEGIN outputIndexPage ###
    # outputIndexPage(characters, title, tmpDir)
    # create the index page
    def outputIndexPage(self, characters, title, tmpDir):
        sOUT = ""
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"no\"?>\n"
        sOUT += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n"
        sOUT += "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        sOUT += " <head>\n"
        sOUT += "  <title>%s</title>\n" % (self.escape(title))
        sOUT += "  <link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\" />\n"
        sOUT += " </head>\n"
        sOUT += " <body class=\"index\">\n"
        sOUT += "  <h1>%s</h1>\n" % (self.escape(title))

        # output char table
        sOUT += "   <table class=\"character\">\n"
        sOUT += "    <tr class=\"character\">\n"
        sOUT += "     <th class=\"sym\">%s</th>\n" % ("Sym")
        sOUT += "     <th class=\"dec\">%s</th>\n" % ("Dec")
        sOUT += "     <th class=\"hex\">%s</th>\n" % ("Hex")
        sOUT += "     <th class=\"nam\">%s</th>\n" % ("Unicode name")
        sOUT += "    </tr>\n"
        for c in characters:
            sOUT += "    <tr class=\"character\">\n"
            
            # skip control characters
            if (c < 32):
                sOUT += "     <td class=\"sym\">%s</td>\n" % ("")
                sOUT += "     <td class=\"dec\">%s</td>\n" % (str(c))
                sOUT += "     <td class=\"hex\">%s</td>\n" % (str(hex(c)))
                sOUT += "     <td class=\"nam\">%s</td>\n" % (self.CONTROL_CHARATERS[c])
            else:
                sOUT += "     <td class=\"sym\">%s</td>\n" % (self.escape(unichr(c)))
                sOUT += "     <td class=\"dec\">%s</td>\n" % (str(c))
                sOUT += "     <td class=\"hex\">%s</td>\n" % (str(hex(c)))
                sOUT += "     <td class=\"nam\">%s</td>\n" % (unicodedata.name(unichr(c), "UNKNOWN NAME"))
            
            sOUT += "    </tr>\n"
        sOUT += "   </table>\n"

        sOUT += " </body>\n"
        sOUT += "</html>"

        sOUT = sOUT.encode("utf-8")

        fileOUT = open(os.path.join(tmpDir, "index.xhtml"), 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END outputIndexPage ###


    ### BEGIN createTOC ###
    # outputToc(tocReferences, identifier, tmpDir) 
    # create the toc.ncx file
    def outputToc(self, tocReferences, identifier, title, tmpDir):

        sOUT = ""
        
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
        sOUT += "<!DOCTYPE ncx PUBLIC \"-//NISO//DTD ncx 2005-1//EN\" \"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd\">\n"
        sOUT += "<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">\n"
        sOUT += " <head>\n"
        sOUT += "  <meta name=\"dtb:uid\" content=\"%s\" />\n" % (identifier)
        sOUT += "  <meta name=\"dtb:depth\" content=\"1\" />\n"
        sOUT += "  <meta name=\"dtb:totalPageCount\" content=\"0\" />\n"
        sOUT += "  <meta name=\"dtb:maxPageNumber\" content=\"0\" />\n"
        sOUT += " </head>\n"
        sOUT += " <docTitle>\n"
        sOUT += "  <text>%s</text>\n" % (self.escape(title))
        sOUT += " </docTitle>\n"
        sOUT += " <navMap>\n"

        playOrder = 0
        for f in tocReferences:
            # reference
            r = f[0]
            # title
            t = f[1]

            playOrder += 1
            sOUT += " <navPoint id=\"%s\" playOrder=\"%s\">\n" % (r, str(playOrder))
            sOUT += "  <navLabel>\n"
            sOUT += "   <text>%s</text>\n" % (self.escape(t))
            sOUT += "  </navLabel>\n"
            sOUT += "  <content src=\"%s\" />\n" % (r)
            sOUT += " </navPoint>\n"
        
        sOUT += " </navMap>\n"
        sOUT += "</ncx>"
             
        sOUT = sOUT.encode("utf-8")
        
        fileOUT = open(os.path.join(tmpDir, "toc.ncx"), 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END createTOC ###


    ### BEGIN outputOpf ###
    # outputOpf(identifier, title, tmpDir)
    # create the content.opf file
    def outputOpf(self, identifier, title, tmpDir):
        sOUT = ""
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
        sOUT += "<package xmlns=\"http://www.idpf.org/2007/opf\" version=\"2.0\" unique-identifier=\"uuid_id\">\n"
        sOUT += " <metadata xmlns:opf=\"http://www.idpf.org/2007/opf\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\">\n"
        sOUT += "  <dc:language>en</dc:language>\n"
        sOUT += "  <dc:title>%s</dc:title>\n" % (self.escape(title))
        sOUT += "  <dc:creator opf:role=\"aut\">genEPUB.py</dc:creator>\n"
        sOUT += "  <dc:date opf:event=\"creation\">2014-03-08</dc:date>\n"
        sOUT += "  <dc:identifier id=\"uuid_id\" opf:scheme=\"uuid\">%s</dc:identifier>\n" % (identifier)
        sOUT += " </metadata>\n"

        sOUT += " <manifest>\n"
        sOUT += "  <item href=\"style.css\" id=\"css\" media-type=\"text/css\" />\n"
        sOUT += "  <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />\n"
        sOUT += "  <item href=\"index.xhtml\" id=\"index.xhtml\" media-type=\"application/xhtml+xml\" />\n"
        sOUT += " </manifest>\n"
        
        sOUT += " <spine toc=\"ncx\">\n"
        sOUT += "  <itemref idref=\"index.xhtml\" />\n"
        sOUT += " </spine>\n"
        sOUT += "</package>"

        sOUT = sOUT.encode("utf-8")

        fileOUT = open(os.path.join(tmpDir, "content.opf"), 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END outputOpf ###


    ### BEGIN usage ###
    # usage()
    # print script usage
    def usage(self):
        print("")
        print("$ python genEPUB.py characters title")
        print("")
        print("Required argument:")
        print(" characters: the name of a UTF-8 plain text file containing the list of decimal Unicode codepoints, one per line")
        print(" title: string to be used as title for the EPUB")
        print("")
        print("Examples:")
        print(" $ python genEPUB.py char.lst \"My Unicode char list\"")
        print("   Create an EPUB file char.lst.epub containing the given list of decimal Unicode codepoints, entitled 'My Unicode char list'")
        print("")
    ### END usage ###


    ### BEGIN main ###
    def main(self):
        
        if (len(sys.argv) > 2):
            listFilename = sys.argv[1]
            title = sys.argv[2]

            if (self.check_existence(listFilename)):
                epubFilename = listFilename + ".epub"
                characters = self.readCharactersFromFile(listFilename)
                self.createEPUB(characters, title, epubFilename)
            else:
                self.usage()
        else:
            self.usage()
    ### END main ###


if __name__ == '__main__':
    d = genEPUB()
    d.main()

