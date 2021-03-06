# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

# Simple parser for sudo configuration files
# Some ideas came from: http://www.planetjoel.com/files/test-sudoers.txt

from os import listdir, geteuid
from os.path import isfile, join
from sys import stdout

from oocs.filesystem import UnixFile, UnixCommand
from oocs.io import Config, die, message_add, quote
from oocs.py2x3 import Scanner

class SudoParser(object):

    module_name = 'sudo'

    def __init__(self, verbose=False):
        self.verbose = verbose

        self.scan = {
            'module' : self.module_name,
            'checks' : {},
            'status' : {}
        }

        try:
            self.cfg = Config().module(self.module_name)
        except KeyError:
            message_add(self.scan['status'], 'warning',
                self.module_name +
                 ' directive not found in the configuration file')
            self.cfg = {}

        self.enabled = (self.cfg.get('enable', 1) == 1)
        self.verbose = (self.cfg.get('verbose', verbose) == 1)

        self.mainfile = self.cfg.get("conf-mainfile", "/etc/sudoers")
        if not UnixFile(self.mainfile).isfile():
            die(2, 'No such file: ' + self.mainfile)

        self.modulesdir = self.cfg.get("conf-modulesdir", None)
        if self.modulesdir and not UnixFile(self.modulesdir).isdir():
            message_add(self.scan['status'], 'warning',
                'no such directory: ' + self.modulesdir)
            self.modulesdir = None

        self.modules = []
        try:
            if self.modulesdir:
                self.modules = [
                    join(self.modulesdir, f) for f in listdir(self.modulesdir)
                        if isfile(join(self.modulesdir, f)) ]
        except:
            pass

        self.lines = []
        self.tokens = []
        self.currline = None

        self.cmnd_aliases = {}
        self.user_aliases = {}
        self.group_specs = {}
        self.user_specs = {}

        self.user_exclude_list = self.cfg.get("excluded-users", [])

        self._parse()

    def _collapse_lines(self):
        collapsed = []
        currentline = ""
        for line in self.lines:
            if(line.rstrip()[-1:] == "\\"):
                currentline += line.rstrip()[:-1]
            else:
                currentline += line
                collapsed.append(currentline)
                currentline = ""

        return collapsed

    def _read_files(self):
        self.lines = []

        try:
            for f in [ self.mainfile ] + self.modules:
                for line in open(f, 'r'):
                    stripped_line = line.strip().replace('\n', '')
                    if stripped_line and not stripped_line.startswith("#"):
                        self.lines.append(stripped_line)

            self.lines = self._collapse_lines()
        except:
            pass

    def _tokenize(self, line):
        #print("line: " + line)
        scanner = Scanner([
            # reserved words
            (r"Cmnd_Alias",  lambda scanner,token:("TOK_CMND_ALIAS", token)),
            (r"Host_Alias",  lambda scanner,token:("TOK_HOST_ALIAS", token)),
            (r"Runas_Alias", lambda scanner,token:("TOK_RUNAS_ALIAS", token)),
            (r"User_Alias",  lambda scanner,token:("TOK_USER_ALIAS", token)),
            (r"Defaults",    lambda scanner,token:("TOK_DEFAULTS", token)),
            (r"ALL"     ,    lambda scanner,token:("TOK_ALL", token)),
            (r"NOPASSWD",    lambda scanner,token:("TOK_NOPASSWD", token)),
            (r"PASSWD",      lambda scanner,token:("TOK_PASSWD", token)),
            (r"\d{1,3}(\.\d{1,3}){3}/\d{1,3}(\.\d{1,3}){3}",
                             lambda scanner,token:("TOK_IP_NET", token)),
            (r"\d{1,3}(\.\d{1,3}){3}",
                             lambda scanner,token:("TOK_IP_ADDR", token)),
            (r"[0-9]+",      lambda scanner,token:("TOK_INTEGER", token)),
            (r"[A-Za-z_]+\w*",
                             lambda scanner,token:("TOK_IDENTIFIER", token)),
            (r"[A-Za-z_/]+[A-Za-z_0-9/\-\[\]*. ]*",
                             lambda scanner,token:("TOK_COMMAND", token)),
            (r"#[0-9]+",     lambda scanner,token:("TOK_UID", token)),
            (r"%[A-Za-z]+[A-Za-z0-9]*",
                             lambda scanner,token:("TOK_GROUP", token)),
            (r"%#[0-9]+",    lambda scanner,token:("TOK_GID", token)),
             # NOTE: we ignore +netgroup, %:nonunix_group, %:#nonunix_gid
             #       see sudoers manpage
            (r':',           lambda scanner,token:("TOK_COLON", token)),
            (r',',           lambda scanner,token:("TOK_COMMA", token)),
            (r'=',           lambda scanner,token:("TOK_EQUAL", token)),
            (r'!',           lambda scanner,token:("TOK_NEGATE", token)),
            (r'\(',          lambda scanner,token:("TOK_BBLOCK", token)),
            (r'\)',          lambda scanner,token:("TOK_EBLOCK", token)),
            (r"\s+",         None),  # skip token
        ])
        results, remainder = scanner.scan(line)
        return results

    def _token_get(self):
        return self.tokens[0]

    def _token_pop(self):
        return self.tokens.pop(0)

    def _token_push(self, id, value):
        self.tokens = [ (id, value) ] + self.tokens

    def _token_match(self, rule, optional=False):
        if rule == "Alias_List":
            # Alias_Type NAME = item1, item2, ...
            (token, alias) = self._token_pop()
            self._token_match("TOK_EQUAL")
            aliases = {}
            aliases[alias] = [
                val for (id, val) in self.tokens if id != "TOK_COMMA" ]
            return aliases
        elif rule == "TOK_HOST":
            (token, value) = self._token_pop()
            if token == "TOK_IP_ADDR" or token == "TOK_IP_NET" or \
               token == "TOK_IDENTIFIER" or token == "TOK_ALL":
                return (token, value)
        elif rule in ["TOK_BBLOCK", "TOK_COLON", "TOK_EBLOCK", "TOK_EQUAL"]:
            (token, value) = self._token_pop()
            if token == rule:
                return (token, value)

        if optional == False:
            (curr_token, curr_value) = self._token_get()
            raise SyntaxError("Unexpected token " + curr_token +
                              " while looking for " + rule + '\n' +
                              "Current line: " + self.currline)
        return (None, None)

    def _parse_cmnd_list(self):
        cmnd_list = [
            val for (tok, val) in self.tokens if tok != "TOK_COMMA" ]
        return cmnd_list

    def _parse_groups(self, group):
        groups = {}
        (token, value) = self._token_match("TOK_HOST")
        self._token_match("TOK_EQUAL")
        runas_list = self._parse_runas_specs()
        tag_specs  = self._parse_tag_specs()
        cmnd_list  = self._parse_cmnd_list()
        groups[group] = { "cmnd": cmnd_list, "runas": runas_list }
        return groups

    def _parse_users(self, first_user):
        users = {}
        ids = [ first_user ]

        (token, value) = self._token_pop()
        # list of users
        # ex: N2,N3 ALL=(root) NOPASSWD: /bin/su
        while token == "TOK_COMMA":
            (token, value) = self._token_pop()
            ids.append(value)
            (token, value) = self._token_pop()

        self._token_push(token, value)

        (token, value) = self._token_match("TOK_HOST")
        self._token_match("TOK_EQUAL")
        runas_list = self._parse_runas_specs()
        tag_specs  = self._parse_tag_specs()
        cmnd_list  = self._parse_cmnd_list()

        for user in ids:
            users[user] = { "cmnd": cmnd_list, "runas": runas_list }
        return users

    def _parse_runas_specs(self):
        (token, value) = self._token_get()
        if token == "TOK_BBLOCK":
            runas_list = []
            self._token_pop()  # discard TOK_BBLOCK
            (token, value) = self._token_pop()
            while token != "TOK_EBLOCK":
                if token != "TOK_COMMA":
                   runas_list.append(value)
                (token, value) = self._token_pop()
            return runas_list
        return ["root"]  # implicit Runas_List is 'root'

    def _parse_tag_specs(self):
        (token, value) = self._token_pop()
        # Note: Tag_Spec can also be [NO]{EXEC,SETENV,LOG_{INPUT,OUTPUT}}
        if token in ["TOK_NOPASSWD", "TOK_PASSWD"]:
            self._token_match("TOK_COLON")
            return (token, value)
        else:
            self._token_push(token, value)
        
    def _printcfg(self):
        """ Print the whole sudo configuration files (for debug only)"""
        self._read_files()
        stdout.write('[sudo configuration]\n')
        for line in self.lines: stdout.write(line + '\n')

    def _parse(self):
        self._read_files()
        #self._printcfg()

        for line in self.lines:
            self.currline = line
            self.tokens = self._tokenize(line)
            #stdout.write('DEBUG: LINE: ' + str(line) + '\n')
            #stdout.write('DEBUG:   --> ' + str(self.tokens) + '\n')
            (token, value) = self._token_pop()
            if token == "TOK_CMND_ALIAS":
                aliases = self._token_match("Alias_List")
                self.cmnd_aliases.update(aliases)
            elif token == "TOK_USER_ALIAS":
                aliases = self._token_match("Alias_List")
                self.user_aliases.update(aliases)
            elif token == "TOK_GROUP":
                self.group_specs.update(self._parse_groups(value))
            elif token == "TOK_IDENTIFIER":
                self.user_specs.update(self._parse_users(value))
            else:
                pass   # ignore the other directives

    def _expand_cmnd(self, cmnd_list):
        expanded_list = []
        for cmnd in cmnd_list:
            if cmnd in self.cmnd_aliases:
                for c in self.cmnd_aliases[cmnd]: expanded_list.append(c)
            else:
                expanded_list.append(cmnd)
        # remove duplicates
        return list(set(expanded_list))

    def _expand_user(self, user):
        expanded_list = []
        if user in self.user_aliases:
            not_excluded = [
                usr for usr in self.user_aliases[user]
                    if usr not in self.user_exclude_list ]
            for usr in not_excluded: expanded_list.append(usr)
        elif user not in self.user_exclude_list:
            expanded_list.append(user)
        return list(set(expanded_list))  

    def _expand_users(self):
        expanded_list = []
        for user in self.user_specs:
            expanded_list.append(_expand_user(user))
        return list(set(expanded_list))

    def configuration(self): return self.cfg
    def enabled(self): return self.enabled

    def catch_root_escalation(self):
        exclude_list = self.user_exclude_list

        cmnd_warning = {}   # commands that may lead to root escalation
        cmnd_normal = {}
        super_users = []

        for user in self.user_specs:
            real_users_list = self._expand_user(user)
            runas_list = self.user_specs[user]['runas']   # FIXME: unused value!

            for cmnd in self.user_specs[user]['cmnd']:
                owned_by_root = False

                if cmnd != 'ALL':
                    cmnd_file = UnixCommand(cmnd)
                    su_command = cmnd_file.command_su_root()
                    owned_by_root = cmnd_file.owned_by_root()
                else:
                    su_command = True

                if type(real_users_list) == list:
                    for usr in real_users_list:
                        if su_command: super_users.append(usr)
                        if not owned_by_root:
                            cmnd_warning.setdefault(usr,[]).append(cmnd)
                        else:
                            cmnd_normal.setdefault(usr,[]).append(cmnd)
                else:
                    if su_command: super_users.append(real_users_list)
                    if not owned_by_root:
                        cmnd_warning.setdefault(real_users_list,[]).append(cmnd)
                    else:
                        cmnd_normal.setdefault(real_users_list,[]).append(cmnd)

        for group in self.group_specs:
            owned_by_root = False
            runas_list = self.group_specs[group]['runas']

            for cmnd in self._expand_cmnd(self.group_specs[group]['cmnd']):
                if cmnd != 'ALL':
                    cmnd_file = UnixCommand(cmnd)
                    su_command = cmnd_file.command_su_root()
                    if cmnd_file.owned_by_root():
                        cmnd_normal.setdefault(group,[]).append(cmnd)
                        continue
                    if 'ALL' in runas_list or 'root' in runas_list:
                        cmnd_warning.setdefault(group,[]).append(cmnd)
                    else:
                        cmnd_normal.setdefault(group,[]).append(cmnd)
                else:
                    if 'ALL' in runas_list or 'root' in runas_list:
                        su_command = True

            if su_command: super_users.append(group)

        return (list(set(super_users)), cmnd_warning, cmnd_normal)


