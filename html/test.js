var assert = require('assert')
  , express = require('express')
  , HTTPStatus = require('http-status')
  , mongoose = require('mongoose')
  , superagent = require('superagent')
  , wagner = require('wagner-core');

/**
 *  This test suite is meant to be run through gulp
 *  (use the `npm run test`) script.
 */

describe('Express Server API', function() {
    var server, port
      , Scan;

    require('./server/models')(wagner);

    before(function() {
        var deps = wagner.invoke(function(Scan) {
            return {
                Scan: Scan
            };
        });

        Scan = deps.Scan;

        var app = require('./server/server')(wagner)

        port = process.env.PORT || 3000;
        server = app.listen(port);
    });

    before(function(done) {
        var scans = [
          {
            "_id" : mongoose.mongo.ObjectID("000000000000000000000001"),
            "hostname" : "__hostname_A",
            "summary" : {
                "criticals" : 4,
                "infos" : 24,
                "max_severity" : "critical",
                "warnings" : 12
            },
            "distribution" : {
                "description" : "openmamba GNU/Linux 3.90.0 for x86_64 (rolling)",
                "vendor" : "openmamba",
                "version" : "3.90.0"
            },
            "modules" : {
                "filesystem" : {
                    "checks" : {
                        "required filesystems" : [{
                            "critical" : [
                                "/var: no such filesystem",
                                "/var/log: no such filesystem"
                            ],
                            "info" : [
                                "/home (rw, nodev, noatime, data=ordered)",
                                "/tmp (rw, nosuid, nodev, noexec, noatime)"
                            ],
                            "warning" : [
                                "/dev/shm: mount options 'rw, nosuid, nodev', required: 'nodev,noexec,nosuid'"
                            ]
                        }]
                    }
                }
            },
            "scan_time" : "2016-04-19T23:27:59.418284"
          },
          {
            "_id" : mongoose.mongo.ObjectID("000000000000000000000002"),
            "hostname" : "__hostname_B",
            "summary" : {
                "criticals" : 0,
                "infos" : 34,
                "max_severity" : "warning",
                "warnings" : 6
            },
            "scan_time" : "2016-04-19T23:26:27.439007"
          }
        ];

        Scan.create(scans, function(error) {
            assert.ifError(error);
            done();
        });
    });

    after(function(done) {
        // Make sure the new scan objects are removed at the end of the test
        Scan.remove({
            hostname: { $in: ['__hostname_A', '__hostname_B'] } 
        }, function(error) {
            assert.ifError(error);
            done();
        });

        // Shut the server down when we're done
        server.close();
    });

    it('can query the MongoDB collection oocs.scan', function(done) {
        Scan.find({ hostname: '__hostname_A' }, function(error, doc) {
            assert.ifError(error);
        });

        done();
    });

    it('can load and parse the page /scan', function(done) {
        var url = 'http://localhost:' + port + '/scan';

        superagent.get(url, function(error, res) {
            assert.ifError(error);
            assert.equal(res.status, HTTPStatus.OK);

            var scans = JSON.parse(res.text)

            assert.equal(scans[0].hostname, '__hostname_A');
            assert.equal(scans[0].max_severity, 'critical');
            assert.equal(scans[0].urlid, '000000000000000000000001');

            assert.equal(scans[1].hostname, '__hostname_B');
            assert.equal(scans[1].max_severity, 'warning');
            assert.equal(scans[1].urlid, '000000000000000000000002');

            done();
        });
    });

    it('can load and parse a scan detail', function(done) {
        var url =
            'http://localhost:' + port + '/scan/000000000000000000000001';

        superagent.get(url, function(error, res) {
            assert.ifError(error);
            assert.equal(res.status, HTTPStatus.OK);

            var detail = JSON.parse(res.text)

            assert.equal(detail.summary.infos, 24);
            assert.equal(detail.summary.warnings, 12);
            assert.equal(detail.summary.criticals, 4);
            assert.equal(detail.scan_time, '2016-04-19T23:27:59.418Z');
            assert.equal(detail.distribution.description,
                         'openmamba GNU/Linux 3.90.0 for x86_64 (rolling)');
            assert.equal(detail.modules.filesystem.
                         checks['required filesystems'][0].critical[0],
                         '/var: no such filesystem');

            done();
        });
    });
});
