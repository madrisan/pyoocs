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

    def configuration(self): return self.cfg
    def module_name(self): return self.module

def check_root_path_variable(verbose=False):
    if geteuid() != 0:
        message_alert("This check (" + __name__ + ") must be run as root" +
                      " ... skip", level='warning')
        return

    env_path_root = getenv('PATH', '')
    if verbose:
        message('root PATH is: ' + quote(env_path_root))

    #env_path_root = "/usr/bin::./bin:.:/dev/null:/no/such/dir:/var/tmp:"
    if '::' in env_path_root:
        message_alert('root PATH contains an empty directory (::)',
                      level='warning')
    if env_path_root[-1] == ':':
        message_alert('root PATH has a trailing :', level='warning')
    for ptok in env_path_root.split(':'):
        ptok_stripped = ptok.lstrip().rstrip()
        # ignore empty pathes already catched by a previous check
        if not ptok_stripped: continue

        if ptok_stripped == '.':
            message_alert('root PATH contains .', level='critical')
        elif not ptok_stripped.startswith('/'):
            message_alert('root PATH contains a non absolute path: ' +
                          quote(ptok), level='warning')
        else:
            fp = UnixFile(ptok)
            if not fp.exists:
                message_alert('root PATH contains ' + quote(ptok) +
                    ' which does not exist', level='warning')
                continue
            if not fp.isdir():
                message_alert('root PATH contains ' + quote(ptok) +
                    ' which is not a directory', level='critical')
            if not (fp.check_owner('root') and fp.check_group('root')):
                message_alert('root PATH contains ' + quote(ptok) +
                    ' which is not owned by root', level='critical')
            match_mode, val_found = fp.check_mode(['040700','040750','040755'])
            if not match_mode:
                message_alert('root PATH contains ' + quote(ptok) +
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
    check_root_path_variable(verbose=verbose)
