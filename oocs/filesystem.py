# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

import os
import stat
import grp
import pwd
import shlex
import subprocess
from os.path import isdir, join

from oocs.config import Config
from oocs.output import message_add, quote, unlist
from oocs.py2x3 import isbasestring

# Octal representation for files modes:
#
#  S_IRWXU     00700  mask for file owner permissions
#  S_IRUSR     00400  owner has read permission
#  S_IWUSR     00200  owner has write permission
#  S_IXUSR     00100  owner has execute permission
#  S_IRWXG     00070  mask for group permissions
#  S_IRGRP     00040  group has read permission
#  S_IWGRP     00020  group has write permission
#  S_IXGRP     00010  group has execute permission
#  S_IRWXO     00007  mask for permissions for others (not in group)
#  S_IROTH     00004  others have read permission
#  S_IWOTH     00002  others have write permission
#  S_IXOTH     00001  others have execute permission
#  S_IFMT    0170000  bitmask for the file type bitfields
#  S_IFSOCK  0140000  socket
#  S_IFLNK   0120000  symbolic link
#  S_IFREG   0100000  regular file
#  S_IFBLK   0060000  block device
#  S_IFDIR   0040000  directory
#  S_IFCHR   0020000  character device
#  S_IFIFO   0010000  FIFO
#  S_ISUID   0004000  set UID bit
#  S_ISGID   0002000  set-group-ID bit (see below)
#  S_ISVTX   0001000  sticky bit (see below)

class Filesystems(object):

    module_name = 'filesystem'

    def __init__(self, verbose=False):
        self.verbose = verbose

        self.scan = {
            'module' : self.module_name,
            'checks' : {}
        }
        self.status = {}

        try:
            self.cfg = Config().module(self.module_name)
            self.enabled = (self.cfg.get('enable', 1) == 1)
        except KeyError:
            message_add(self.status, 'warning',
                self.module_name +
                 ' directive not found in the configuration file')
            self.cfg = {}

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)

        self.procfs = self.cfg.get('procfilesystem', '/proc')
        self.sysfs = self.cfg.get('sysfilesystem', '/sys')

        self.required_filesystems = self.cfg.get('required', {})
        if not self.required_filesystems:
            message_add(self.status, 'warning',
                self.module_name +
                ':required not found in the configuration file')

        self.file_permissions = self.cfg.get('file-permissions', {})
        if not self.file_permissions:
            message_add(self.status, 'warning',
                self.module_name +
                ':file-permissions not found in the configuration file')

        self.proc_mountsfile = join(self.procfs, 'mounts')

    def configuration(self): return self.cfg

    def dump_proc_mounts(self):
        input = UnixFile(self.proc_mountsfile)
        return input.readlines() or []

class Filesystem(Filesystems):

    def __init__(self, mountpoint):
        Filesystems.__init__(self)
        self.mountpoint = mountpoint

        self.filesystems = self.dump_proc_mounts()
        """ self.is_mounted: True if mounted otherwise False
            self.fstype: filesystem type
            self.mount_opts: list of the mount options """
        self.is_mounted, self.fstype, self.mount_opts = self._is_mounted()

    def _is_mounted(self):
        """ Return the tuple (True, list-of-mount-options) or (False, None) """
        self.filesystems = self.dump_proc_mounts()
        for line in self.filesystems:
            cols = line.split()
            if self.mountpoint == cols[1]:
                return (True, cols[2], cols[3].split(','))
        return (False, None, None)

    def check_mount_opts(self, req_opts):
        if not self.is_mounted:
            return (False, None)
        req_opts_list = req_opts.split(',')
        opts_match = set(req_opts_list).issubset(set(self.mount_opts))
        return (opts_match, ', '.join(self.mount_opts))

class UnixFile(object):

    def __init__(self, filename, abort_on_error=False):
        self.filename = filename
        self.exists = False
        try:
            self.exists = os.path.exists(self.filename)
            # note: os.stat follows symbolic links
            # we have to use os.lstat instead if we do not want this behaviour
            stat_info = os.stat(self.filename)
            self.mode = oct(stat_info[stat.ST_MODE])
            self.uid = stat_info.st_uid
            self.gid = stat_info.st_gid
            try:
               self.owner = pwd.getpwuid(self.uid)[0]
            except KeyError:
               self.owner = None
            try:
               self.group = grp.getgrgid(self.gid)[0]
            except KeyError:
               self.group = None
        except OSError:
            if abort_on_error and not self.exists:
                die(1, "file not found: " + self.filename)
            elif abort_on_error:
                die(1, "i/o error while opening " + self.filename)

            self.mode = None    # FIXME: os.strerror(e.errno)
            self.uid = self.gid = None
            self.owner = self.group = None

    def check_mode(self, shouldbe):
        """check if the file object has mode 'shouldbe'.
           'shouldbe' must be a string representaing the octal desired value.
           see on the top of this file. """
        if not isinstance(shouldbe, list): shouldbe = [shouldbe]
        for mode in shouldbe:
            if isbasestring(mode):
                mode = int(mode, 8)
            else:
                mode = str(oct(mode))
            if self.mode == oct(mode):
                return (True, self.mode)

        return (False, self.mode)

    def check_owner(self, shouldbe_usr):
        if not self.owner:
            raise KeyError('uid not found: %s' % self.uid)
        return (self.owner == shouldbe_usr)

    def check_group(self, shouldbe_grp):
        if not self.group:
            raise KeyError('gid not found: %s' % self.gid)
        return (self.group == shouldbe_grp)

    def name(self): return self.filename
    def basename(self): return os.path.basename(self.filename)
    def dirname(self): return os.path.dirname(self.filename)

    def mode(self): return str(self.mode)

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