def check_sudo(verbose=False):
    sudocfg = SudoParser(verbose=verbose)
    localscan = {}

    if not sudocfg.enabled:
        if verbose:
            message_add(sudocfg.scan['status'], 'info',
                'Skipping ' + quote(sudocfg.module_name) +
                ' (disabled in the configuration)')
        return {}

    if geteuid() != 0:
        message_add(sudocfg.scan['status'], 'warning',
            'This check (' + __name__ + ') must be run as root' + ' ... skip')
        return {}

    (super_users, cmnd_warning, cmnd_normal) = sudocfg.catch_root_escalation()

    if verbose:
        for usr in sudocfg.user_exclude_list:
            message_add(localscan, 'info',
                'ignoring user/group ' + quote(usr) + ' (see configuration)')

    #stdout.write("\n[CMND_ALIAS]\n" + str(sudocfg.cmnd_aliases()) + '\n')
    #stdout.write("\n[USER_ALIAS]\n" + str(sudocfg.user_aliases()) + '\n')
    #stdout.write("\n[GROUPS]\n"     + str(sudocfg.group_specs()) + '\n')
    #stdout.write("\n[USERS]\n"      + str(sudocfg.user_specs()) + '\n\n')

    for usr in super_users:
        message_add(localscan, 'critical',
            quote(usr) + ' can become super user')

    for key in sorted(cmnd_warning.keys()):
        message_add(localscan, 'critical',
            'to be checked: ' + quote(key) + ' can execute ' +
            str(cmnd_warning[key]))

    if verbose:
        for key in sorted(cmnd_normal.keys()):
            message_add(localscan, 'info',
                quote(key) + ' can run ' + str(cmnd_normal[key]))

    message_add(sudocfg.scan['checks'], 'sudo configuration', localscan)

    return sudocfg.scan
