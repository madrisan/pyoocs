# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

import glob
from os import sep
from os.path import join

from oocs.config import Config
from oocs.filesystem import Filesystem, UnixCommand, UnixFile
from oocs.output import message, message_alert, message_ok, quote, unlist

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
        """Note: service can be a chain of commands as in the following
                 example: 'syslogd|/sbin/rsyslogd'"""
        Services.__init__(self)
        self.service = service
        self.proc_filesystem = Filesystem().procfilesystem

    def status(self):
        """Return a touple (status, pids) containing the status of the
           process(es) (can be 'running' or 'down') and the list of the pid
           numbers (or an empty one when the status is 'down').
           If 'service' is a chain of commands, the global status of the given
           processes will be considered.  This mean that the final status will
           be set to 'running' if at least one of the processes will be found,
           and the list of all the pid numbers will be reported."""
        cmdlines = glob.glob(join(self.proc_filesystem, '*', 'cmdline'))
        srv_pids = []
        srv_status = 'down'
        for f in cmdlines:
            for srv in self.service.split('|'):
                cmdlinefile = UnixFile(f)
                if not cmdlinefile.isfile(): continue
                if srv in cmdlinefile.readfile():
                    srv_pids.append(int(f.split(sep)[2]))
                    srv_status = 'running'
        return (srv_status, srv_pids)

    def name(self):
        return self.service

    def pid(self):
        """Return the list of pid numbers or an empty list when the process
           is not running"""
        return self.status()[1]

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
        pid = service.pid()
        if pid and services.verbose:
            message_ok('the service ' + quote(service.name()) +
                       ' is running with pid(s) %s' % unlist(pid))
        else:
            message_alert('the service ' + quote(service.name()) +
                          ' is not running', level='critical')
