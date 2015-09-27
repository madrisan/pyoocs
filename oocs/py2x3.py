# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

import sys

try:
    import json
except ImportError:
    import simplejson as json

def python_major():
    '''Return the major version # of the python interpreter we're running on'''
    return sys.version_info[0]

if sys.version_info < (2, 5):
    from sre import Scanner as Scanner
else:
    from re import Scanner as Scanner

if python_major() == 2:
    str_types = basestring
elif python_major() == 3:
    # In Python3 there is no longer a 'basestring' data type
    str_types = str
else:
    sys.stderr.write('%s: Python < 2 or > 3 not (yet) supported\n' % sys.argv[0])
    sys.exit(1)
    
def isbasestring(obj):
    return isinstance(obj, str_types)
