(function() {
    var app = angular.module('scanServices', []);

    app.constant('scanURL', '/scan');
    app.constant('loginURL', '/users/login');

    app.factory("authFactory",
        ['$resource', '$http', 'loginURL', '$localStorage', '$rootScope',
        function ($resource, $http, loginURL, $localStorage, $rootScope) {

        console.log('inside authFactory..');

        var authFac = {};
        var userInfo = {};

        function useUserCredentials(credentials) {
            userInfo = {
                email: credentials.email,
                token: credentials.token,
                authenticated: true
            };

            // set the token as header for next requests
            $http.defaults.headers.common['x-access-token'] = credentials.token;
        }

        function loadUserCredentials() {
            var credentials = $localStorage.getObject('accessToken', '{}');

            if (credentials.email !== undefined) {
                console.log('using stored credentials...');
                useUserCredentials(credentials);
            }
        }

        function storeUserCredentials(credentials) {
            $localStorage.storeObject('userInfo', credentials);
            useUserCredentials(credentials);
        }

        authFac.login = function(email, password) {
            $resource(loginURL).
                save({ email: email, password: password },
                    function(response) {
                        console.log('post:' + loginURL + ' : ' + response);
                        storeUserCredentials({
                            email: email,
                            token: response.token
                        });
                        userInfo.authenticated = true;
                        $rootScope.$broadcast('login:successful');
                    },
                    function(response) {
                        userInfo.authenticated = false;

                        // FIXME: login unsuccessful
                        //   response.data.err.message
                        //   response.data.err.name
                        console.log('login unsuccessful');
                    }
                 );
        };

        //authFac.getUserInfo = function() {
        //    return userInfo;
        //};

        authFac.isAuthenticated = function() {
            return userInfo.authenticated;
        };

        loadUserCredentials();

        return authFac;
    }]);

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
