var fs = require('fs');
var path = require('path');

module.exports = function(wagner) {
    wagner.factory('Config', function() {
        var filepath = path.join(__dirname, './config/');
        return JSON.parse(fs.readFileSync(filepath + 'secure.json').toString());
    });
};
