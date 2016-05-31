(function() {
    var app = angular.module('scanServices', []);

    app.constant('scanURL', '/scan');
    app.constant('loginURL', '/users/login');
    app.constant('logoutURL', '/users/logout');

    app.factory('authFactory',
        ['$http', '$q', '$localStorage', '$rootScope', 'loginURL', 'logoutURL',
        function ($http, $q, $localStorage, $rootScope, loginURL, logoutURL) {

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
            $localStorage.storeObject('accessToken', credentials);
            useUserCredentials(credentials);
        }

        function destroyUserCredentials() {
            userInfo = {};
            $http.defaults.headers.common['x-access-token'] = undefined;
            $localStorage.remove('accessToken');
        }

        function login(email, password) {
            var deferred = $q.defer();

            $http.post(loginURL, { email: email, password: password }).
                then(function(response) {
                    console.log('post:' + loginURL + ' : ' +
                                JSON.stringify(response.data));

                    storeUserCredentials({
                        email: email,
                        token: response.data.token
                    });

                    userInfo.authenticated = true;
                    $rootScope.$broadcast('login:successful');

                    deferred.resolve('login successful');
                }, function(error) {
                    userInfo.authenticated = false;
                    $rootScope.$broadcast('login:failed');

                    deferred.reject(error);
                });

            return deferred.promise;
        }

        function logout() {
            $http.get(logoutURL).
                then(function(response) {});
            destroyUserCredentials();
        }

        function getAuthenticatedUser() {
            return userInfo.email;
        }

        function isAuthenticated() {
            return userInfo.authenticated;
        }

        loadUserCredentials();

        return {
            login: login,
            logout: logout,
            getAuthenticatedUser: getAuthenticatedUser,
            isAuthenticated: isAuthenticated
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
