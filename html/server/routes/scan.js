var express = require('express')
  , assert = require('assert')
  , bodyParser = require('body-parser')
  , path = require('path')
  , HTTPStatus = require('http-status')
  , mongoose = require('mongoose');

module.exports = function(wagner) {
    var api = express.Router();

    api.route('/')
        .get(wagner.invoke(function(Scan) {
            return function(req, res) {
                var jsonHeader = []
                  , query = { hostname: 1, summary: 1 };

                Scan.
                    find({}, query).
                    sort({ hostname: 1 }).
                    exec(function(error, docs) {
                        if (error) {
                            return res.
                                status(HTTPStatus.INTERNAL_SERVER_ERROR).
                                json({ error: error.toString() });
                        }
                        docs.forEach(function(doc) {
                            //console.log('doc.hostname: ' + doc.hostname);
                            //console.log('doc._id: ' + doc._id);
                            //console.log('doc.summary: ' + doc.summary);

                            jsonHeader.push({
                                'hostname': doc.hostname,
                                'urlid': doc._id,
                                'max_severity': doc.summary.max_severity || 'unknown'
                            });
                        });
                        res.json(jsonHeader);
                    });
            };
        }));

    api.route('/:id')
        .get(wagner.invoke(function(Scan) {
            return function(req, res) {
                //console.log('req.params.id: ' + req.params.id);
                try {
                    query = { _id: mongoose.mongo.ObjectID(req.params.id) };
                }
                catch(error) {
                    return res.
                        status(HTTPStatus.INTERNAL_SERVER_ERROR).
                        json({ error: error.message });
                }

                Scan.findOne(query, function(error, doc) {
                    assert.equal(error, null, 'mongodb findOne() error');
                    if (doc) {
                        res.json(doc);
                        //console.log('returned doc: ' + JSON.stringify(doc));
                    }
                    else {
                         return res.
                             status(HTTPStatus.NOT_FOUND).
                             json({ error: 'No such document ' + req.params.id });
                    }
                });
            }
        }));

    return api;
};
