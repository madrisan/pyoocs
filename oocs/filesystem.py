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
from oocs.output import message, message_alert, message_ok, quote, unlist
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

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)

        self.procfilesystem = self.cfg.get('procfilesystem', '/proc')

        self.mandatory = self.cfg.get('mandatory', {})
        if not self.mandatory:
            message_alert(self.module +
                ':mandatory not found in the configuration file',
                level='warning')

        self.file_permission = self.cfg.get('file-permission', {})
        if not self.file_permission:
            message_alert(self.module +
                ':file-permission not found in the configuration file',
                level='warning')

        self.proc_mountsfile = join(self.procfilesystem, 'mounts')

    def configuration(self): return self.cfg
    def enabled(self): return self.enabled
    def module_name(self): return self.module

    def procfilesystem(self): return self.procfilesystem

    def cfg_file_permissions(self): return self.file_permission
    def cfg_mandatory_filesystems(self): return self.mandatory

    def dump_proc_mounts(self):
        input = UnixFile(self.proc_mountsfile)
        return input.readlines() or []

class Filesystem(Filesystems):
    def __init__(self, mountpoint):
        Filesystems.__init__(self)
        self.mountpoint = mountpoint

        self.filesystems = self.dump_proc_mounts()
        self.mounted, self.fstype, self.mount_opts = self._is_mounted()

    def _is_mounted(self):
        """ Return the tuple (True, list-of-mount-options) or (False, None) """
        self.filesystems = self.dump_proc_mounts()
        for line in self.filesystems:
            cols = line.split()
            if self.mountpoint == cols[1]:
                return (True, cols[2], cols[3].split(','))
        return (False, None, None)

    def fstype(self):
        """ Return the filesystem type """
        return self.fstype

    def mount_opts(self):
        """ Return the list of the mount options """
        return self.mount_opts

    def is_mounted(self):
        """ Return True if mounted otherwise False """
        return self.mounted

    def check_mount_opts(self, req_opts):
        if not self.mounted:
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
            #self.mode = oct(os.stat(filename)[stat.ST_MODE])
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

def check_file_permissions(file_permission, verbose=False):
    for file in sorted(file_permission.keys()):
        values = file_permission[file]
        req_owner = values[0]
        req_group = values[1]
        # multiple different modes are allowed
        req_modes = values[2].split('|')

        fp = UnixFile(file)
        match_mode, val_found = fp.check_mode(req_modes)
        if not val_found:
            message_alert(fp.name(), reason='no such file or directory',
                          level='warning')
            continue
        try:
            match_perms = (
            fp.check_owner(req_owner) and fp.check_group(req_group))
        except:
            message_alert(fp.name(), reason='no such user or group ' +
                          quote(req_owner + ':' + req_group),
                          level='warning')
            match_perms = False
        if not (match_mode and match_perms):
            message_alert(fp.name(), reason='invalid permissions, ' +
                          'should be: ' + req_owner + ':' + req_group +
                          ' ' + unlist(req_modes, sep=' or '),
                          level='critical')
        elif verbose:
            message_ok(fp.name())

def check_mandatory_filesystems(mandatory_filesystems, verbose=False):
    for part in mandatory_filesystems:
        mountpoint = part['mountpoint']
        req_opts = part.get('opts', '')

        fs = Filesystem(mountpoint)
        if not fs.is_mounted():
            message_alert(mountpoint + ": no such filesystem",
                          level="critical")
            continue

        (match, opts) = fs.check_mount_opts(req_opts)
        if not match and req_opts:
            message_alert(mountpoint + ": mount options " +
                          quote(opts) + ", required: " + quote(req_opts))
        elif not opts:
            message_alert(mountpoint + ": no such filesystem")
        elif verbose:
            message_ok(mountpoint + ' (' + opts + ')')

def check_filesystem(verbose=False):
    fs = Filesystems(verbose=verbose)
    if not fs.enabled:
        if verbose:
            message_alert('Skipping ' + quote(fs.module_name()) +
                          ' (disabled in the configuration)', level='note')
        return

    message('Checking for mandatory filesystems', header=True, dots=True)
    check_mandatory_filesystems(fs.cfg_mandatory_filesystems(), verbose=verbose)

    message('Checking for mounted filesystems not in /etc/fstab',
             header=True, dots=True)
    fstab = UnixFile('/etc/fstab').readlines()
    for line in fstab:
        if line.startswith('#'): continue
        cols = line.split()
        mountpoint = cols[1]
        fstype = cols[2]
        if fstype == 'swap': continue
        checkfs = Filesystem(mountpoint)
        if not checkfs.is_mounted():
            message_alert('No such mount point in /etc/fstab: '+ mountpoint)

    message('Checking the permissions of some system folders and files',
            header=True, dots=True)
    check_file_permissions(fs.cfg_file_permissions(), verbose=verbose)

    message("Checking the mode of the /home subdirs", header=True, dots=True)
    home = UnixFile('/home')
    for subdir in home.subdirs():
        sdname = join('/home', subdir)
        fp = UnixFile(sdname)
        req_mode = '040700'
        match_mode, val_found = fp.check_mode(req_mode)
        if not match_mode:
            message_alert(fp.name(),
                          reason=val_found + ' instead of ' + req_mode,
                          level='warning')
        elif verbose:
            message_ok(fp.name())

    message('Checking for file permissions in /etc/profile.d',
            header=True, dots=True)
    dp = UnixFile('/etc/profile.d')
    for file in dp.filelist():
        fname = join(dp.name(), file)
        fp = UnixFile(fname)
        match_mode, val_found = fp.check_mode(["100755", "100644"])
        match_perms = fp.check_owner('root') and fp.check_group('root')
        if not (match_mode and match_perms):
            message_alert(fp.name(),
                reason = quote(fp.owner() + '.' + fp.group()) +
                ' instead of ' + quote('root.root'), level='critical')

