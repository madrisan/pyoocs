var mongoose = require('mongoose')
  , _ = require('underscore');

var database = require('./config/database')

module.exports = function(wagner) {
    mongoose.connect(database.url);

    wagner.factory('db', function() {
        return mongoose;
    });

    var Scan =
        mongoose.model('Scan', require('./models/scan'), 'scan');

    var models = {
        Scan: Scan
    };

    _.each(models, function(value, key) {
        wagner.factory(key, function() {
            return value;
        });
    });

    return models;
}
