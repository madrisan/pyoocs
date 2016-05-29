#!/usr/bin/env node

// HTML viewer for the Out of Compliance Scanner (pyOOCS)
// Copyright (C) 2016 Davide Madrisan <davide.madrisan.gmail.com>

var express = require('express')
  , HTTPStatus = require('http-status')
  , bodyParser = require('body-parser')
  , cookieParser = require('cookie-parser')
  , favicon = require('serve-favicon')
  , path = require('path')
  , wagner = require('wagner-core');

var app = express();
var port = process.env.PORT || 8080;

require('./models')(wagner);
wagner.invoke(require('./auth'), { app: app });

app.use(favicon(path.join(__dirname, '../public/images', 'favicon.ico')));
app.use(require('morgan')('dev'));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());

app.use('/users', require('./routes/users')(wagner));
app.use('/scan', require('./routes/scan')(wagner));

app.use(express.static(path.join(__dirname, '../public'),
        { maxAge: 4 * 60 * 60 * 1000 /* 2hrs */ }));

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(error, req, res, next) {
    res.status(error.status || HTTPStatus.INTERNAL_SERVER_ERROR);
    // return json strings to the angular/ionic application
    res.json({
        message: error.message,
        error: error
    });
  });
}

// production error handler
// no stacktraces leaked to user
app.use(function(error, req, res, next) {
  res.status(error.status || HTTPStatus.INTERNAL_SERVER_ERROR);
  res.json({
    message: error.message,
    error: {}
  });
});

app.listen(port, function() {
    console.log('OOCS server listening on port %s.', port);
});
