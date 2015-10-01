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
        """
        Note: service can be a chain of commands as in the following example:
           'syslogd|/sbin/rsyslogd'
        The service string must match the one displayed by 'ps'.
        """
        Services.__init__(self)
        self.service = service
        self.proc_filesystem = Filesystem().procfilesystem
        self.status, self.pids, self.uids, self.gids = self._status()

    def _proc_status_parser(self, pid):
        procfile = glob.glob(join(self.proc_filesystem, str(pid), 'status'))[0]
        rawdata = UnixFile(procfile).readlines() or []
        data = {}
        for line in rawdata:
            cols = line.split(':')
            key = cols[0].lower()
            values = cols[1].rstrip('\n').split()
            data[key] = values
        return data

    def _status(self):
        """
        Return a touple (status, pids) containing the status of the process(es)
        (can be 'running' or 'down') and the list of the pid numbers (or an
        empty one when the status is 'down').

        If 'service' is a chain of commands, the global status of the given
        processes will be considered.  This mean that the final status will be
        set to 'running' if at least one of the processes will be found, and the
        list of all the pid numbers will be reported.
        """
        cmdlines = glob.glob(join(self.proc_filesystem, '*', 'cmdline'))
        srv_gids = []
        srv_pids = []
        srv_uids = []
        srv_status = 'down'
        for f in cmdlines:
            for srv in self.service.split('|'):
                cmdlinefile = UnixFile(f)
                if not cmdlinefile.isfile(): continuea
                if cmdlinefile.readfile().startswith(srv):  # FIXME
                    pid = int(f.split(sep)[2])
                    srv_pids.append(pid)

                    proc_status = self._proc_status_parser(pid)
                    # Real, effective, saved set, and file system UIDs
                    uid = proc_status.get('uid', [None, None, None, None])
                    # Real, effective, saved set, and file system GIDs
                    gid = proc_status.get('gid', [None, None, None, None])
                    srv_uids.append(uid[0])
                    srv_gids.append(gid[0])

                    srv_status = 'running'

        return (srv_status, srv_pids, srv_uids, srv_gids)

    def name(self):
        return self.service

    def pid(self):
        """Return the list of pid numbers or an empty list when the process
           is not running"""
        return self.pids

    def status(self):
        return self.status

    def uid(self): return self.uids
    def gid(self): return self.gids

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
        uids = service.uid()
        gids = service.gid()
        if pid and services.verbose:
            message_ok('the service ' + quote(service.name()) +
                       ' is running with pid(s) %s, uid %s, gid %s' %
                       (unlist(pid,sep=','),
                        unlist(uids,sep=','), unlist(gids, sep=',')))
        else:
            message_alert('the service ' + quote(service.name()) +
                          ' is not running', level='critical')
