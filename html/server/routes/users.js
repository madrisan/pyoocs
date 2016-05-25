var express = require('express')
  , passport = require('passport')
  , bodyParser = require('body-parser')
  , HTTPStatus = require('http-status')
  , jwt = require('jsonwebtoken')
  , config = require('../config/secure');

module.exports = function(wagner) {
    var api = express.Router();

    api.use(bodyParser.json());

    api.post('/login',
        function(req, res, next) {
            // Note: static user/passwd just for testing
            //
            //var post = req.body;
            //if (post.email === 'davide.madrisan@gmail.com' &&
            //    post.password === '1234') {
            //    var token = jwt.sign(
            //        { user: post.email },
            //        config.secretKey, {
            //        expiresIn: '1h'   // the token will be valid for one hour
            //    });
            //
            //    return res.status(HTTPStatus.OK).json({
            //        status: 'Login successful',
            //        success: true,
            //        token: token
            //    });
            //} else {
            //    return res.status(HTTPStatus.UNAUTHORIZED).json({
            //        error: 'Login failed'
            //    });
            //}

            passport.authenticate('local', function(error, user, info) {
                if (error) {
                    return next(error);
                }
                if (!user) {
                    return res.status(HTTPStatus.UNAUTHORIZED).json({
                        error: info
                    });
                }
                req.logIn(user, function(error) {
                    if (error) {
                        return res.status(HTTPStatus.INTERNAL_SERVER_ERROR).json({
                            error: 'Could not log in user'
                        });
                    }

                    // generate a token for the user
                    var token = jwt.sign(user, secure.secretKey, {
                        expiresIn: 3600   // the token will be valid for one hour
                    });

                    res.status(HTTPStatus.OK).json({
                        status: 'Login successful',
                        success: true,
                        token: token
                    });
                });
            })(req, res, next);
        }
    );

    return api;
};
