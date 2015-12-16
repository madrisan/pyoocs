# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

import rpm

from oocs.config import Config
from oocs.output import message, message_alert, message_ok, quote

class Packages(object):

    module_name = 'packages'

    def __init__(self, verbose=False):
        self.verbose = verbose

        try:
            self.cfg = Config().read(self.module_name)
            self.enabled = (self.cfg.get('enable', 1) == 1)
        except KeyError:
            message_alert(self.module_name +
                          ' directive not found in the configuration file',
                          level='warning')
            self.cfg = {}

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)
        
        self.package_manager = self.cfg.get('package-manager')
        self.forbidden = self.cfg.get('forbidden')
        
    def installed_packages(self, nameonly=False):
        if not self.package_manager == 'rpm':
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
    pck = Packages(verbose=verbose)
    if not pck.enabled:
        if verbose:
            message_alert('Skipping ' + quote(pck.module_name) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking software packages', header=True, dots=True)
    if not pck.package_manager == "rpm":
        message_alert('unsupported package manager ' +
                      quote(pck.package_manager) +
                      ' ... skip', level='warning')
        return

    installed_packages = pck.installed_packages(nameonly=True)
    for pck in list(set(pck.forbidden) & set(installed_packages)):
        message_alert('forbidden package found: ' + quote(pck), level='warning')
