var express = require('express')
  , assert = require('assert')
  , bodyParser = require('body-parser')
  , path = require('path')
  , HTTPStatus = require('http-status');

var db = require('../db');

module.exports = function() {
    var api = express.Router();

    api.use(bodyParser.json());

    api.route('/')
        .get(function(req, res, next) {
            var jsonHeader = []
              , collection = db.get().collection('scan')
              , query = { hostname: 1, summary: 1 };

            assert(collection, 'collection is null');
            collection.find({}, query).toArray(function(err, docs) {
                assert.equal(err, null, 'mongodb find() error');
                docs.forEach(function(doc) {
                    console.log(doc.hostname);
                    jsonHeader.push({
                        'hostname': doc.hostname,
                        'urlid': doc._id,
                        'max_severity': doc.summary.max_severity || 'unknown'
                    });
                });

                res.json(jsonHeader);
            });
        });

    api.route('/:id')
        .get(function(req, res, next) {
            var collection = db.get().collection('scan')
              , query = { _id: req.params.id };

            collection.findOne(query, function(err, doc) {
                assert.equal(err, null, 'mongodb findOne() error');
                if (doc) {
                    console.log(JSON.stringify(doc));
                    res.json(doc);
                }
                else {
                    res.writeHead(HTTPStatus.NOT_FOUND, { 'Content-Type': 'text/html' });
                    res.end('<h1>' + HTTPStatus.NOT_FOUND + ' Not Found - Unknown scan id</h1>');
                }
            });
        });

    return api;
};
