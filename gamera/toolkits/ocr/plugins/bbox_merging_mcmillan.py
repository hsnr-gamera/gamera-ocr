#
# Copyright (C) 2010      Robert Butz
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

from gamera.plugin import *
from gamera.args import NoneDefault


class bbox_mcmillan(PluginFunction):
# overwrite find_tall_glyphs to adjust deviation

    
    """Returns the textlines in an image as connected components.
The segmentation method is adapted from McMillan's segmentation method
in roman_text.py. It allows a more individual segmentation through
parameterization.
    
Options:

    *glyphs*:
      This list can be build out of a ``cc_analysis``. On default, this
      parameter is blank, which will cause the function to call
      ``cc_analysis`` itself.
      
    *section_search_size*
      This optional parameter adjusts the calculated avg_glyph_size by
      multipling its value (default=1).
      
    *noise_mltplk*
      With this optional parameter one can adjust the noise_recognition
      rate independently from the calculated avg_glyph_size (default = 1).
      Values greater than 1 let the noise_removal detect bigger noise
      (but maybe even glyphs). Chose smaller values to avoid assigning
      small glyphs to noise.
      
    *large_mltplk*
      Analog to noise_mltplk one can set this parameter to manipulate the
      recognition of very large ccs according to the avg_glyph_size
      (default=20). Higher values lead to a better acceptance of
      above-average ccs. Beneficial, for example for big capital
      initials at the beginning of paragraphs such as seen in bibles.
      
    *stdev_mltplk*
      This parameter affects the line finding algorithm by excluding
      abnormally tall glyphs (default=5). The standard deviation will
      be calculated and multiplied by this parameter. 
 """
    pure_python = True
    category="PageSegmentation"
    self_type = ImageType([ONEBIT])
    args = Args([ImageList("glyphs", default=NoneDefault),
                 Float("section_search_size", default=1.0),
                 Float("noise_mltplk", default=1.0),
                 Float("large_mltplk", default=20.0),
                 Float("stdev_mltplk", default=5.0)])
    return_type = ImageList("line_cc_list")
    author = "Robert Butz, Karl MacMillan"

    def __call__(self, glyphs=None, section_search_size=1, noise_mltplk=1, large_mltplk=20, stdev_mltplk=5):
        from gamera import core
        from gamera.roman_text import Section as Roman_Section
        #from gamera.plugins.image_utilities import union_images
        
        def find_sections(image, glyphs, section_search_size=1, noise_mltplk=1, large_mltplk=20, stdev_mltplk=5):
            """Find the sections within an image - this finds large blocks
            of text making it possible to find the lines within complex
            text layouts."""
            
            FUDGE = __avg_glyph_size(glyphs) * section_search_size
            
            # remove noise and large objects
            noise_size = FUDGE * noise_mltplk
            large_size = FUDGE * large_mltplk
            new_glyphs = []
            for g in glyphs:
                if __section_size_test(image, g, noise_size, large_size):
                    new_glyphs.append(g)
                
            
            # Sort the glyphs left-to-right and top-to-bottom
            new_glyphs.sort(lambda x, y: cmp(x.ul_x, y.ul_x))
            new_glyphs.sort(lambda x, y: cmp(x.ul_y, y.ul_y))
            
            # Create rectangles for each glyph that are bigger by FUDGE
            big_rects = []
            for g in new_glyphs:
                ul_y = max(0, g.ul_y - FUDGE)
                ul_x = max(0, g.ul_x - FUDGE)
                lr_y = min(image.lr_y, g.lr_y + FUDGE)
                lr_x = min(image.lr_x, g.lr_x + FUDGE)
                ul_x = int(ul_x); ul_y = int(ul_y)
                nrows = int(lr_y - ul_y + 1)
                ncols = int(lr_x - ul_x + 1)
                big_rects.append(core.Rect(core.Point(ul_x, ul_y), core.Dim(ncols, nrows)))
            
            # Search for intersecting glyphs and merge them. This is
            # harder than it seems at first because we want everything
            # to merge together that intersects regardless of the order
            # in the list. It ends up being similar to connected-component
            # labeling. This is prone to be kind-of slow.
            current = 0
            rects = big_rects
            while(1):
                # Find the indexes of any rects that interesect with current
                inter = __find_intersecting_rects(rects, current)
                # If we found intersecting rectangles merge them with them current
                # rect, remove them from the list, and start the whole process
                # over. We start over to make certain that everything that should
                # be merged is.
                if len(inter):
                    g = rects[current]
                    new_rects = [g]
                    for i in range(len(rects)):
                        if i == current:
                            continue
                        if i in inter:
                            g.union(rects[i])
                        else:
                            new_rects.append(rects[i])
                    rects = new_rects
                    current = 0
                # If we didn't find anything that intersected move on to the next
                # rectangle.
                else:
                    current += 1
                # Bail when we are done.
                if current >= len(rects):
                    break
            
            # Create the sections
            sections = []
            for rect in rects:
                sections.append(Section(rect, stdev_mltplk))
            
            # Place the original (small) glyphs into the sections
            for g in glyphs:
                if __section_size_test(image, g, noise_size, large_size):
                    for s in sections:
                        if s.bbox.intersects(g):
                            s.add_glyph(g)
                            break
            
            # Fix up the bounding boxes
            for s in sections:
                s.calculate_bbox()
            
            return sections
        
        def __avg_glyph_size(glyphs):
            """Compute the average glyph size for the page"""
            total = 0.0
            for g in glyphs:
                total += g.nrows
                total += g.ncols
            return total / (2 * len(glyphs))
    
        def __section_size_test(image, glyph, noise_size, large_size):
            """Filter for section finding - removes very small and
            very large glyphs"""
            black_area = glyph.black_area()[0]
            if black_area > noise_size and \
                    glyph.nrows < large_size and \
                    glyph.ncols < large_size:
                return 1
            else:
                return 0
        
        def __find_intersecting_rects(glyphs, index):
            """For section finding - return the index of glyphs intersecting
            the glyph and the index passed in."""
            g = glyphs[index]
            inter = []
            for i in range(len(glyphs)):
                if i == index:
                    continue
                if g.intersects(glyphs[i]):
                    inter.append(i)
            return inter 

        # overwrite find_tall_glyphs to adjust deviation
        class Section(Roman_Section):
            def __init__(self, bbox, stdev_mltplk=5):
                self.bbox = core.Rect(bbox)
                self.lines = []
                self.glyphs = []
                # stats
                self.avg_glyph_area = 0
                self.avg_glyph_height = 0
                self.avg_glyph_width = 0
                self.avg_line_height = 0
                self.agv_line_width = 0
                self.stdev = 0
                self.stdev_mltplk = stdev_mltplk
                
                
            def find_tall_glyphs(self):
                from gamera import stats
                if self.stdev == 0:
                    self.stdev = stats.samplestdev([g.nrows for g in self.glyphs])
                
                tall = []
                for i in range(len(self.glyphs)):
                    g = self.glyphs[i]
                    if (g.nrows - self.avg_glyph_height) > self.stdev*self.stdev_mltplk:
                        tall.append(i)
                return tall
            
        
        # this is the actual beginning of the __call__-method
        if glyphs == None:
            glyphs = self.cc_analysis()
    
        sections = find_sections(self, glyphs, section_search_size, noise_mltplk, large_mltplk, stdev_mltplk)
    
        for s in sections:
            s.find_lines()

        # create a Cc for each line
        lines = []
        label = 1
        for s in sections:
            for l in s.lines:
                if len(l.glyphs) == 0:
                    continue
                # label the lines in input image
                label += 1
                for g in l.glyphs:
                    self.highlight(g, label)
                line_rect = l.glyphs[0].union_rects(l.glyphs)
                lines.append(core.Cc(self, label, line_rect))
                
        return lines

    __call__ = staticmethod(__call__)
    
   
class BboxModule(PluginModule):
    category = "OCR"
    functions = [bbox_mcmillan]
    author = "Robert Butz, Karl MacMillan"
    url = "http://gamera.sourceforge.net/"

module = BboxModule()

