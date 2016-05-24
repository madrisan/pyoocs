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
                    templateUrl: 'views/header.html'
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

    // start capturing attempted state changes and inspecting them for our
    // requireLogin property.

    app.run(function ($rootScope, $state) {
        $rootScope.$on('$stateChangeStart',
                       function(e, toState, toParams, fromState, fromParams) {

            var requireLogin = toState.data ? toState.data.requireLogin : false;
            //console.log('requireLogin: ' + requireLogin);

            //console.log('fromState: ' + fromState.name + ' ---> toState: ' + toState.name);

            if (requireLogin && toState.name !== 'app.login') {
                //console.log('redirect to app.login...');
                e.preventDefault();
                $state.go('app.login');
            }
        });
    });

})();
