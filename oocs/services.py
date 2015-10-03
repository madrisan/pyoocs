# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

import glob
from os import sep
from os.path import join
from pwd import getpwuid

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

        self.must_be_running = self.cfg.get("must-be-running", [])
        self.must_be_stopped = self.cfg.get("must-be-stopped", [])

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)

    def configuration(self): return self.cfg
    def enabled(self): return self.enabled
    def module_name(self): return self.module
    def must_be_running(self): return self.must_be_running
    def must_be_stopped(self): return self.must_be_stopped

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
        self.state, self.fullstatus = self._status()

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
        Return a touple (state-string, full-status-infos-dict).
        state-string will be 'running' or 'down' and will reflect the state of
        the 'self.service' process(es).
        full-status-infos-dict is a dictionaty containing the information
        provided by /proc/<pid>/status of each process pid:
           srv_full_status[pidnum] = dictionary containing the status of the
                                     process whith pid equal to pidnum
        """

        cmdlines = glob.glob(join(self.proc_filesystem, '*', 'cmdline'))
        srv_state = 'down'
        srv_full_status = {}

        for f in cmdlines:
            for srv in self.service.split('|'):
                cmdlinefile = UnixFile(f)
                if not cmdlinefile.isfile(): continue
                if cmdlinefile.readfile().startswith(srv):  # FIXME
                    pid = f.split(sep)[2]
                    proc_pid_status = self._proc_status_parser(pid)
                    srv_full_status[pid] = proc_pid_status
                    srv_state = 'running'

        return (srv_state, srv_full_status)

    def name(self):
        return self.service

    def pid(self):
        """Return the list of pid numbers or an empty list when the process
           is not running"""
        return self.fullstatus.keys()

    def ppid(self):
        ppids = []
        for pid in self.pid():
            ppid = self.fullstatus.get(pid)['ppid'][0]
            ppids.append(ppid)
        return ppids

    def state(self):
        return self.state

    def uid(self):
        real_uids = []
        for pid in self.pid():
            # Real, effective, saved set, and file system UIDs
            uids = self.fullstatus.get(pid)['uid']
            real_uids.append(uids[0])
        return real_uids

    def gid(self):
        real_gids = []
        for pid in self.pid():
            # Real, effective, saved set, and file system GIDs
            gids = self.fullstatus.get(pid)['gid']
            real_gids.append(gids[0])
        return real_gids

    def owner(self):
        owners = []
        for uid in self.uid():
            owners.append(getpwuid(int(uid)).pw_name)
        return owners

    def threads(self):
        threads_num = 0
        for pid in self.pid():
            threads_num += int(self.fullstatus.get(pid)['threads'][0])
        return threads_num

def check_services(verbose=False):
    services = Services(verbose=verbose)
    if not services.enabled:
        if verbose:
            message_alert('Skipping ' + quote(module_name()) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking services', header=True, dots=True)

    #message('runlevel: ' + services.runlevel())

    for srv in services.must_be_running:
        service = Service(srv)
        pids = service.pid()
        owners = service.owner()
        if pids and services.verbose:
            message_ok(
                'the service ' + quote(service.name()) +
                ' is running (with pid:%s owner:%s)' % (
                unlist(pids,sep=','), unlist(owners,sep=',')))
        else:
            message_alert('the service ' + quote(service.name()) +
                          ' is not running', level='critical')

    for srv in services.must_be_stopped:
        service = Service(srv)
        pids = service.pid()
        if pids:
            message_alert('the service ' + quote(service.name()) +
                          ' should not be running', level='critical')
        elif services.verbose:
            message_ok('the service ' + quote(service.name()) +
                       ' is not running as required')
