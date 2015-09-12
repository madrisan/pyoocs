# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

try:
    import json
except ImportError:
    import simplejson as json

from oocs.output import message

oocs_filepath = "oocs-cfg.json"

def read_config(module, filepath = oocs_filepath):
    cfgfile = open(filepath, 'r')
    try:
        data = json.load(cfgfile)
        cfgfile.close();
        return data["oocs-module"][module]
    except IOError:
        message('File ' + filepath + ' does not appear to exist.',
                level='warning')
        return {}
