angular.module('oocsApp')
       .constant("baseURL", "@baseURL@")
       .service('ScanService', ['$http', 'baseURL', function($http, baseURL) {

           'use strict';

           this.getJSONdata = function() {
                return $http.get(baseURL + 'scan');
           };

        }])
;
