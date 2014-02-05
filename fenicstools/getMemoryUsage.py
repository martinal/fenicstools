__author__ = "Mikael Mortensen <mikaem@math.uio.no>"
__date__ = "2014-01-08"
__copyright__ = "Copyright (C) 2014 " + __author__
__license__  = "GNU Lesser GPL version 3 or any later version"

import os, inspect
from dolfin import compile_extension_module

def compile_module():
    fem_folder = os.path.abspath(os.path.join(inspect.getfile(inspect.currentframe()), "../fem"))
    memory_code = open(os.path.join(fem_folder, 'getMemoryUsage.cpp'), 'r').read()
    return compile_extension_module(code=memory_code)

# Execute compilation on import
compiled_module = compile_module()

def getMemoryUsage(rss=True):
    return compiled_module.getMemoryUsage(rss)

