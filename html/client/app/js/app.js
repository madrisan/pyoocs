(function() {
    var app = angular.module('oocsApp', [
        'ui.router',
        'ngResource',
        'scanControllers'
    ]);

    app.config(function($stateProvider, $urlRouterProvider) {
        'use strict';

        $urlRouterProvider.otherwise('/');

        $stateProvider.
        // route for the scan list page
        state('app', {
            url: '/',
            views: {
                'header': {
                    templateUrl: 'views/header.html',
                    controller: 'headerController'
                },
                'content': {
                    templateUrl: 'views/scan.html',
                    controller: 'scanController'
                },
                'footer': {
                    templateUrl: 'views/footer.html'
                }
            },
            data: { requireLogin: true }
        }).
        // route for the scandetail page
        state('app.scandetail', {
            url: 'scan/:id',
            views: {
                'content@': {
                    templateUrl: 'views/scandetail.html',
                    controller: 'scandetailController'
                }
            },
            data: { requireLogin: true }
        }).
        // route for the about page
        state('app.about', {
            url: 'about',
            views: {
                'content@': {
                    templateUrl: 'views/about.html'
                }
            },
            data: { requireLogin: false }
        }).
        // route for the login page
        state('app.login', {
            url: 'users/login',
            views: {
                'content@': {
                    templateUrl: 'views/login.html',
                    controller: 'loginController'
                }
            }
        });
    });

    app.config(function($httpProvider) {
        $httpProvider.interceptors.push(function($q, $injector) {
            return {
                responseError: function(rejection) {
                    if (rejection.status !== 401) {
                        return rejection;
                    }
                    return $q.reject(rejection);
                }
            };
        });
    });

    // start capturing attempted state changes and inspecting them for our
    // requireLogin property.

    app.run(function($rootScope, $state, authFactory) {
        $rootScope.$on('$stateChangeStart',
                       function(e, toState, toParams, fromState, fromParams) {

            var requireLogin = toState.data ? toState.data.requireLogin : false;
            //console.log('requireLogin: ' + requireLogin);

            console.log('fromState: ' + fromState.name + ' ---> toState: ' + toState.name);

            if (requireLogin && toState.name !== 'app.login') {
                console.log('redirect to app.login...');

                var authenticated = authFactory.isAuthenticated();
                console.log('authenticated: ' + authenticated);

                if (authenticated !== true) {
                     e.preventDefault();    // stop current execution
                     $state.go('app.login');   // go to the login form
                }
            }
        });

        $rootScope.$on('login:successful', function() {
            console.log('redirect to app...');
            $state.go('app');
        });
    });

})();
