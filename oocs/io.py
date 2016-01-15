# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015,2016 Davide Madrisan <davide.madrisan.gmail.com>

from os import chdir, path

from oocs.py2x3 import iteritems, json, urlparse

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

    hostname = socket.gethostname()

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

    hostname = socket.gethostname()
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

    modules_branch = json['scan'][hostname]['modules']

    max_severity = 'success'

    for scan in scan_result:
        module_name = scan.pop('module', None)
        checks = scan.pop('checks', None)
        status = scan.pop('status', None)

        modules_branch[module_name] = dict()
        modules_branch[module_name]['checks'] = checks
        modules_branch[module_name]['status'] = status

        if max_severity == 'critical': continue

        for check, messages in iteritems(checks):
            severities = messages[0].keys()
            if 'critical' in severities:
                max_severity = 'critical'
                break
            elif 'warning' in severities:
                max_severity = 'warning'

    json['scan'][hostname]['max_severity'] = [ max_severity ]

    return json

def _output_json(scan_result):
    "Scan output in json format"

    jsondata = _create_json(scan_result)
    writeln(json.dumps(jsondata,
                       sort_keys=True, indent=2, separators=(',', ': ')))

def simple_http_server(baseurl, publicdir, jsondata):
    "Start a simple HTTP server"

    from oocs.py2x3 import HTTPServer, SocketServer

    class JSONRequestHandler(HTTPServer.SimpleHTTPRequestHandler):
        def end_headers (self):
            self.send_header('Access-Control-Allow-Origin', '*')
            HTTPServer.SimpleHTTPRequestHandler.end_headers(self)
        def do_GET(self):
            """Serve a GET request."""
            if self.path == "/scan" or self.path == '/scan/':
                self.send_response(200)  # OK
                self.send_header("Content-type:", "text/html")
                self.end_headers()
                # send response:
                try:
                    json.dump(jsondata['scan'], self.wfile)
                except:
                    die(2, 'runtime error while getting jsondata[\'scan\']')
            else:
                return HTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    try:
        chdir(publicdir)
    except:
        die(2, "cannot access to the HTML root directory " + publicdir)

    url = urlparse(baseurl)

    try:
        httpd = SocketServer.TCPServer(('localhost', url.port), JSONRequestHandler)
    except:
        die(2, "cannot open a TCP socket on port " + str(url.port))

    writeln('The Simple HTTP Server is running...\n\n' +
            'Resources\nhttp://localhost:%d/scan\n\n' % url.port +
            'Home\nhttp://localhost:%d\n' % url.port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        writeln('\nShutting down the http server...')
        httpd.server_close()

def _output_html(scan_result, publicdir, baseurl):
    "Scan output in html format"

    jsondata = _create_json(scan_result);
    simple_http_server(baseurl, publicdir, jsondata)

def output_dump(scan):
    cfg = Config()
    html_opts = {}

    try:
        output_type = cfg.variable('oocs-output')
    except KeyError:
        die(quote('oocs-output') + ' unset in the configuration file')

    if output_type == 'console':
        _output_console(scan)
    elif output_type == 'html':
        try:
             html_opts = cfg.variable('oocs-html-opts')
             baseurl = html_opts["baseUrl"]
             publicdir = html_opts["publicDir"]
        except:
             die(1, quote('oocs-html-opts') +
                  ' must provide both baseUrl and publicDir')
        _output_html(scan, publicdir, baseurl)
    elif output_type == 'json':
        _output_json(scan)
    else:
        die(1, 'unsupported output (see configuration file): '
            + quote(output_type))
