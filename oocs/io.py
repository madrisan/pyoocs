# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

from os import chdir, path

from oocs.py2x3 import json

class Config(object):
    def __init__(self):
        self.configfile = 'oocs-cfg.json'
        if not path.isfile(self.configfile):
            die(1, "Configuration file not found: " + self.configfile)

    def _read(self):
        cfgfile = open(self.configfile, 'r')
        try:
            data = json.load(cfgfile)
            cfgfile.close();
        except IOError:
            die(1, 'I/O error while opening ' + self.configfile)
        except ValueError:
            die(1, 'Invalid json file: ' + self.configfile)

        return data

    def variable(self, var):
        data = self._read()
        return data.get(var)

    def module(self, module):
        data = self._read()
        #return data.get("oocs-module", {}).get(module, {})
        return data.get('oocs-module', {})[module]

# Simple output primitives

import sys

def colonize(message):
    #return ": %s" % message if message else ''
    if not message: return ''
    return ": %s" % message

def die(exitcode, message):
    "Print error and exit with errorcode"
    sys.stderr.write('pyoocs: Fatal error: %s\n' % message)
    sys.exit(exitcode)

def quote(message):
    return "'%s'" % message

def unlist(list, sep=', '):
    return sep.join(map(str, list))

def writeln(line):
    sys.stdout.write(line + '\n')

def message_add(d, key, message):
    "Add the message 'message' to the key 'key' of the dictionary 'd'"
    if not key in d:
        d[key] = [message]
    else:
        d[key].append(message)

import socket

def _output_console(scan_result):
    "Scan with output sent to the console"
    hostname = socket.getfqdn()

    for scan in scan_result:
        "Display on the console the scan and status messages"
        writeln('\n# host:' + hostname + ' module:' + scan['module'])

        for severity in scan.get('status', []):
            for message in scan['status'].get(severity, []):
                writeln(severity.upper() + ': ' + message)

        for line in scan.get('infos', []): writeln('(i) ' + line)

        checks = scan['checks']
        for check in checks:
            writeln('[' + check + ']')
            for scan_block in checks[check]:
                for entry in scan_block.get('critical', []):
                    writeln('(c) ' + entry)
                for entry in scan_block.get('warning', []):
                    writeln('(w) ' + entry)
                for entry in scan_block.get('info', []):
                    writeln('(i) ' + entry)

def _create_json(scan_result):
    from oocs.distribution import Distribution
    distro = Distribution()

    hostname = socket.getfqdn()
    json = {
        'scan' : {
            hostname : {
                'distribution' : {
                    'codename'      : distro.codename,
                    'description'   : distro.description,
                    'majversion'    : distro.majversion,
                    'patch_release' : distro.patch_release,
                    'vendor'        : distro.vendor,
                    'version'       : distro.version
                },
                'modules' : {}
            }
        }
    }

    modules_branch = json['scan'][hostname]['modules'];

    for scan in scan_result:
        module_name = scan.pop('module', None)
        checks = scan.pop('checks', None)
        status = scan.pop('status', None)

        modules_branch[module_name] = dict()
        modules_branch[module_name]['checks'] = checks
        modules_branch[module_name]['status'] = status

    return json

def _output_json(scan_result):
    "Scan output in json format"

    jsondata = _create_json(scan_result)
    writeln(json.dumps(jsondata,
                       sort_keys=True, indent=2, separators=(',', ': ')))

def _output_html(scan_result, home, port):
    "Scan output in html format"

    jsondata = _create_json(scan_result);
    chdir(home)

    # start a simple HTTP server
    import SimpleHTTPServer
    import SocketServer

    class JSONRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def do_GET(self):
            """Serve a GET request."""

            if self.path == "/scan" or self.path == '/scan/':
                self.send_response(200)  # OK
                self.send_header("Content-type:", "text/html")
                self.end_headers()
                # send response:
                json.dump(jsondata, self.wfile)
            else:
                return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    httpd = SocketServer.TCPServer(('', port), JSONRequestHandler)
    writeln('http server is running...\nhttp://localhost:%d' % port)
    httpd.serve_forever()

def output_dump(scan):
    cfg = Config()
    try:
        otype = cfg.variable('oocs-output')
    except KeyError:
        die(quote('oocs-output') + ' unset in the configuration file')

    if otype == 'console':
        _output_console(scan)
    elif otype == 'html':
        # FIXME: path and 8000 should not be hardcoded
        _output_html(scan, 'html/json-server/public/', 8000)
    elif otype == 'json':
        _output_json(scan)
    else:
        die(1, 'unsupported output (see configuration file): ' + quote(otype))
