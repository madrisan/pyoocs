# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015,2016 Davide Madrisan <davide.madrisan.gmail.com>

from os import chdir, path
import re

from oocs.py2x3 import iteritems, json, urlparse

class Config(object):
    def __init__(self):
        self.configfile = '/etc/oocs-cfg.json'
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
        if not scan: continue

        # Display on the console the scan and status messages
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
    infos = warnings = criticals = 0

    for scan in scan_result:
        module_name = scan.pop('module', None)
        if not module_name: continue

        checks = scan.pop('checks', None)
        status = scan.pop('status', None)

        modules_branch[module_name] = dict()
        modules_branch[module_name]['checks'] = checks
        modules_branch[module_name]['status'] = status

        # set the number of infos, warnings, criticals entries
        for check, messages in iteritems(checks):
            infos += len(messages[0].get('info', []))
            warnings += len(messages[0].get('warning', []))
            criticals += len(messages[0].get('critical', []))

        # check for the max severity
        if max_severity == 'critical': continue

        for check, messages in iteritems(checks):
            severities = messages[0].keys()
            if 'critical' in severities:
                max_severity = 'critical'
                break
            elif 'warning' in severities:
                max_severity = 'warning'

    json['scan'][hostname]['summary'] = {
        "max_severity": max_severity,
        "infos": infos,
        "warnings": warnings,
        "criticals": criticals
    }

    return json

def _output_json(scan_result):
    "Scan output in json format"

    jsondata = _create_json(scan_result)
    writeln(json.dumps(jsondata,
                       sort_keys=True, indent=2, separators=(',', ': ')))

def simple_http_server(baseurl, publicdir, jsondata):
    "Start a simple HTTP server"

    from oocs.py2x3 import SocketServer, WebServer

    class JSONRequestHandler(WebServer.SimpleHTTPRequestHandler):
        def end_headers (self):
            self.send_header('Access-Control-Allow-Origin', '*')
            WebServer.SimpleHTTPRequestHandler.end_headers(self)

        def do_GET(self):
            """Serve a GET request."""

            matchurl = re.match(r'^/scan(/(\d+)){0,1}$', self.path)
            if not matchurl:
                return WebServer.SimpleHTTPRequestHandler.do_GET(self)

            # url: /scan/[0-9]+
            if matchurl.group(2):
                scannum = int(matchurl.group(2))
                if scannum >= len(jsondata):
                    self.send_error(404, 'File not found')
                    return None

                try:
                    jsonstream = \
                        json.dumps(jsondata[scannum]['scan'],
                                   sort_keys=True, separators=(',', ': '))
                except:
                    # runtime error while getting jsondata[scan]
                    self.send_error(500, 'Internal Server Error')
                    return None

            # url: /scan
            else:
                # the /scan page provides the informations about
                # the available scan data (server name + url).
                try:
                    jsonstream = \
                        json.dumps(jsonheader,
                                   sort_keys=True, separators=(',', ': '))
                except:
                    self.send_error(500, 'Internal Server Error')
                    return None

            self.send_response(200)  # OK
            self.send_header("Content-type:", "text/plain")
            self.end_headers()
            self.wfile.write(jsonstream.encode())

    try:
        chdir(publicdir)
    except:
        die(2, "cannot access to the HTML root directory " + publicdir)

    jsonheader = []
    urlnum = 0

    for data in jsondata:
        try:
            # NOTE: we assume that each json file contains the data
            #       of one host only
            currhost = list(data['scan'])[0]
            summary = data['scan'][currhost]['summary']

            # map each host with the corresponding position
            # (and thus url subpage).
            # ie: host#1 --> 0 (--> /scan/0)
            #     host#2 --> 1 (--> /scan/1)
            #     ...
            jsonheader.append({
                'hostname': currhost,
                'urlid': urlnum,
                'max_severity': summary['max_severity']
            })
        except:
            pass

        #from oocs.py2x3 import json
        #writeln('DEBUG: jsonheader:\n' + json.dumps(jsonheader,
        #        sort_keys=True, indent=2, separators=(',', ': ')))

        urlnum += 1

    url = urlparse(baseurl)

    try:
        httpd = SocketServer.TCPServer(('localhost', url.port),
                    JSONRequestHandler)
    except:
        die(2, "cannot open a TCP socket on port " + str(url.port))

    writeln('The Simple HTTP Server is running...\n\n' +
            'Home\nhttp://localhost:%d\n' % url.port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        writeln('\nShutting down the http server...')
        httpd.server_close()

def _output_html(scan_result, publicdir, baseurl):
    "Scan output in html format"

    jsondata = _create_json(scan_result)
    simple_http_server(baseurl, publicdir, [jsondata])

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
