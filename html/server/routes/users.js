var express = require('express')
  , passport = require('passport')
  , HTTPStatus = require('http-status')
  , jwt = require('jsonwebtoken')
  , config = require('../config/secure');

module.exports = function(wagner) {
    var api = express.Router();

    api.post('/login',
        function(req, res, next) {
            // passport takes the req.body.email and req.body.password and
            // passes it to our verification function in the local strategy.

            // Note: static user/passwd (just for debugging)
            //
            // var post = req.body;
            // if (post.email === '...' && post.password === '...') {
            //     var token = jwt.sign(
            //         { user: post.email },
            //         config.secretKey, {
            //         expiresIn: '1h'   // the token will be valid for one hour
            //     });
            //
            //     return res.status(HTTPStatus.OK).json({
            //         status: 'Login successful',
            //         success: true,
            //         token: token
            //     });
            // } else {
            //     return res.status(HTTPStatus.UNAUTHORIZED).json({
            //         error: 'Login failed'
            //     });
            // }

            passport.authenticate('local', function(error, user, info) {
                if (error) { return next(error); }

                if (!user) {
                    return res.status(HTTPStatus.UNAUTHORIZED).json({
                        error: info
                    });
                }

                // the middleware will call req.logIn (a passport function attached to
                // the request) - this will call our passport.serializeUser method.
                // this method can access the user object we passed back to the
                // middleware.  It's its job to determine what data from the user object
                // should be stored in the session.  The result of the serializeUser
                // method is attached to the session as
                // req.session.passport.user = { // our serialised user object // }.

                // The result is also attached to the request as req.user.
                // Once done, our requestHandler is invoked.

                req.logIn(user, function(error) {
                    if (error) { return next(error); }

                    // generate a token for the user
                    var token = jwt.sign(
                        user,
                        config.secretKey, {
                            expiresIn: '1h'   // the token will be valid for one hour
                        }
                    );
                    res.status(HTTPStatus.OK).json({
                        status: 'Login successful',
                        success: true,
                        token: token
                    });
            });
        })(req, res, next);
    });

    api.get('/logout',
        function(req, res) {
            res.status(HTTPStatus.OK).json({
                status: 'Bye!'
            });
        }
    );

    return api;
};
