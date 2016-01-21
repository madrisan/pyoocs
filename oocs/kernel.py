# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from platform import release as kernel_release
from os.path import join

from oocs.filesystem import Filesystems, UnixFile
from oocs.io import Config, message_add, quote

class Kernel(object):

    module_name = 'kernel'

    def __init__(self, verbose=False):
        self.verbose = verbose

        self.scan = {
            'module' : self.module_name,
            'checks' : {},
            'status' : {}
        }

        try:
            self.cfg = Config().module(self.module_name)
            self.enabled = (self.cfg.get('enable', 1) == 1)
        except KeyError:
            message_add(self.scan['status'], 'warning',
                self.module_name +
                 ' directive not found in the configuration file')
            self.cfg = {}

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)
        
        self.runtime_params = self.cfg.get("runtime-parameters", {})
        if not self.runtime_params:
            message_add(self.scan['status'], 'warning',
                self.module_name +
                 ':runtime-parameters not found in the configuration file')

        # list of kernel modules that must not be loaded
        self.forbidden_modules = self.cfg.get("forbidden-modules", [])

        self.procfs = Filesystems().procfs
        self.sysfs = Filesystems().sysfs

    def configuration(self): return self.cfg

    def version(self):
        release = kernel_release()
        return release

    def loaded_modules(self):
        # The module name will always show up if the module is loaded as a
        # dynamic module.  If it is built directly into the kernel, it will
        # only show up if it has a version or at least one parameter.
        # The conditions of creation in the built-in case are not by design
        # and may be removed in the future.
        modulesdir = UnixFile(join(self.sysfs, 'module'))
        return sorted(modulesdir.subdirs())

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
        localscan = {}
        for kparameter in self.runtime_params:
            filename = join(self.procfs, 'sys',
                            kparameter.replace('.', '/'))
            f = UnixFile(filename)
            if not f.exists:
                message_add(localscan, 'warning',
                            'no such file: ' + filename)
                continue

            curr_value = int(f.readfile().rstrip())
            req_value = self.runtime_params.get(kparameter, 'N/A')
            if curr_value != req_value:
                message_add(localscan, 'warning',
                            kparameter + ' is ' + quote(curr_value) +
                            ', required: ' + quote(req_value))
            elif self.verbose:
                message_add(localscan, 'info',
                            kparameter + ' = ' + quote(curr_value))

        message_add(self.scan['checks'], 'kernel runtime parameters', localscan)

    def check_forbidden_modules(self):
        loaded_kernel_modules = self.loaded_modules()

        localscan = {}
        for mod in self.forbidden_modules:
            if mod in loaded_kernel_modules:
                message_add(localscan, 'warning',
                            'The kernel module ' + quote(mod) + ' is loaded')
            elif self.verbose:
                message_add(localscan, 'info',
                            'The kernel module ' + quote(mod) + ' is not loaded')

        message_add(self.scan['checks'], 'kernel forbidden modules', localscan)

def check_kernel(verbose=False):
    kernel = Kernel(verbose=verbose)
    if not kernel.enabled:
        if verbose:
            message_add(kernel.scan['status'], 'info',
                        'Skipping ' + quote(kernel.module_name) +
                        ' (disabled in the configuration)')
        return

    if verbose:
        message_add(kernel.scan, 'infos', 'Kernel version: ' + kernel.version())

    kernel.check_runtime_parameters()
    kernel.check_forbidden_modules()

    return kernel.scan
