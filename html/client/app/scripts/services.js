(function() {
    var app = angular.module('scanServices', []);

    app.constant('scanURL', '/scan');

    app.service('scanService', ['$http', 'scanURL', function($http, scanURL) {
        this.getServerList = function() {
            return $http.get(scanURL);
        };
    }]);

    app.service('scandetailService', ['$resource', 'scanURL', function($resource, scanURL) {
        this.getJSONdata = function() {
            return $resource(scanURL + '/:id', null, {'update': {method: 'PUT'}});
        };
    }]);
})();
