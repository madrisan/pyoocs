# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

import errno, os, stat
import grp, pwd
import shlex, subprocess
from os.path import isdir, join
from sys import version_info as pyver

from oocs.config import Config
from oocs.output import die, message, message_alert, message_ok, quote

# S_IRWXU     00700  mask for file owner permissions
# S_IRUSR     00400  owner has read permission
# S_IWUSR     00200  owner has write permission
# S_IXUSR     00100  owner has execute permission
# S_IRWXG     00070  mask for group permissions
# S_IRGRP     00040  group has read permission
# S_IWGRP     00020  group has write permission
# S_IXGRP     00010  group has execute permission
# S_IRWXO     00007  mask for permissions for others (not in group)
# S_IROTH     00004  others have read permission
# S_IWOTH     00002  others have write permission
# S_IXOTH     00001  others have execute permission
# S_IFMT    0170000  bitmask for the file type bitfields
# S_IFSOCK  0140000  socket
# S_IFLNK   0120000  symbolic link
# S_IFREG   0100000  regular file
# S_IFBLK   0060000  block device
# S_IFDIR   0040000  directory
# S_IFCHR   0020000  character device
# S_IFIFO   0010000  FIFO
# S_ISUID   0004000  set UID bit
# S_ISGID   0002000  set-group-ID bit (see below)
# S_ISVTX   0001000  sticky bit (see below)

mod_dir = stat.S_IFDIR
mod_chdev = stat.S_IFCHR
mod_stickybit = stat.S_ISVTX

class Filesystem(object):
    def __init__(self, verbose=False):
        self.module = 'filesystem'
        self.verbose = verbose

        try:
           self.cfg = Config().read(self.module)
           self.enabled = (self.cfg.get('enable', 1) == 1)
        except KeyError:
            message_alert(self.module +
                          ' directive not found in the configuration file',
                          level='warning')
            self.cfg = {}

    def configuration(self): return self.cfg
    def enabled(self): return self.enabled
    def module_name(self): return self.module

class UnixFile(object):
    def __init__(self, filename, abort_on_error=False):
        self.filename = filename
        self.exists = False
        try:
            self.exists = os.path.exists(self.filename)
            #self.mode = oct(os.stat(filename)[stat.ST_MODE])
            stat_info = os.stat(self.filename)
            self.mode = oct(stat_info[stat.ST_MODE])
            self.uid = stat_info.st_uid
            self.gid = stat_info.st_gid
            self.owner = pwd.getpwuid(self.uid)[0]
            self.group = grp.getgrgid(self.gid)[0]
        except OSError:
            if abort_on_error and not self.exists:
                die(1, "file not found: " + self.filename)
            elif abort_on_error:
                die(1, "i/o error while opening " + self.filename)

            self.mode = None    # FIXME: os.strerror(e.errno)
            self.uid = self.gid = None
            self.owner = self.group = None


    def check_mode(self, shouldbe):
        if pyver[0] == 3:
            # In Python3 there is no longer a 'basestring' data type
            str_types = str,
        else:
            str_types = basestring,

        try:
            iter(shouldbe)
        except TypeError:
            shouldbe = [shouldbe]

        shouldbe_str = ''
        for mode in shouldbe:
            if not isinstance(mode, str_types): mode = str(oct(mode))
            shouldbe_str += (mode + ' or ')
        shouldbe_str = shouldbe_str[:-len(' or ')]

        for mode in shouldbe:
            # trasform octal strings into integers
            if isinstance(mode, str_types): mode = int(mode, 8)
            if self.mode == oct(mode):
                return (True, shouldbe_str, self.mode)
        return (False, shouldbe_str, self.mode)

    def check_owner(self, shouldbe_usr, shouldbe_grp):
        return (self.owner == shouldbe_usr) and (self.group == shouldbe_grp)

    def name(self): return self.filename
    def basename(self): return os.path.basename(self.filename)
    def dirname(self): return os.path.dirname(self.filename)

    def mode(self): return str(self.mode)

    def uid(self): return self.uid
    def gid(self): return self.gid
    def owner(self): return self.owner
    def group(self): return self.group

    def exists(self): return self.exists

    def isdir(self): return os.path.isdir(self.filename)
    def isfile(self): return os.path.isfile(self.filename)

    def readfile(self, len=0):
        "Return content of a file"
        if not os.path.isfile(self.filename):
            return None
        if len:
            return open(self.filename, 'r').read(len)
        return open(self.filename, 'r').read()

    def readlines(self):
        "Return content of each line of a text file"
        if not os.path.isfile(self.filename):
            return None

        fd = open(self.filename, 'r')
        try:
            content = fd.readlines()
        except:
            content = []
        return content

    # owned by root and not writable by others
    def owned_by_root(self):
        if not self.mode: return False  # the file does not exist
        return ((self.uid == 0) and (self.gid == 0) and
                  not ((int(self.mode, 8) % 8) >> 1 & 1))

    def command_su_root(self):
        return (self.filename == '/bin/su' and self.args in [['-'], []])

    def filelist(self):
        if not isdir(self.filename): return []
        try:
            (_, _, files) = os.walk(self.filename).next()
        except:
            # In Python3, use next(x) instead of x.next()
            (_, _, files) = next(os.walk(self.filename))

        return files

    def subdirs(self):
        try: 
            dirlist = os.listdir(self.filename)
            return [e for e in dirlist if isdir(join(self.filename, e))]
        except OSError:
            return []

