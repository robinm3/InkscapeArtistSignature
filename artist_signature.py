#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

# We will use the inkex module with the predefined Effect base class.
try:
    from subprocess import Popen, PIPE
    bsubprocess = True
except:
    bsubprocess = False
# local library
import inkex
import pathmodifier
from simpletransform import *
# The simplestyle module provides functions for style parsing.
from simplestyle import *


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
        Defines the "--what" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # Define string option "--artname" with "-an" shortcut and default value "Artist Name"
        self.OptionParser.add_option('-a', '--artistName', 
                                     action = 'store', type = 'string', 
                                     dest = 'artistName', default = 'Artist Name',
                                     help = "Enter your artist name")

        # Define string option "--textSize" with "-t" shortcut and default value "24"
        self.OptionParser.add_option("-t", "--textSize",
                                     action="store", type="int",
                                     dest="textSize", default=24,
                                     help="Text size")

        # Define string option "--place" with "-p" shortcut and default value "bottomRight"
        self.OptionParser.add_option("-p", "--signaturePlace",
                                     action="store", type="string", 
                                     dest="signaturePlace", default='bottomRight',
                                     help="Where do you want your signature to appear?")

        # Define string option "--hexColour" with "-c" shortcut and default value ""
        self.OptionParser.add_option("-c", "--hexColour",
                                     action="store", type="string", 
                                     dest="hexColour", default='#000000',
                                     help="Give a colour in hex")

        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='title', # use a legitmate default
                                     help="Active tab.")

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts the artist's name text into SVG document.
        """
        # Get artist's name, text size, signature place.
        artistName = self.options.artistName
        textSize = self.options.textSize
        hexColour = self.options.hexColour
        signaturePlace = self.options.signaturePlace

        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()
        scale = self.unittouu('1px')

        # query inkscape about the bounding box
        if len(self.options.ids) == 0:
            inkex.errormsg(("Please select an object."))
            exit()
        else:
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
            self.bbox = (q['x'], q['x']+q['width'], q['y'], q['y']+q['height'])

        # Avoid ugly failure on rects and texts.
        try:
            testing_the_water = self.bbox[0]
        except TypeError:
            inkex.errormsg(('Unable to process this object.  Try changing it into a path first.'))
            exit()
        

        # Create a new layer.
        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'Signature layer')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

        # Create text element
        font_height = max(10, int(self.getUnittouu(str(textSize) + 'px')))
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
        text.text = artistName

        # Set text position.
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
        
        text.set('x', str(xPos))
        text.set('y', str(yPos))


        # Center text horizontally with CSS style.

        # Connect elements together.
        layer.append(text)

    def getUnittouu(self, param):
        " for 0.48 and 0.91 compatibility "
        try:
            return inkex.unittouu(param)
        except AttributeError:
            return self.unittouu(param)

# Create effect instance and apply it.
effect = ArtistSignatureEffect()
effect.affect()
