var express = require('express')
  , assert = require('assert')
  , bodyParser = require('body-parser')
  , path = require('path')
  , HTTPStatus = require('http-status')
  , ObjectID = require('mongodb').ObjectID;

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

            collection.find({}, query).toArray(function(error, docs) {
                if (error) {
                     return res.
                         status(HTTPStatus.INTERNAL_SERVER_ERROR).
                         json({ error: error.toString() });
                }
                docs.forEach(function(doc) {
                    //console.log(doc.hostname);
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
            //console.log('req.params.id: ' + req.params.id);

            var collection = db.get().collection('scan');
            try {
                query = { _id: ObjectID(req.params.id) };
            }
            catch(error) {
                return res.
                    status(HTTPStatus.INTERNAL_SERVER_ERROR).
                    json({ error: error.message });
            }

            collection.findOne(query, function(error, doc) {
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
        });

    return api;
};
