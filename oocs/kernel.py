# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from platform import release as kernel_release
from os.path import join

from oocs.config import config
from oocs.filesystem import UnixFile
from oocs.output import message, message_alert, message_ok, quote

class Kernel:
    def __init__(self):
        self.runtime_params = {}

        try:
            cfg = config().read("kernel")
        except KeyError:
            message_alert("configuration file: 'kernel' block not found!",
                          level='warning')
            cfg = {}

        self.runtime_params = cfg.get("parameters", {})
        if not self.runtime_params:
            message_alert(
                "configuration file: 'kernel:parameters' block not found!",
                level='warning')

        self.procfilesystem = cfg.get('procfilesystem', '/proc')

    def version(self):
        release = kernel_release()
        return release

    def version_numeric(self):
        release = self.version()
        if not release: return None

        item = release.split('.')
        maj = int(item[0])
        min = int(item[1])
        patch = int(item[2].split('-')[0])

        # see /usr/include/linux/version.h
        return (((maj) << 16) + ((min) << 8) + (patch))

    def check_runtime_parameters(self, verbose=False):
        for kparameter in self.runtime_params:
            filename = join(self.procfilesystem, 'sys',
                            kparameter.replace('.', '/'))
            f = UnixFile(filename)
            if not f.exists:
                message_alert("no such file: " + filename, level="warning")
                continue

            curr_value = int(f.readfile().rstrip())
            req_value = self.runtime_params.get(kparameter, 'N/A')
            if curr_value != req_value:
                message_alert(kparameter + " is " + quote(curr_value) +
                              ", required: " + quote(req_value),
                              level="warning")
            elif verbose:
                message_ok(kparameter + ' = ' + quote(curr_value))

def check_kernel(verbose=False):
    module = 'kernel'
    cfg = config().read(module)
    if cfg.get('enable', 1) != 1:
        if verbose:
            message_alert('Skipping ' + quote(module) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking kernel runtime parameters', header=True, dots=True)

    kernel = Kernel()
    message('Kernel version: ' + kernel.version())
    kernel.check_runtime_parameters(verbose=verbose)