var express = require('express')
  , passport = require('passport')
  , HTTPStatus = require('http-status');
//, secret = require('../config/secure');  FIXME

module.exports = function(wagner) {
    var api = express.Router();

    api.post('/login',
        function(req, res, next) {
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
