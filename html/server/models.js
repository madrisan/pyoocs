var mongoose = require('mongoose')
  , _ = require('underscore');

var database = require('./config/database')

module.exports = function(wagner) {
    mongoose.connection.on('error', function(error) {
        console.log(error.name + ': ' + error.message);
        throw error;
    });
    mongoose.connect(database.url);

    wagner.factory('db', function() {
        return mongoose;
    });

    var Scan = mongoose.model('Scan', require('./models/scan'), 'scan')
      , User = mongoose.model('User', require('./models/user'), 'users');

    var models = {
        Scan: Scan,
        User: User
    };

    _.each(models, function(value, key) {
        wagner.factory(key, function() {
            return value;
        });
    });

    return models;
}
