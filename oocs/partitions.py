# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from oocs.config import read_config
from oocs.filesystem import unix_file
from oocs.output import message, message_alert, quote

class partitions:
    def __init__(self, procfile):
        self.procfile = procfile
        self.partitions = []

        try:
            partscfg = read_config("partitions")
        except KeyError:
            message_alert("configuration file: 'partitions' block not found!",
                          level='warning')
            partscfg = {}

        self.required_parts = partscfg.get("required", {})
        if not self.required_parts:
            message_alert(
                "configuration file: 'partitions:requires' block not found!",
                level='warning')

        self.partitions = self._parse()

    def _check_partition_opts(self, mountpoint, opts=''):
        for line in self.partitions:
            if mountpoint in line.split():
                mount_opts = line.split()[3]
                mount_opts_list = line.split()[3].split(',')
                opts_match = set(opts).issubset(set(mount_opts_list))
                return (opts_match, mount_opts)

        return (False, mount_opts)

    def _partition_exists(self, mountpoint):
        for line in self.partitions:
            if mountpoint in line.split(): return True
        return False

    def _parse(self):
        input = unix_file(self.procfile, abort_on_error=True)
        return input.readlines() or []

    def check_required(self):
        for part in self.required_parts:
            mountpoint = part['mountpoint']
            req_opts = part.get('opts', '')

            exists = self._partition_exists(mountpoint)
            if not exists:
                message_alert(mountpoint + ": not such partition",
                              level="critical")
                continue

            (match, opts) = self._check_partition_opts(mountpoint, req_opts)
            if not match:
                message_alert(mountpoint + ": mount options "
                    + quote(opts) + ", required: " + quote(req_opts))

def check_partitions(verbose=False):
    message('Checking partitions', header=True, dots=True)

    fs = partitions(procfile='/proc/mounts')
    fs.check_required()
