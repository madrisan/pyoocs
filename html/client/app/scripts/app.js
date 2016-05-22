(function() {
    var app = angular.module('oocsApp', [
        'ui.router',
        'ngResource',
        'scanControllers'
    ]);

    app.config(function($stateProvider, $urlRouterProvider) {
        'use strict';

        $stateProvider.
        // route for the home page
        state('app', {
            url: '/',
            views: {
                'header': {
                    templateUrl: 'views/header.html',
                },
                'content': {
                    templateUrl: 'views/scan.html',
                    controller: 'scanController'
                },
                'footer': {
                    templateUrl: 'views/footer.html',
                }
            }
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
        }).
        // route for the scandetail page
        state('app.scandetail', {
            url: 'scan/:id',
            views: {
                'content@': {
                    templateUrl: 'views/scandetail.html',
                    controller: 'scandetailController'
                }
            }
        }).
        // route for the about page
        state('app.about', {
            url: 'about',
            views: {
                'content@': {
                    templateUrl: 'views/about.html',
                }
            }
        });

        $urlRouterProvider.otherwise('/');
    });
})();
