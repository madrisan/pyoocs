# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from os import getenv, geteuid

from oocs.config import Config
from oocs.filesystem import UnixFile
from oocs.output import die, message, message_alert, quote

class Environment(object):
    def __init__(self, verbose=False):
        self.module = 'environment'
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
        self.verbose = True

    def configuration(self): return self.cfg
    def module_name(self): return self.module

    def getenv(self, variable): return getenv(variable, '')
    def check_ld_library_path(self):
        env_var = 'LD_LIBRARY_PATH'
        env_ld_library_path = self.getenv(env_var)
        if self.verbose:
            message(env_var + ' is ' + quote(env_ld_library_path))
        if env_ld_library_path:
            message_alert(env_var + ' is not empty: (' +
                          quote(env_ld_library_path), level='warning')

    def check_path(self):
        env_var = 'PATH'
        env_path = self.getenv(env_var)
        if self.verbose:
            message(env_var + ' is ' + quote(env_path))
        #env_path = "/usr/bin::./bin:.:/dev/null:/no/such/dir:/var/tmp:"
        if '::' in env_path:
            message_alert('PATH contains an empty directory (::)',
                          level='warning')
        if env_path[-1] == ':':
            message_alert('PATH has a trailing :', level='warning')
        for ptok in env_path.split(':'):
            ptok_stripped = ptok.lstrip().rstrip()
            # ignore empty pathes already catched by a previous check
            if not ptok_stripped: continue

            if ptok_stripped == '.':
                message_alert('PATH contains .', level='critical')
            elif not ptok_stripped.startswith('/'):
                message_alert('PATH contains a non absolute path: ' +
                              quote(ptok), level='warning')
            else:
                fp = UnixFile(ptok)
                if not fp.exists:
                    message_alert('PATH contains ' + quote(ptok) +
                        ' which does not exist', level='warning')
                    continue
                if not fp.isdir():
                    message_alert('PATH contains ' + quote(ptok) +
                        ' which is not a directory', level='critical')

                # FIXME: users can add non root dirs. ex: $HOME/bin
                if not (fp.check_owner('root') and fp.check_group('root')):
                    message_alert('PATH contains ' + quote(ptok) +
                        ' which is not owned by root', level='critical')
                match_mode, val_found = (
                    fp.check_mode(['040700','040750','040755']))
                if not match_mode:
                    message_alert('PATH contains ' + quote(ptok) +
                        ' which has wrong (' + val_found + ') permissions',
                        level='critical')

def check_environment(verbose=False):
    environment = Environment(verbose=verbose)
    if not environment.enabled:
        if verbose:
            message_alert('Skipping ' + quote(environment.module_name()) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking root environment', header=True, dots=True)

    if geteuid() != 0:
        message_alert("This check (" + __name__ + ") must be run as root" +
                      " ... skip", level='warning')
        return

    environment.check_path()
    environment.check_ld_library_path()
