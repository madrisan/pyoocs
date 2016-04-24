#!/usr/bin/env node

// HTML viewer for the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var assert = require('assert')
  , url = require('url');

var cfg = require('./config')
  , db = require('./db')
  , server = require('./server');

db.connect(cfg.mongoUrl, function(err) {
    assert.equal(err, null);

    var urlTokens = url.parse(cfg.baseurl);
    var uri = {
        hostname: urlTokens.hostname,
        port: urlTokens.port
    };

    server().listen(uri.port, uri.hostname, function() {
        console.log('Server running at http://%s:%s/',
                    uri.hostname, uri.port);
    });
});
