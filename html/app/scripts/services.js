angular.module('oocsApp')
       .constant("baseURL","http://localhost:8000/")
       .service('ScanService', ['$http', 'baseURL', function($http, baseURL) {

           'use strict';

           this.getJSONdata = function() {
                return $http.get(baseURL + 'scan');
           };

        }])
;
