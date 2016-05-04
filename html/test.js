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

        port = process.env.PORT || 8080;
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
            }
          },
          {
            "_id" : mongoose.mongo.ObjectID("000000000000000000000002"),
            "hostname" : "__hostname_B",
            "summary" : {
                "criticals" : 0,
                "infos" : 34,
                "max_severity" : "warning",
                "warnings" : 6
            }
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

    it('can parse a scan list', function(done) {
        var url = 'http://localhost:' + port + '/scan';

        superagent.get(url, function(error, res) {
            assert.ifError(error);
            assert.equal(res.status, HTTPStatus.OK);

            var scans = JSON.parse(res.text)
            //console.log(scans);

            // assert.equal(scans.length, 2);
            assert.equal(scans[0].hostname, '__hostname_A');
            assert.equal(scans[0].max_severity, 'critical');
            assert.equal(scans[1].hostname, '__hostname_B');
            assert.equal(scans[1].max_severity, 'warning');
            done();
        });
    });
});
