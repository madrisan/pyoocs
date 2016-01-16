# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from oocs.io import Config, message_add, quote

class Packages(object):

    module_name = 'packages'

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
        
        self.package_manager = self.cfg.get('package-manager')
        self.forbidden = self.cfg.get('forbidden')

    def installed_packages(self, nameonly=False):
        if not self.package_manager == 'rpm':
            return None

        try:
            import rpm
        except ImportError:
            return None

        ts = rpm.TransactionSet()
        iterator = ts.dbMatch()
        pcks = []
        for hdr in iterator:
            # note: hdr[rpm.RPMTAG_VERSION]
            #       hdr[rpm.RPMTAG_RELEASE]
            if nameonly:
                pcks.append(hdr[rpm.RPMTAG_NAME])
            else:
                pcks.append(hdr[rpm.RPMTAG_NAME] + '@' + hdr[rpm.RPMTAG_ARCH])

        return pcks

def check_packages(verbose=False):
    localscan = {}
    pck = Packages(verbose=verbose)

    if not pck.enabled:
        if verbose:
            message_add(pck.scan['status'], 'info',
                'skipping ' + quote(pck.module_name) +
                ' (disabled in the configuration)')
        return pck.scan
 
    if not pck.package_manager == "rpm":
        message_add(pck.scan['status'], 'warning',
            'unsupported package manager ' + quote(pck.package_manager) +
            ' ... skip')
        return pck.scan

    installed_packages = pck.installed_packages(nameonly=True)
    if not installed_packages:
        message_add(pck.scan['status'], 'warning',
            'no rpm installed... (did you install the rpm python bindings?)')
        return pck.scan

    for pk in list(set(pck.forbidden) & set(installed_packages)):
        message_add(localscan, 'warning',
            'forbidden package found: ' + quote(pk))

    message_add(pck.scan['checks'], 'software packages', localscan)

    return pck.scan
