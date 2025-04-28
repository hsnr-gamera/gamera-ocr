#!/usr/bin/env python

from gamera import gendoc
import sys

if __name__ == '__main__':
   # Step 1:
   # Import all of the plugins to document.
   # Be careful not to load the core plugins, or they
   # will be documented here, too.
   # If the plugins are not already installed, we'll just ignore
   # them and generate the narrative documentation.
   try:
      from gamera.toolkits.ocr.plugins import bbox_merging_mcmillan
   except ImportError:
      print("ERROR:")
      print("This `ocr` toolkit must be installed before generating")
      print("the documentation.  For now, the system will skip generating")
      print("documentation for the plugins.")
      sys.exit(1)

   # Step 2:
   # Generate documentation for this toolkit
   # This will handle any commandline arguments if necessary
   gendoc.gendoc(classes=[("gamera.toolkits.ocr.classes",
                           "Textline",
                           "__init__ add_glyph add_glyphs sort_glyphs"),
			  ("gamera.toolkits.ocr.classes",
                           "Page",
                           "__init__ segment page_to_lines order_lines lines_to_chars chars_to_words show_lines show_glyphs show_words"),
			  ("gamera.toolkits.ocr.classes",
                           "hocrPage",
                           "__init__"),
			  ("gamera.toolkits.ocr.classes",
                           "ClassifyCCs",
                           "__init__ __call__")],
                 plugins=["PageSegmentation"],
                 sourceforge_logo=False)