class UnixCommand(UnixFile):
    """Derived class for commands: binary [options]"""
    def __init__(self, cmdline):
        UnixFile.__init__(self, cmdline.split()[0])
        self.cmdline = cmdline
        self.cmdname = cmdline.split()[0]
        self.args = cmdline.split()[1:]

    def cmnd_args(self): return self.args
    def cmnd_name(self): return self.cmdname

    def execute(self):
        args = shlex.split(self.cmdline)
        if not self.exists:
            return ('', 'No such executable or script: ' + self.cmdname, 1)
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            out, err = p.communicate()
            retcode = p.returncode
        except:
            out = err = None
            retcode = 1

        return (out, err, retcode)

def check_filesystem(verbose=False):
    filesystem = Filesystem(verbose=verbose)
    if not filesystem.enabled:
        if verbose:
            message_alert('Skipping ' + quote(filesystem.module_name()) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking the permissions of some system folders',
            header=True, dots=True)

    filemodes = {
        '/dev/null'  : mod_chdev|0o0666,
        '/dev/random': mod_chdev|0o0666,
        '/dev/random': mod_chdev|0o0666,
        '/'          : mod_dir|0o0755,
        '/home'      : mod_dir|0o0755,
        '/root'      : mod_dir|0o0550,
        '/tmp'       : mod_dir|mod_stickybit|0o0777,
        '/var/tmp'   : mod_dir|mod_stickybit|0o0777,
    }

    cfg = filesystem.configuration()

    for f in sorted(filemodes.keys()):
        fp = UnixFile(f)

        req_mode_cfg = cfg.get(f+"-modes", [])
        if req_mode_cfg: req_mode = req_mode_cfg
        else: req_mode = filemodes[f]

        (match, val_req, val_found) = fp.check_mode(req_mode)
        if not match:
            message_alert(fp.name(), reason = val_found +
                          ' instead of ' + val_req,
                          level='critical')
        elif verbose:
            message_ok(fp.name())

    message("Checking the mode of the /home subdirs", header=True, dots=True)

    home = UnixFile('/home')
    for subdir in home.subdirs():
        req_mode = mod_dir|0o0700
        sdname = join('/home', subdir)

        fp = UnixFile(sdname)
        (match, val_req, val_found) = fp.check_mode(req_mode)
        if not match:
            message_alert(fp.name(),
                reason = val_found +
                ' instead of ' + val_req, level='warning')

    message('Checking for file permissions in /etc/profile.d',
            header=True, dots=True)

    dp = UnixFile('/etc/profile.d')
    for file in dp.filelist():
        fname = join(dp.name(), file)
        fp = UnixFile(fname)
        match = fp.check_owner('root', 'root')
        if not match:
            message_alert(fp.name(),
                reason = quote(fp.owner() + '.' + fp.group()) +
                ' instead of ' + quote('root.root'), level='critical')

