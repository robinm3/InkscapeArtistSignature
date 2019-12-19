#!/usr/bin/env python

# local library
import inkex
import pathmodifier
from simpletransform import *
from simplestyle import *

# We will use the inkex module with the predefined Effect base class.
try:
    from subprocess import Popen, PIPE
    bsubprocess = True
except:
    bsubprocess = False


def points_to_bbox(p):
    """ 
    from a list of points (x,y pairs)
    return the lower-left xy and upper-right xy
    """
    llx = urx = p[0][0]
    lly = ury = p[0][1]
    for x in p[1:]:
        if   x[0] < llx: llx = x[0]
        elif x[0] > urx: urx = x[0]
        if   x[1] < lly: lly = x[1]
        elif x[1] > ury: ury = x[1]
    return (llx, lly, urx, ury)


class ArtistSignatureEffect(inkex.Effect):
    """
    Inkscape artist extension.
    Creates artist's signature on the document.
    """
    def __init__(self):
        """
        Constructor.
        Defines the options of the script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        self.OptionParser.add_option('-a', '--artistName', 
                                     action = 'store', type = 'string', 
                                     dest = 'artistName', default = 'Artist Name',
                                     help = "Enter your artist name")

        self.OptionParser.add_option("-t", "--textSize",
                                     action="store", type="int",
                                     dest="textSize", default=24,
                                     help="Text size")

        self.OptionParser.add_option("-p", "--signaturePlace",
                                     action="store", type="string", 
                                     dest="signaturePlace", default='bottomRight',
                                     help="Where do you want your signature to appear?")

        self.OptionParser.add_option("-s", "--strokeColour",
                                     action="store", type="string", 
                                     dest="strokeColour", default=000,
                                     help="Give colour in RGBA")

        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='title',
                                     help="Active tab.")

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts the artist's name text into SVG document.
        """
        # Get artist's name, text size, hex Colour, signature place.
        artistName = self.options.artistName
        textSize = self.options.textSize
        hexColour = self.getColorString(self.options.strokeColour)
        signaturePlace = self.options.signaturePlace

        # Get access to main SVG document element and get its dimensions.
        scale = self.unittouu('1px')

        #bounding box
        if self.objectSelected():
            self.bbox = self.getBoundingBoxDimensions(scale)

        if not self.boundingBoxIsPath:
            exit()

        # Create a new layer.
        layer = self.createLayer('Signature layer')

        # Create text element
        font_height = max(10, int(self.getUnittouu(str(textSize) + 'px')))
        text = self.createText(font_height, hexColour, layer, artistName)

        # Set text position.
        xPos, yPos = self.textPosition(signaturePlace, artistName, font_height)
        text.set('x', str(xPos))
        text.set('y', str(yPos))

        # Connect elements together.
        layer.append(text)
    
    def createLayer(self, layerName):
        """
        Creates an inkscape layer with given name
        """
        layer = inkex.etree.SubElement(self.document.getroot(), 'g')
        layer.set(inkex.addNS('label', 'inkscape'), str(layerName))
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        return layer

    def objectSelected(self):
        """
        Makes sure an object has been selected
        """
        if len(self.options.ids) == 0:
            inkex.errormsg(("Please select an object."))
            exit()
        return True
    
    def getBoundingBoxDimensions(self, scale):
        """
        Query inkscape about the bounding box
        """
        q = {'x':0,'y':0,'width':0,'height':0}
        file = self.args[-1]
        id = self.options.ids[0]
        for query in q.keys():
            if bsubprocess:
                p = Popen('inkscape --query-%s --query-id=%s "%s"' % (query,id,file), shell=True, stdout=PIPE, stderr=PIPE)
                rc = p.wait()
                q[query] = scale*float(p.stdout.read())
                err = p.stderr.read()
            else:
                f,err = os.popen3('inkscape --query-%s --query-id=%s "%s"' % (query,id,file))[1:]
                q[query] = scale*float(f.read())
                f.close()
                err.close()
        bbox = (q['x'], q['x']+q['width'], q['y'], q['y']+q['height'])

        return bbox
    
    def boundingBoxIsPath(self, bbox):
        """
        Avoid ugly failure on rects and texts.
        """
        try:
            testing_the_water = bbox[0]
        except TypeError:
            inkex.errormsg(('Unable to process this object.  Try changing it into a path first.'))
            exit()
        return True

    def getColorString(self, longColor, verbose=False):
        """ 
        Convert the long into a #RRGGBB color value
        - verbose=true pops up value for us in defaults
        conversion back is A + B*256^1 + G*256^2 + R*256^3
        """
        if verbose: inkex.debug("%s ="%(longColor))
        longColor = long(longColor)
        if longColor <0: longColor = long(longColor) & 0xFFFFFFFF
        hexColor = hex(longColor)[2:-3]
        hexColor = '#' + hexColor.rjust(6, '0').upper()
        if verbose: inkex.debug("  %s for color default value"%(hexColor))
        return hexColor

    def textPosition(self, signaturePlace, artistName, font_height):
        """
        Depending on signature place and width
        Return position (x, y)
        """
        if signaturePlace == "topLeft":
            xPos = (self.bbox[0]+(len(artistName)*3.5)*font_height/10)
            yPos = (self.bbox[2]+(15)*font_height/10)   
        elif signaturePlace == "topRight":
            xPos = (self.bbox[1]-(len(artistName)*3.5)*font_height/10)
            yPos = (self.bbox[2]+(15)*font_height/10)
        elif signaturePlace == "bottomLeft":
            xPos = (self.bbox[0]+(len(artistName)*3.5)*font_height/10)
            yPos = (self.bbox[3]-(10)*font_height/10)
        elif signaturePlace == "center":
            xPos = (self.bbox[0] + ((self.bbox[1]-self.bbox[0]) / 2))
            yPos = (self.bbox[2] + ((self.bbox[3]-self.bbox[2]) / 2))
        else:
            xPos = (self.bbox[1]-(len(artistName)*3.5)*font_height/10)
            yPos = (self.bbox[3]-(10)*font_height/10)
        
        return (xPos, yPos)
    
    def createText(self, font_height, hexColour, layer, textString):
        """
        Creates text with given options
        """
        text_style = { 'font-size': str(font_height),
                       'font-family': 'arial',
                       'text-anchor': 'middle',
                       'text-align': 'center',
                       'fill': hexColour }
        text_atts = {'style':simplestyle.formatStyle(text_style),
                     'x': str(44),
                     'y': str(-15) }
        text = inkex.etree.SubElement(layer, 'text', text_atts)
        text.set('style', formatStyle(text_style))
        text.text = textString
        return text
    
    def embedImage(self, node):
        xlink = node.get(inkex.addNS('href','xlink'))
        if xlink is None or xlink[:5] != 'data:':
            absref=node.get(inkex.addNS('absref','sodipodi'))
            url=urlparse.urlparse(xlink)
            href=urllib.url2pathname(url.path)
            
            path=''
            #path selection strategy:
            # 1. href if absolute
            # 2. realpath-ified href
            # 3. absref, only if the above does not point to a file
            if (href != None):
                path=os.path.realpath(href)
            if (not os.path.isfile(path)):
                if (absref != None):
                    path=absref

            try:
                path=unicode(path, "utf-8")
            except TypeError:
                path=path
                
            if (not os.path.isfile(path)):
                inkex.errormsg(_('No xlink:href or sodipodi:absref attributes found, or they do not point to an existing file! Unable to embed image.'))
                if path:
                    inkex.errormsg(_("Sorry we could not locate %s") % str(path))

            if (os.path.isfile(path)):
                file = open(path,"rb").read()
                embed=True
                if (file[:4]=='\x89PNG'):
                    type='image/png'
                elif (file[:2]=='\xff\xd8'):
                    type='image/jpeg'
                elif (file[:2]=='BM'):
                    type='image/bmp'
                elif (file[:6]=='GIF87a' or file[:6]=='GIF89a'):
                    type='image/gif'
                elif (file[:4]=='MM\x00\x2a' or file[:4]=='II\x2a\x00'):
                    type='image/tiff'
                #ico files lack any magic... therefore we check the filename instead
                elif(path.endswith('.ico')):
                    type='image/x-icon' #official IANA registered MIME is 'image/vnd.microsoft.icon' tho
                else:
                    embed=False
                if (embed):
                    node.set(inkex.addNS('href','xlink'), 'data:%s;base64,%s' % (type, base64.encodestring(file)))
                    if (absref != None):
                        del node.attrib[inkex.addNS('absref',u'sodipodi')]
                else:
                    inkex.errormsg(_("%s is not of type image/png, image/jpeg, image/bmp, image/gif, image/tiff, or image/x-icon") % path)

    def getUnittouu(self, param):
        " for 0.48 and 0.91 compatibility "
        try:
            return inkex.unittouu(param)
        except AttributeError:
            return self.unittouu(param)

# Create effect instance and apply it.
effect = ArtistSignatureEffect()
effect.affect()
