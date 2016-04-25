(function() {
    var app = angular.module('scan-services', []);

    app.constant('scanURL', '/scan');

    app.service('ScanService', ['$http', 'scanURL', function($http, scanURL) {
        this.getServerList = function() {
            return $http.get(scanURL);
        };
    }]);

    app.service('ScanDetailService', ['$resource', 'scanURL', function($resource, scanURL) {
        this.getJSONdata = function() {
            console.log('DEBUG: executing http ' + scanURL + '/' + id);
            return $resource(scanURL + '/:id', null, {'update': {method: 'PUT'}});
        };
    }]);
})();
