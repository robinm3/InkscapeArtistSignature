#!/usr/bin/env python

# local library
import inkex
import pathmodifier
from simpletransform import *
from simplestyle import *
try:
    from subprocess import Popen, PIPE
    bsubprocess = True
except:
    bsubprocess = False

# Create effect instance and apply it.
effect = ArtistSignatureEffect()
effect.affect()

class ArtistSignatureEffect(inkex.Effect):
    """
    Inkscape artist extension effect.
    Creates artist's signature on the document.
    """
    def __init__(self):
        inkex.Effect.__init__(self)
        self.artistName = ''

        self.OptionParser.add_option('-a', '--artistName', 
                                     action = 'store', type = 'string', 
                                     dest = 'artistName', default = 'Artist Name',
                                     help = "Enter your artist name")

        self.OptionParser.add_option("-t", "--textSize",
                                     action="store", type="int",
                                     dest="textSize", default=24,
                                     help="Text size")

        self.OptionParser.add_option("-f", "--fontType",
                                     action="store", type="str",
                                     dest="fontType", default="arial",
                                     help="Give font type")

        self.OptionParser.add_option("-p", "--signaturePlace",
                                     action="store", type="string", 
                                     dest="signaturePlace", default='bottomRight',
                                     help="Where do you want your signature to appear?")

        self.OptionParser.add_option("-s", "--social",
                                     action="store", type="string", 
                                     dest="social", default="",
                                     help="Add social media?")

        self.OptionParser.add_option("-c", "--strokeColour",
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
        self.artistName = self.options.artistName
        textSize = self.options.textSize
        fontType = self.options.fontType
        fontHeight = max(10, int(self.getUnittouu(str(textSize) + 'px')))
        hexColour = self.getHexColour(self.options.strokeColour)
        signaturePlace = self.options.signaturePlace

        # Make bounding box
        scale = self.unittouu('1px')
        if self.objectIsSelected():
            self.bbox = self.getBoundingBoxDimensions(scale)

        if not self.boundingBoxIsPath():
            exit()

        # Create a new layer
        layer = self.createTextLayer('Signature layer')

        # Create text element
        self.addSocial()
        text = self.createText(fontType, fontHeight, hexColour, layer, self.artistName)

        # Set text position
        xPos, yPos = self.textPosition(signaturePlace, self.artistName, fontHeight)
        text.set('x', str(xPos))
        text.set('y', str(yPos))

        # Connect elements together
        layer.append(text)

    def addSocial(self):
        social = self.options.social
        if social == 'Facebook':
            self.artistName = social + ': @' + self.artistName
        elif social == 'Tumblr':
            self.artistName = social + ': @' + (self.artistName.replace(" ", "")).lower()
        elif social in ('Instagram', 'Twitter'):
            self.artistName = social + ': @' + self.artistName.replace(" ", "_")
        elif social == 'Reddit':
            self.artistName = social + ': u/' + self.artistName.replace(" ", "")
        elif social == 'DeviantArt':
            self.artistName = social + ': ' + self.artistName

    def createTextLayer(self, layerName):
        """
        Creates an inkscape text layer with given name
        """
        layer = inkex.etree.SubElement(self.document.getroot(), 'g')
        layer.set(inkex.addNS('label', 'inkscape'), str(layerName))
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        return layer

    def objectIsSelected(self):
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
    
    def boundingBoxIsPath(self):
        """
        Avoid ugly failure on rects and texts.
        """
        try:
            testing_the_water = self.bbox[0]
        except TypeError:
            inkex.errormsg(('Unable to process this object.  Try changing it into a path first.'))
            exit()
        return True

    def getHexColour(self, longColour):
        """ 
        Convert the long color into hex colour
        """
        longColour = long(longColour)
        if longColour < 0: 
            longColour = long(longColour) & 0xFFFFFFFF
        hexColour = hex(longColour)[2:-3]
        hexColour = '#' + hexColour.rjust(6, '0').upper()
        return hexColour

    def textPosition(self, signaturePlace, artistName, fontHeight):
        """
        Depending on signature place and width
        Return position (x, y)
        """
        if signaturePlace == "topLeft":
            xPos = (self.bbox[0]+(len(artistName)*3.5)*fontHeight/10)
            yPos = (self.bbox[2]+(15)*fontHeight/10)   
        elif signaturePlace == "topRight":
            xPos = (self.bbox[1]-(len(artistName)*3.5)*fontHeight/10)
            yPos = (self.bbox[2]+(15)*fontHeight/10)
        elif signaturePlace == "bottomLeft":
            xPos = (self.bbox[0]+(len(artistName)*3.5)*fontHeight/10)
            yPos = (self.bbox[3]-(10)*fontHeight/10)
        elif signaturePlace == "center":
            xPos = (self.bbox[0] + ((self.bbox[1]-self.bbox[0]) / 2))
            yPos = (self.bbox[2] + ((self.bbox[3]-self.bbox[2]) / 2))
        else:
            xPos = (self.bbox[1]-(len(artistName)*3.5)*fontHeight/10)
            yPos = (self.bbox[3]-(10)*fontHeight/10)
        
        return (xPos, yPos)
    
    def createText(self, fontType, fontHeight, hexColour, layer, textString):
        """
        Creates text with given options
        """
        textStyle = { 'font-size': str(fontHeight),
                       'font-family': fontType,
                       'text-anchor': 'middle',
                       'text-align': 'center',
                       'fill': hexColour }
        textAttributes = {'style':simplestyle.formatStyle(textStyle),
                     'x': str(44),
                     'y': str(-15) }
        text = inkex.etree.SubElement(layer, 'text', textAttributes)
        text.set('style', formatStyle(textStyle))
        text.text = textString
        return text

    def getUnittouu(self, param):
        " for 0.48 and 0.91 compatibility "
        try:
            return inkex.unittouu(param)
        except AttributeError:
            return self.unittouu(param)

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
