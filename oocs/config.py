# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from os import path
try:
    import json
except ImportError:
    import simplejson as json

from oocs.output import die, message

class Config(object):
    def __init__(self):
        self.configfile = 'oocs-cfg.json'
        if not path.isfile(self.configfile):
            die(1, "Configuration file not found: " + self.configfile)

    def read(self, module):
        cfgfile = open(self.configfile, 'r')
        try:
            data = json.load(cfgfile)
            cfgfile.close();
        except IOError:
            die(1, 'I/O error while opening ' + self.configfile)
        except ValueError:
            die(1, 'Invalid json file: ' + self.configfile)

        return data.get("oocs-module", {}).get(module, {})
