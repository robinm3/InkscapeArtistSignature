#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *

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
        self.OptionParser.add_option('-an', '--artname', 
                                     action = 'store', type = 'string', 
                                     dest = 'artistName', default = 'Artist Name',
                                     help = "Enter your artist name")

        # Define string option "--place" with "-p" shortcut and default value "bottomRight"
        self.OptionParser.add_option("-p", "--place",
                                     action="store", type="string", 
                                     dest="signaturePlace", default='bottomRight',
                                     help="Where do you want your signature to appear?")

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts the artist's name text into SVG document.
        """
        # Get artist's name and signature place.
        artistName = self.options.artistName
        signaturePlace = self.options.signaturePlace

        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()

        # Get width and height:
        width  = self.unittouu(svg.get('width'))
        height = self.unittouu(svg.attrib['height'])

        # Create a new layer.
        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), f'{artistName} signature layer')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

        # Create text element
        text = inkex.etree.Element(inkex.addNS('text','svg'))
        text.text = artistName

        # Set text position.
        if signaturePlace == "topLeft":
            xPos = (width - width / 10)
            yPos = (height - height / 10)   
        elif signaturePlace == "topRight":
            xPos = (width - width / 10)
            yPos = (height - height / 10)
        elif signaturePlace == "BottomLeft":
            xPos = (width / 10)
            yPos = (height / 10)
        elif signaturePlace == "Center":
            xPos = (width / 2)
            yPos = (height / 2)
        else:
            xPos = (width - width/10)
            yPos = (height/10)
        
        text.set('x', str(xPos))
        text.set('y', str(yPos))

        # Center text horizontally with CSS style.
        style = {'text-align' : 'center', 'text-anchor': 'middle'}
        text.set('style', formatStyle(style))

        # Connect elements together.
        layer.append(text)

# Create effect instance and apply it.
effect = ArtistSignatureEffect()
effect.affect()
