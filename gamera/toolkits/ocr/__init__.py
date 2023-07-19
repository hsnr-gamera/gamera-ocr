"""
Toolkit setup

This file is run on importing anything within this directory.
Its purpose is only to help with the Gamera GUI shell,
and may be omitted if you are not concerned with that.
"""


from gamera import toolkit
from gamera.toolkits.ocr.plugins import *
import wx
from gamera.toolkits.ocr import ocr_toolkit

# You can inherit from toolkit.CustomMenu to create a menu
# for your toolkit.  Create a list of menu option in the
# member _items, and a series of callback functions that
# correspond to them.  The name of the callback function
# should be the same as the menu item, prefixed by '_On'
# and with all spaces converted to underscores.

#class OcrMenu(toolkit.CustomMenu):
#     _items = ["Ocr Toolkit",
#               "Ocr Toolkit 2"]
#     def _OnOcr_Toolkit(self, event):
#         wx.MessageDialog(None, "You clicked on Ocr Toolkit!").ShowModal()
#         main.main()
#     def _OnOcr_Toolkit_2(self, event):
#         wx.MessageDialog(None, "You clicked on Ocr Toolkit 2!").ShowModal()
#         main.main()
#    
#    
# ocr_menu = OcrMenu()
