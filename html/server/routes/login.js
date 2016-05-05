var express = require('express')
  , bodyParser = require('body-parser');

module.exports = function(wagner) {
    var api = express.Router();

    api.use(bodyParser.json());

    api.route('/')
        .post(wagner.invoke(function(User) {
            return function(req, res) {
                res.json({ login: 'todo' });
            };
        }));

    return api;
};
