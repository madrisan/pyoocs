#!/usr/bin/env node

// HTML viewer for the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
  , url = require('url')
  , wagner = require('wagner-core');

require('./models')(wagner);

var server = require('./server')(wagner)
  , port = process.env.PORT || 8080;

server.listen(port, function() {
    console.log('OOCS server listening on port %s.', port);
});
