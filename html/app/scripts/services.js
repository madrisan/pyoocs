angular.module('oocsApp')

       .constant('scanURL', '/scan')
       .service('ScanService', ['$http', 'scanURL', function($http, scanURL) {

           'use strict';

           this.getJSONdata = function() {
                return $http.get(scanURL);
           };

        }])
;
