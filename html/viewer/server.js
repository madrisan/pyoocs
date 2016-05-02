// This file is part of the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
  , path = require('path')
  , favicon = require('serve-favicon');

module.exports = function() {
    var app = express();

    app.use(favicon(path.join(__dirname, '../server/public/images', 'favicon.ico')));
    app.use('/scan', require('./routes/scan')());
    app.use(express.static(path.join(__dirname, '../server/public')));

    return app;
};
