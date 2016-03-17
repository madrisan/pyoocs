#!/usr/bin/env node

// HTML viewer for the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
  , app = express()
  , path = require('path')
  , fs = require('fs')
  , url = require('url');

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

var jsonFiles = [];
var scanFiles = fs.readdirSync(argv.scandir);

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

app.use('/scan', require('./routes/scan')(argv.scandir, jsonFiles));
app.use(express.static(argv.publicdir));

var urlTokens = url.parse(argv.baseurl);
var uri = {
    hostname: urlTokens.hostname,
    port: urlTokens.port
};

var server = app.listen(uri.port, uri.hostname, function() {
    console.log('Server running at http://%s:%s/',
                server.address().address, server.address().port);
});
