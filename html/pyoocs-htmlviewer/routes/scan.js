var express = require('express')
  , bodyParser = require('body-parser')
  , path = require('path')
  , fs = require('fs');

module.exports = function(scandir, jsonFiles) {
    var api = express.Router();

    api.use(bodyParser.json());

    api.route('/')
        .all(function(req, res, next) {
            res.writeHead(200, { 'Content-Type': 'text/json' });
            next();
        })
        .get(function(req, res, next) {
            var jsonHeader = [];

            for (var i in jsonFiles) {
                try {
                    var jsonFile = path.join(scandir, jsonFiles[i]);
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

    api.route('/:scanId')
        .get(function(req, res, next) {
            if (req.params.scanId > jsonFiles.length) {
                res.writeHead(404, { 'Content-Type': 'text/html' });
                res.end('<h1>404 Not Found - Scan ID out of bound</h1>');
            }
            else {
                var jsonFile = path.join(scandir, jsonFiles[req.params.scanId]);

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

    return api;
};
