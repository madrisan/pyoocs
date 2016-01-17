angular.module('oocsApp')

       .constant('scanURL', '/scan')
       .service('ScanService', ['$http', 'scanURL', function($http, scanURL) {

           'use strict';

           this.getJSONdata = function() {
                //console.log('DEBUG: executing http ' + scanURL);
                return $http.get(scanURL);
           };

        }])
;
