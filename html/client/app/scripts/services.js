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

    app.factory('$localStorage', ['$window', function ($window) {
        return {
            store: function (key, value) {
                $window.localStorage[key] = value;
            },
            get: function (key, defaultValue) {
                return $window.localStorage[key] || defaultValue;
            },
            remove: function (key) {
                $window.localStorage.removeItem(key);
            },
            storeObject: function (key, value) {
                $window.localStorage[key] = JSON.stringify(value);
            },
            getObject: function (key, defaultValue) {
                return JSON.parse($window.localStorage[key] || defaultValue);
            }
        };
    }]);
})();
