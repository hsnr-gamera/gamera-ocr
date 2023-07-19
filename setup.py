from pathlib import Path

from setuptools import setup

from gamera import gamera_setup

# This constant should be the name of the toolkit
TOOLKIT_NAME = "ocr"

# ----------------------------------------------------------------------------
# You should not usually have to edit anything below, but it is
# implemented here and not in the Gamera core so that you can edit it
# if you need to do something more complicated (for example, building
# and linking to a third- party library).
# ----------------------------------------------------------------------------

PLUGIN_PATH = 'gamera/toolkits/%s/plugins/' % TOOLKIT_NAME
PACKAGE = 'gamera.toolkits.%s' % TOOLKIT_NAME
PLUGIN_PACKAGE = PACKAGE + ".plugins"
plugins = gamera_setup.get_plugin_filenames(PLUGIN_PATH)
plugin_extensions = gamera_setup.generate_plugins(plugins, PLUGIN_PACKAGE)

# This is a standard setuptools setup initializer. If you need to do
# anything more complex here, refer to the Python setuptools documentation.
if __name__ == "__main__":
    setup(name="gamera-ocr",
          version="2.0.0",
          ext_modules=plugin_extensions,
          packages=[PACKAGE, PLUGIN_PACKAGE],
          include_dirs=['include/plugins'],
          python_requires='>=3.5',
          scripts=['scripts/ocr4gamera'],
          install_requires=['gamera>=4.1.0']
          )
