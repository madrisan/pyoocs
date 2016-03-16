#!/usr/bin/env node

// HTML viewer for the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
  , app = express()
  , path = require('path')
  , fs = require('fs')
  , url = require('url')
  , bodyParser = require('body-parser');

var argv = require('yargs')
    .usage('Usage: $0 -u <baseurl> -p <publicdir> -d <json-scan-dir>')
    //.example('$0 -u http://localhost:8000 -p html/server/public/ -d ./jsonfiles/')
    .demand(['u', 'p', 'd'])
    .alias('u', 'baseurl')
    .nargs('u', 1)
    .describe('u', 'Base URL')
    .alias('p', 'publicdir')
    .nargs('p', 1)
    .describe('p', 'Directory public')
    .alias('d', 'scandir')
    .nargs('d', 1)
    .describe('d', 'JSON container directory')
    .help('h')
    .alias('h', 'help')
    .epilog('Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>')
    .argv

var progName = path.basename(__filename);

var checkDir = function(dir) {
    fs.stat(dir, function(err, stats) {
        if (err || !stats.isDirectory())
            return console.error(progName + ': ' + dir);
    })
}

checkDir(argv.publicdir);
checkDir(argv.scandir);

jsonFiles = [];
scanFiles = fs.readdirSync(argv.scandir);
for (var i in scanFiles) {
    var scanFile = path.join(argv.scandir, scanFiles[i]);
    try {
        JSON.parse(fs.readFileSync(scanFile));
        jsonFiles.push(scanFiles[i]);
    }
    catch (err) {
        console.error('skipping ' + scanFile + ': ' + err.message);
    }
}

var scanRouter = express.Router();
scanRouter.use(bodyParser.json());

scanRouter.route('/')
    .all(function(req, res, next) {
        res.writeHead(200, { 'Content-Type': 'text/json' });
        next();
    })
    .get(function(req, res, next) {
        var jsonHeader = [];

        for (var i in jsonFiles) {
            try {
                var jsonFile = path.join(argv.scandir, jsonFiles[i]);
                var jsonObj = JSON.parse(fs.readFileSync(jsonFile));

                var currHost;
                for (var key in jsonObj.scan) {
                    if (jsonObj.scan.hasOwnProperty(key)) {
                        currHost = key;
                        break;
                    }
                }
                //console.log('currHost: ' + currHost);

                var currSummary = jsonObj.scan[currHost]['summary'];
                //console.log('currSummary: ' + JSON.stringify(currSummary));

                if (!currHost || !currSummary) throw new Error();

                jsonHeader.push({
                    'hostname': currHost,
                    'urlid': i,
                    'max_severity': currSummary['max_severity'] || 'unknown'
                });
            }
            catch(err) {
                console.error('Error parsing ' + jsonFiles[i] + ' ... skip');
            }

        }

        res.write(JSON.stringify(jsonHeader));
        //console.log(JSON.stringify(jsonHeader));
        res.end();
    });

scanRouter.route('/:dishId')
    .get(function(req, res, next) {
        if (req.params.dishId > jsonFiles.length) {
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>404 Not Found - Scan ID out of bound</h1>');
        }
        else {
            var jsonFile = path.join(argv.scandir, jsonFiles[req.params.dishId]);

            fs.readFile(jsonFile, function(err, data) {
                if (err) {
                    res.writeHead(500, { 'Content-Type': 'text/html' });
                    res.end('<h1>500 Internal Error - Cannot read JSON file</h1>');
                }
                res.writeHead(200, { 'Content-Type': 'text/json' });
                var jsonObj = JSON.parse(data);
                res.end(JSON.stringify(jsonObj.scan));
            });
        }
    });

app.use('/scan', scanRouter);
app.use(express.static(argv.publicdir));

urlTokens = url.parse(argv.baseurl);
var hostname = urlTokens.hostname,
    port = urlTokens.port;

app.listen(port, hostname, function() {
    console.log('Server running at http://%s:%s/', hostname, port);
});
