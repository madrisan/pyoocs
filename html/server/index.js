#!/usr/bin/env node

// HTML viewer for the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
  , wagner = require('wagner-core');

require('./models')(wagner);

var server = require('./server')(wagner, 'dev')
  , port = process.env.PORT || 8080;

wagner.invoke(require('./auth'), { app: server });

server.listen(port, function() {
    console.log('OOCS server listening on port %s.', port);
});
