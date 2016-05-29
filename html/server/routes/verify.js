var jwt = require('jsonwebtoken')
  , HTTPStatus = require('http-status');

var config = require('../config/secure');

// generate a token for the user
exports.generateToken = function(user) {
    var token = jwt.sign(
        user,
        config.secretKey, {
            expiresIn: '1h'   // the token will be valid for one hour
        }
    );
    return token;
};

exports.verifyOrdinaryUser = function(req, res, next) {
    var token = req.headers['x-access-token'];

    if (token) {
        jwt.verify(token, config.secretKey, function(error, decoded) {
            if (error) {
                var err = new Error('Unathorized user');
                err.status = HTTPStatus.UNAUTHORIZED;
                return next(err);
            }

            req.decoded = decoded;   // save to request for use in other routes
            next();
        });
    } else {
        var err = new Error('No access token provided');
        err.status = HTTPStatus.FORBIDDEN;
        return next(err);
    }
};

exports.verifyAdminUser = function(req, res, next) {
    if (req.decoded._doc.admin) {
        next();
    } else {
        var err = new Error('You are not authorized to perform this operation');
        err.status = HTTPStatus.FORBIDDEN;
        return next(err);
    }
};
