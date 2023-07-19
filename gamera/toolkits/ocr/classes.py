#
# Copyright (C) 2009-2010 Rene Baston, Christoph Dalitz
#               2014      Fabian Schmitt, Christoph Dalitz
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from gamera.core import * 
init_gamera()    
from gamera.plugins import pagesegmentation
from gamera.plugins.listutilities import median

class Textline:
#########################################################################
  """The ``Textline`` object stores information about a text line in its
following properties:

  **bbox**
    A ``Rect`` object representing the bounding box of the text line.

  **glyphs**
    A list of ``Cc`` objects, each representing a character in the line.

  **words**
    A nested list of ``Cc`` objects, where each sublist represents
    the characters of a single word.

"""
  bbox = []
  glyphs = []
  words = []
  text = ""
  
  #######################################################################
  # constructor
  #
  def __init__(self,bbox,glyphs = None):
    """Signature:

  ``init (bbox, glyphs=None)``

with

  *bbox*:
     ``Rect`` object representing position and size of the text line

  *glyphs*:
     A list of ``Cc`` objects representing the characters in the text line

"""
    self.bbox = Rect(bbox)
    if(glyphs == None):
      self.glyphs = []
    else:
      self.glyphs = glyphs
    self.text = ""

  def add_glyph(self,glyph,extend=True):
    """Adds the given *glyph* to the Textline. Signature:

  ``add_glyph (glyph, extend=True)``

When *extend* is ``True``, the text line bounding box *bbox* is
extended by the glyph's bounding box.
"""
    self.glyphs.append(glyph)
    if (extend):
      self.bbox.union(glyph)

  def add_glyphs(self,glyphs,extend=True):
    """Adds the given *glyphs* to the Textline. Signature:

  ``add_glyphs (glyphs, extend=True)``

When *extend* is ``True``, the text line bounding box *bbox* is
extended by the union of the glyphs' bounding boxes.
"""
    for glyph in glyphs:
      self.glyphs.append(glyph)
      if (extend):
        self.bbox.union(glyph)

  def sort_glyphs(self):
    """Sorts the characters in *Textline.glyphs* from left to right.
"""
    self.glyphs.sort(key=lambda x: x.ul_x)


class ClassifyCCs:
###############################################################################
  """This is a callable class that can optionally be passed to the constructor
of Page_, so that it will be called during the segmentation process.

.. _Page: gamera.toolkits.ocr.classes.Page.html

Its standard definition should generally be sufficient for using a kNN 
classifier. Should you need to write your own classification function (e.g.
one that additionally uses heuristic rules for classification), make sure
that you overwrite the `__call__`_ method with the same signature.

For fine tuning the classification, the follwoing attributes can be used:

  **knn**
    The knn classifier; this is passed in the constructor

  **parts_to_group**
    Corresponds to *max_parts_per_group* in 
    *kNNInteractive.group_list_automatic*. Default value is 3.

  **grouping_distance**
    Corresponds to the *distance* argument of the *grouping_function* in 
    *kNNInteractive.group_list_automatic*. Only CCs closer than this
    distance are considered for grouping. Default value is -1, which means
    that it will be calculated automatically as in `__call__`__.

.. __: #call    

"""

  #############################################################################
  # constructor
  #
  def __init__(self,knn):
    """Signature:

  ``__init__ (knn)``

where *knn* is a kNN classifier which has already loaded training data.
"""
    self.knn = knn
    self.grouping_distance = -1
    self.parts_to_group = 3

  def __call__(self,ccs):
    """This method will be called in `Page.segment`_. Signature:

.. _`Page.segment`: gamera.toolkits.ocr.classes.Page.html#segment

  ``__call__ (ccs)``

where *ccs* is the list of glyphs that is to be classified. See the
documentation of Gamera's classifier API how the classification result
is stored in the glpyhs.

How the classification is done is controled by the following attributes
of ``ClassifyCCs``:

- When *parts_to_group* > 1, the classification is done with Gamera's
  grouping algorithm; otherwise no grouping of broken characters is done.

- In case of grouping, the property *distance* is passed to the grouping
  function. When it is -1 (default), it is set to the median height of
  the *ccs*.

"""
    from gamera.classify import ShapedGroupingFunction, BoundingBoxGroupingFunction
    distance = self.grouping_distance
    if (self.parts_to_group > 1 and distance < 0):
      distance = int(median([c.nrows for c in ccs]))
    if (self.parts_to_group > 1):
      ccs = self.knn.group_and_update_list_automatic(ccs,grouping_function=ShapedGroupingFunction(distance),max_parts_per_group=self.parts_to_group)
      #ccs = self.knn.group_and_update_list_automatic(ccs,grouping_function=BoundingBoxGroupingFunction(distance),max_parts_per_group=self.parts_to_group)
    else:
      ccs = self.knn.classify_and_update_list_automatic(ccs)
    return ccs

