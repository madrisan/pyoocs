// This file is part of the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
  , path = require('path')
  , favicon = require('serve-favicon')
  , logger = require('morgan');


module.exports = function(wagner, logFormat = 'dev') {
    var app = express();

    app.use(favicon(path.join(__dirname, '../public/images', 'favicon.ico')));
    if (logFormat) {
        app.use(logger(logFormat));
    };
    app.use('/scan', require('./routes/scan')(wagner));

    app.use(express.static(path.join(__dirname, '../public'),
            { maxAge: 4 * 60 * 60 * 1000 /* 2hrs */ }));

    return app;
};