def check_file_permissions(file_permissions, verbose=False):
    localscan = {}

    for file in sorted(file_permissions.keys()):
        values = file_permissions[file]
        req_owner = values[0]
        req_group = values[1]
        # multiple different modes are allowed
        req_modes = values[2].split('|')

        fp = UnixFile(file)
        match_mode, val_found = fp.check_mode(req_modes)

        if not val_found:
            message_add(localscan, 'warning',
                fp.name() + ': no such file or directory')
            continue

        try:
            match_perms = (
            fp.check_owner(req_owner) and fp.check_group(req_group))
        except:
            message_add(localscan, 'warning',
                fp.name() + ': no such user or group ' +
                quote(req_owner + ':' + req_group))
            match_perms = False

        if not (match_mode and match_perms):
            message_add(localscan, 'warning',
                fp.name() + ': invalid permissions, ' +
                'should be: ' + req_owner + ':' + req_group +
                ' ' + unlist(req_modes, sep=' or '))
        elif verbose:
            message_add(localscan, 'info',
                fp.name() + '  (' + fp.mode + ')')

        return localscan

def check_mode_of_home_subdirs(verbose=False):
    localscan = {}
    home = UnixFile('/home')

    for subdir in home.subdirs():
        sdname = join('/home', subdir)
        fp = UnixFile(sdname)
        req_mode = '040700'
        match_mode, val_found = fp.check_mode(req_mode)
        if not match_mode:
            message_add(localscan, 'critical',
                fp.name() + ': ' + val_found + ' instead of ' + req_mode)
        elif verbose:
            message_add(localscan, 'info', fp.name())

    return localscan

def check_mounted_filesystems_not_in_fstab(verbose=False):
    localscan = {}
    fstab = UnixFile('/etc/fstab').readlines()

    for line in fstab:
        if line.startswith('#'): continue
        cols = line.split()
        mountpoint = cols[1]
        fstype = cols[2]
        if fstype == 'swap': continue
        checkfs = Filesystem(mountpoint)
        if not checkfs.is_mounted:
            message_add(localscan, 'critical',
                'No such mount point in /etc/fstab: ' + mountpoint)

    return localscan

def check_profiled_permissions(verbose=False):
    localscan = {}
    dp = UnixFile('/etc/profile.d')

    for file in dp.filelist():
        fname = join(dp.name(), file)
        fp = UnixFile(fname)
        match_mode, val_found = fp.check_mode(["100755", "100644"])
        match_perms = fp.check_owner('root') and fp.check_group('root')
        if not (match_mode and match_perms):
            message_add(localscan, 'critical',
                fp.name() + ': ' + quote(fp.owner() + '.' + fp.group()) +
                ' instead of ' + quote('root.root'))

    return localscan

def check_required_filesystems(required_filesystems, verbose=False):
    localscan = {}

    for part in required_filesystems:
        mountpoint = part['mountpoint']
        req_opts = part.get('opts', '')

        fs = Filesystem(mountpoint)
        if not fs.is_mounted:
            message_add(localscan, 'critical',
                mountpoint + ': no such filesystem')
            continue

        (match, opts) = fs.check_mount_opts(req_opts)
        if not match and req_opts:
            message_add(localscan, 'warning',
                mountpoint + ": mount options " +
                quote(opts) + ", required: " + quote(req_opts))
        elif not opts:
            message_add(localscan, 'warning',
                mountpoint + ": no such filesystem")
        elif verbose:
            message_add(localscan, 'info', mountpoint + ' (' + opts + ')')

        return localscan

def check_filesystem(verbose=False):
    fs = Filesystems(verbose=verbose)
    if not fs.enabled:
        if verbose:
            message_add(self.status, 'info',
                'Skipping ' + quote(fs.module_name) +
                ' (disabled in the configuration)')
        return

    scan_result = \
        check_required_filesystems(fs.required_filesystems, verbose=fs.verbose)
    message_add(fs.scan['checks'], 'required filesystems', scan_result)

    scan_result = check_mounted_filesystems_not_in_fstab(verbose=fs.verbose)
    message_add(fs.scan['checks'], 'mounted filesystems not in /etc/fstab',
        scan_result)

    scan_result = \
        check_file_permissions(fs.file_permissions, verbose=fs.verbose)
    message_add(fs.scan['checks'], 
        'permissions of some system folders and files', scan_result)

    scan_result = check_mode_of_home_subdirs(verbose=fs.verbose)
    message_add(fs.scan['checks'], 'mode of the /home subdirs', scan_result)

    scan_result = check_profiled_permissions(verbose=fs.verbose)
    message_add(fs.scan['checks'], 'file permissions in /etc/profile.d',
        scan_result)

    return (fs.scan, fs.status)
