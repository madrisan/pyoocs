#!/usr/bin/env node

// HTML viewer for the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var assert = require('assert')
  , url = require('url');

var database = require('./config/database')
  , db = require('./db')
  , server = require('./server');

var port = process.env.PORT || 8080;

db.connect(database.url, function(err) {
    assert.equal(err, null);

    server().listen(port, function() {
        console.log('OOCS server listening on port %s.', port);
    });
});
