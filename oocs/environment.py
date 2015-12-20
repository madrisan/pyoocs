# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from os import getenv, geteuid

from oocs.filesystem import UnixFile
from oocs.io import Config, die, message_add, quote

class Environment(object):

    module_name = 'environment'

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

    def configuration(self): return self.cfg

    def getenv(self, variable): return getenv(variable, '')

    def check_ld_library_path(self):
        env_var = 'LD_LIBRARY_PATH'
        env_ld_library_path = self.getenv(env_var)
        localscan = {}

        if self.verbose:
            message_add(localscan, 'info',
                        env_var + ' is ' + quote(env_ld_library_path))
        if env_ld_library_path:
            message_add(localscan, 'warning',
                self.module_name +
                env_var + ' is not empty: (' + quote(env_ld_library_path))

        message_add(self.scan['checks'], 'root environment -- LD_LIBRARY_PATH',
                    localscan)

    def check_path(self):
        env_var = 'PATH'
        env_path = self.getenv(env_var)
        localscan = {}

        if self.verbose:
            message_add(localscan, 'info', env_var + ' is ' + quote(env_path))

        # 'env_path' for code DEBUG:
        # env_path = "/usr/bin::./bin:.:/dev/null:/no/such/dir:/var/tmp:"
        if '::' in env_path:
            message_add(localscan, 'warning',
                        'PATH contains an empty directory (::)')
        if env_path[-1] == ':':
            message_add(localscan, 'warning', 'PATH has a trailing :')

        for ptok in env_path.split(':'):
            ptok_stripped = ptok.lstrip().rstrip()
            # ignore empty pathes already catched by a previous check
            if not ptok_stripped: continue

            if ptok_stripped == '.':
                message_add(localscan, 'critical', 'PATH contains .')
            elif not ptok_stripped.startswith('/'):
                message_add(localscan, 'warning',
                    'PATH contains a non absolute path: ' + quote(ptok))
            else:
                fp = UnixFile(ptok)
                if not fp.exists:
                    message_add(localscan, 'warning',
                        'PATH contains ' + quote(ptok) +
                        ' which does not exist')
                    continue
                if not fp.isdir():
                    message_add(localscan, 'critical',
                        'PATH contains ' + quote(ptok) +
                        ' which is not a directory')

                # FIXME: users can add non root dirs. ex: $HOME/bin
                if not (fp.check_owner('root') and fp.check_group('root')):
                    message_add(localscan, 'critical',
                                'PATH contains ' + quote(ptok) +
                                ' which is not owned by root')
                match_mode, val_found = (
                    fp.check_mode(['040700','040750','040755']))
                if not match_mode:
                    message_add(localscan, 'critical',
                        'PATH contains ' + quote(ptok) +
                        ' which has wrong (' + val_found + ') permissions')

        message_add(self.scan['checks'], 'root environment -- PATH', localscan)

def check_environment(verbose=False):
    environment = Environment(verbose=verbose)
    if not environment.enabled:
        if verbose:
            message_add(environment.scan['status'], 'info',
                        'Skipping ' + quote(environment.module_name) +
                        ' (disabled in the configuration)')
        return

    if geteuid() != 0:
        message_add(environment.scan['status'], 'warning',
                    'This check (' + __name__ + ') must be run as root' +
                    ' ... skip')
        return

    environment.check_path()
    environment.check_ld_library_path()

    return environment.scan
