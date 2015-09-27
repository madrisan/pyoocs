# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from platform import release as kernel_release
from os.path import join

from oocs.config import Config
from oocs.filesystem import UnixFile
from oocs.output import message, message_alert, message_ok, quote

class Kernel(object):
    def __init__(self, verbose=False):
        self.module = 'kernel'
        self.verbose = verbose

        try:
            self.cfg = Config().read(self.module)
            self.enabled = (self.cfg.get('enable', 1) == 1)
        except KeyError:
            message_alert(self.module +
                          ' directive not found in the configuration file',
                          level='warning')
            self.cfg = {}

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)
        
        self.runtime_params = self.cfg.get("parameters", {})
        if not self.runtime_params:
            message_alert(self.module +
                ':parameters not found in the configuration file',
                level='warning')

        self.procfilesystem = self.cfg.get('procfilesystem', '/proc')

    def configuration(self): return self.cfg
    def enabled(self): return self.enabled
    def module_name(self): return self.module

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

    def check_runtime_parameters(self):
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
            elif self.verbose:
                message_ok(kparameter + ' = ' + quote(curr_value))

def check_kernel(verbose=False):
    kernel = Kernel(verbose=verbose)
    if not kernel.enabled:
        if verbose:
            message_alert('Skipping ' + quote(kernel.module_name()) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking kernel runtime parameters', header=True, dots=True)

    message('Kernel version: ' + kernel.version())
    kernel.check_runtime_parameters()
