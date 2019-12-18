#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.
from simplestyle import *

class ArtistSignature(inkex.Effect):
    """
    Inkscape artist extension.
    Creates signature on the document.
    """
    def __init__(self):
        """
        Constructor.
        Defines the "--what" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        # Define string option "--what" with "-w" shortcut and default value "World".
        self.OptionParser.add_option('-an', '--artname', 
                                     action = 'store', type = 'string', 
                                     dest = 'artist_name', default = 'Artist Name',
                                     help = "Enter your artist name")

        self.OptionParser.add_option("-p", "--place",
                                     action="store", type="string", 
                                     dest="signature_place", default='choice1',
                                     help="Where do you want your signature to appear?")

    def effect(self):
        """
        Effect behaviour.
        Overrides base class' method and inserts the artist's name text into SVG document.
        """
        # Get script's "--what" option value.
        what = self.options.what

        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()
        # or alternatively
        # svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]

        # Again, there are two ways to get the attibutes:
        width  = self.unittouu(svg.get('width'))
        height = self.unittouu(svg.attrib['height'])

        # Create a new layer.
        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'Hello %s Layer' % (what))
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

        # Create text element
        text = inkex.etree.Element(inkex.addNS('text','svg'))
        text.text = 'Hello %s!' % (what)

        # Set text position to center of document.
        text.set('x', str(width / 2))
        text.set('y', str(height / 2))

        # Center text horizontally with CSS style.
        style = {'text-align' : 'center', 'text-anchor': 'middle'}
        text.set('style', formatStyle(style))

        # Connect elements together.
        layer.append(text)

# Create effect instance and apply it.
effect = HelloWorldEffect()
effect.affect()
