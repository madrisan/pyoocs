# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from os.path import join

from oocs.config import config
from oocs.filesystem import UnixFile
from oocs.output import message, message_alert, message_ok, quote

class Partitions:
    def __init__(self, procfile):
        self.procfile = procfile
        self.partitions = []

        try:
            cfg = config().read("partitions")
        except KeyError:
            message_alert("configuration file: 'partitions' block not found!",
                          level='warning')
            cfg = {}

        self.required_parts = cfg.get("required", {})
        if not self.required_parts:
            message_alert(
                "configuration file: 'partitions:requires' block not found!",
                level='warning')

        self.partitions = self._parse()

    def _check_partition_opts(self, mountpoint, opts=''):
        for line in self.partitions:
            cols = line.split()
            if mountpoint == cols[1]:
                mount_opts = cols[3]
                mount_opts_list = cols[3].split(',')
                opts_match = set(opts).issubset(set(mount_opts_list))
                return (opts_match, mount_opts)

        return (False, None)

    def _partition_exists(self, mountpoint):
        for line in self.partitions:
            if mountpoint in line.split(): return True
        return False

    def _parse(self):
        input = UnixFile(self.procfile, abort_on_error=True)
        return input.readlines() or []

    def check_required(self, verbose=False):
        for part in self.required_parts:
            mountpoint = part['mountpoint']
            req_opts = part.get('opts', '')

            exists = self._partition_exists(mountpoint)
            if not exists:
                message_alert(mountpoint + ": no such partition",
                              level="critical")
                continue

            (match, opts) = self._check_partition_opts(mountpoint, req_opts)
            if not match and opts:
                message_alert(mountpoint + ": mount options "
                    + quote(opts) + ", required: " + quote(req_opts))
            elif not opts:
                message_alert(mountpoint + ": no such filesystem")
            elif verbose:
                message_ok(mountpoint + ' (' + opts + ')')

def check_partitions(verbose=False):
    module = 'partitions'
    cfg = config().read(module)
    if cfg.get('enable', 1) != 1:
        if verbose:
            message_alert('Skipping ' + quote(module) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking partitions', header=True, dots=True)

    procfilesystem = cfg.get('procfilesystem', '/proc')
    partitions = Partitions(procfile=join(procfilesystem, 'mounts'))
    partitions.check_required(verbose=verbose)