class Page:
#####################################################################################
  """The ``Page`` object offers the page segmentation functionality by 
providing a ``segment`` method. See `its documentation`__ for more information
on how to overwrite specific steps of the segmentation process.

.. __: #segment

After the call of ``segment``, the segmentation results are stored in the
following attributes of ``Page``:

  **textlines**
    List of Textline_ objects representing all text lines

  **img**
    The image to which Ccs in the *textlines* refer.

.. _Textline: gamera.toolkits.ocr.classes.Textline.html

"""
  ccs_glyphs = []
  ccs_lines = []
  textlines = []
  img = None
  classify_ccs = None

  ####################################################################################
  # constructor
  #
  def __init__(self, image, glyphs=None, classify_ccs=None):
    """The only required argument in the constructor is the image that is to
be segmented. Note that the constructor does *not* do the segmentation; for
this, you must call the segment__ method.

.. __: #segment

Signature:
    
   ``init (image, glyphs=None, classify_ccs=None)``
  
with

  *image*:
     The image to be segmented.

  *glyphs*:
     An optional list of connected components representing the characters
     in the image. In general, this is not needed, but it can be useful
     for bottom up methods starting from already detected characters (e.g.
     by Gamera's classification based character grouping.

  *classify_ccs*:
     A callable class with the same interface as ClassifyCCs_.
     If given, it will be called during the segmentation process, right after
     the splitting of lines to characters.

.. _ClassifyCCs: gamera.toolkits.ocr.classes.ClassifyCCs.html

"""
    self.img = image
    self.textlines =  []

    if (classify_ccs != None):
      self.classify_ccs = classify_ccs
    else:
      self.classify_ccs = None      
    
    if (glyphs != None):
      self.ccs_glyphs = glyphs
    else:
      self.ccs_glyphs = []

  def segment(self):
    """Segments *Page.img* and stores the result in *Page.textlines*.
This method has no arguments.

It calls the following methods in the given order:

  - page_to_lines_ for splitting the page into segments representing text lines
  - order_lines_ for sorting the lines into reading order
  - lines_to_chars_ for splitting all lines into characters
  - *Page.classify_ccs* when it is set, i.e., has been passed to the
    constructor (default is that it is not set)
  - chars_to_words_ for grouping the characters to words

.. _page_to_lines: #page-to-lines
.. _order_lines: #order-lines
.. _lines_to_chars: #lines-to-chars
.. _chars_to_words: #chars-to-words

By overwriting one (or several) of the above functions, you can
replace specific steps of the segmentation process with custom
algorithms.
    """
    self.page_to_lines()
    self.order_lines()
    self.lines_to_chars()
    if(self.classify_ccs != None):
      for line in self.textlines:
        line.glyphs = self.classify_ccs(line.glyphs)
        # grouping in classification may change glyph order
        line.sort_glyphs()
    self.chars_to_words()

  def page_to_lines(self):
    """Splits the image into segments representing text lines.
This method has no arguments.

The current implementation simply calls the *bbox_merging*
plugin from the Gamera core with *Ey=0*, such that the page is not
split into paragraphs, but into lines.

The segmentation result is stored in the variable *Page.ccs_lines*,
which is a list of the data type ``Cc``, i.e., with each segment (line)
represented by a different label in the image. This is the interface
used by all page segmentation plugins in the Gamera core.

.. note::
   When you overwrite this method, make sure that write the
   segmentation result to *self.ccs_lines*. This member variable
   will then be further processed by lines_to_chars_.

.. _lines_to_chars: #lines-to-chars
"""
    self.ccs_lines = self.img.bbox_merging(Ey=0)

  def order_lines(self):
    """Sorts the segments in *Page.ccs_lines* into reading order.
This method has no arguments.

The current implementation uses the plugin *textline_reading_order*
from the Gamera core.
"""
    from gamera.plugins.pagesegmentation import textline_reading_order
    self.ccs_lines = textline_reading_order(self.ccs_lines)

  def lines_to_chars(self, lines=None):
    """Splits text lines into characters. Signature:

   ``lines_to_chars (lines=None)``

*lines* must be a list of ``Cc`` data types, each of them representing
a text line. When not given (default), *Page.ccs_lines* is used instead.
The current implementation calls *get_line_glyphs* as defined
in the module ocr_toolkit_.

.. _ocr_toolkit: functions.html

The result is stored in *Page.textlines*; the characters are stored
for each textline in *Textline.glyphs*.
"""
    from gamera.toolkits.ocr.ocr_toolkit import get_line_glyphs
    if(lines != None):
      seg_lines = lines
    else:
      seg_lines = self.ccs_lines
    self.textlines = get_line_glyphs(self.img, seg_lines)

  def chars_to_words(self, lines=None):
    """Groups the characters in each ``Textline`` from *Page.textlines*
to words and stores the result for each ``Textline`` in the property
*Textline.words*.

This method has an optional but generally useless argument for the list of
textlines. It is therefore usually called without arguments.

The current implementation calls *chars_make_words* as defined
in the module ocr_toolkit_.

.. _ocr_toolkit: functions.html
"""
    from gamera.toolkits.ocr.ocr_toolkit import chars_make_words
    if(lines != None):
      lines = lines
    else:
      lines = self.textlines
    for line in lines:
      line.words = chars_make_words(line.glyphs)

  def show_lines(self):
    """Returns an RGB image with all segmented text lines marked by hollow 
rects. Makes only sense after *page_to_lines* (or *segment*) has 
been called.
"""
    from gamera.toolkits.ocr.ocr_toolkit import show_bboxes
    return show_bboxes(self.img, self.ccs_lines)

  def show_glyphs(self):
    """Returns an RGB image with all segmented/grouped characters marked by
hollow rects. Makes only sense after *lines_to_chars* (or *segment*) has 
been called.
"""
    glyphs = []
    for line in self.textlines:
      if(len(line.glyphs) > 0):
        for glyph in line.glyphs:
          glyphs.append(glyph)
    from gamera.toolkits.ocr.ocr_toolkit import show_bboxes
    return show_bboxes(self.img, glyphs)

  def show_words(self):
    """Returns an RGB image with all grouped words marked by
hollow rects. Makes only sense after *chars_to_words* (or *segment*) has 
been called..
"""
    words = []
    for line in self.textlines:
      for word in line.words:
        words.append(word)
    final_bboxes = []
    if(len(words) > 0):
      for word in words:
        cc = word[:1]
        word_bbox = Rect(cc[0])
        for glyph in word[1:]:
          word_bbox.union(glyph)
        final_bboxes.append(word_bbox)
    from gamera.toolkits.ocr.ocr_toolkit import show_bboxes
    return show_bboxes(self.img, final_bboxes)

