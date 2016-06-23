var jwt = require('jsonwebtoken')
  , HTTPStatus = require('http-status');

module.exports = function(wagner) {
    var module = {};

    var secretKey = wagner.invoke(function(Config) {
        return Config.secretKey;
    });

    // generate a token for the user
    module.generateToken = function(user) {
        var token = jwt.sign(
            user,
            secretKey, {
                expiresIn: '1h'   // the token will be valid for one hour
            }
        );
        return token;
    };

    module.verifyOrdinaryUser = function(req, res, next) {
        var token = req.headers['x-access-token'];

        if (token) {
            jwt.verify(token, secretKey, function(error, decoded) {
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

    module.verifyAdminUser = function(req, res, next) {
        if (req.decoded._doc.admin) {
            next();
        } else {
            var err = new Error('You are not authorized to perform this operation');
            err.status = HTTPStatus.FORBIDDEN;
            return next(err);
        }
    };

    return module;
};
