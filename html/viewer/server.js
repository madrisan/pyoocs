// This file is part of the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
var cfg = require('./config');

module.exports = function() {
    var app = express();

    app.use('/scan', require('./routes/scan')());
    app.use(express.static(cfg.publicdir));

    return app;
};
