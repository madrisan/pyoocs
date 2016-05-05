var express = require('express')
  , passport = require('passport');

module.exports = function(wagner) {
    var api = express.Router();

    api.route('/login')
        .post(wagner.invoke(function(User) {
            return function(req, res) {
                // TODO
                res.json({ login: 'todo' });
            };
        }));

    return api;
};