class hocrPage(Page):
    """A class derived from Page__ that overrides the *page_to_lines*
method. Instead of bbox_merging, *page_to_lines* reads the segmentation
information from a hOCR file for textline detection.

.. __: gamera.toolkits.ocr.classes.Page.html
"""

    #Constructor
    ###########################################################################
    def __init__(self, image, hocr_in_path,  glyphs=None, classify_ccs=None):
        """Like `Page.__init__`_, but with the additional obligatory argument
*hocr_in_path* for the name of a hOCR file from which the textline
segmentation is read. Note that the constructor does *not* do the
segmentation; for this, you must call the *segment* method.

Signature:
    
   ``init (image, hocr_in_path, glyphs=None, classify_ccs=None)``

.. _Page.__init__: gamera.toolkits.ocr.classes.Page.html#init
"""
        self.hocr_path = hocr_in_path
        self.img = image
        self.textlines =  []

        if (classify_ccs != None):
            self.classify_ccs = classify_ccs
        else:
            self.classify_ccs = None      

        if (glyphs != None):
            self.ccs_glyphs = glyphs
        else:
            self.ccs_glyphs = []

    #extract the bbox information from the file
    ###########################################################################
    def bbox_from_hocr(self, hocr_path, maxrect):
        hocr = open(hocr_path,"r")
        maxy = maxrect.nrows - 1
        maxx = maxrect.ncols - 1
        bboxes = []
        for l in hocr:
            pcl = l.split("class=",1)
            if len(pcl) > 1:
                cl = pcl[1].split("'",2)[1]
                if cl == "ocr_line":
                    bbox_t = l.split("id=")[1].split("title=")[1].split('"',2)[1]
                    val = bbox_t.split(" ")
                    ul = Point(min([int(val[1]),maxx]), min([int(val[2]), maxy]))
                    lr = Point(min([int(val[3]),maxx]), min([int(val[4].rstrip(';')),maxy]))
                    bboxes.append(Rect(ul,lr))
        return bboxes

    #create the textline ccs with the bbox information
    ###########################################################################
    def page_to_lines(self):
        bboxes = self.bbox_from_hocr(self.hocr_path, self.img)
        self.ccs_lines = []
        for bbox in bboxes:
            self.ccs_lines.append(Cc(self.img, 1, bbox))
