angular.module('oocsApp', ['ui.router'])

       .config(function($stateProvider, $urlRouterProvider) {

           'use strict';
           $stateProvider

           // route for the home page
           .state('app', {
               url   :'/',
               views : {
                   'header': {
                       templateUrl : 'views/header.html',
                   },
                   'content': {
                       templateUrl : 'views/scan.html',
                       controller  : 'ScanController'
                   },
                   'footer': {
                       templateUrl : 'views/footer.html',
                   }
               }
           })

           // route for the about page
           .state('app.about', {
               url   : 'about',
               views : {
                   'content@': {
                       templateUrl : 'views/about.html',
                       controller  : 'AboutController'
                   }
               }
           });

           $urlRouterProvider.otherwise('/');
       })
;