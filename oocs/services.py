# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

import glob

from oocs.config import Config
from oocs.filesystem import UnixCommand, UnixFile
from oocs.output import message, message_alert, message_ok, quote

class Services(object):
    def __init__(self, verbose=False):
        self.module = 'services'
        self.verbose = verbose

        try:
           self.cfg = Config().read(self.module)
           self.enabled = (self.cfg.get('enable', 1) == 1)
        except KeyError:
            message_alert(self.module +
                          ' directive not found in the configuration file',
                          level='warning')
            self.cfg = {}

        self.required = self.cfg.get("required", [])

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)

    def configuration(self): return self.cfg
    def enabled(self): return self.enabled
    def module_name(self): return self.module
    def required(self): return self.required

    def runlevel(self):
        rl = UnixCommand('/sbin/runlevel')
        out, err, retcode = rl.execute()
        if retcode != 0: return err or 'unknown error'
        return out.split()[1]

class Service(Services):
    def __init__(self, service):
        Services.__init__(self)
        self.service = service

    def status(self):
        cmdlines = glob.glob('/proc/*/cmdline')
        for f in cmdlines:
            for srv in self.service.split('|'):
                cmdlinefile = UnixFile(f)
                if not cmdlinefile.isfile(): continue
                if srv in cmdlinefile.readfile():
                    return 'running'
        return 'down'

    def name(self):
        return self.service

    def is_running(self):
        return self.status() == 'running'

def check_services(verbose=False):
    services = Services(verbose=verbose)
    if not services.enabled:
        if verbose:
            message_alert('Skipping ' + quote(module_name()) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking services', header=True, dots=True)

    #message('runlevel: ' + services.runlevel())

    for srv in services.required:
        service = Service(srv)
        if not service.is_running():
            message_alert('the service ' + quote(service.name()) +
                          ' is not running', level='critical')
        elif services.verbose:
            message_ok('the service ' + quote(service.name()) + ' is running')
