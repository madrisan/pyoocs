angular.module('oocsApp')

       .constant('scanURL', '/scan')

       .service('ScanService', ['$http', 'scanURL', function($http, scanURL) {
           'use strict';

           this.getServerList = function(id) {
               return $http.get(scanURL);
           };
       }])

       .service('ScanDetailService', ['$http', 'scanURL', function($http, scanURL) {
           'use strict';

           this.getJSONdata = function(id) {
               //console.log('DEBUG: executing http ' + scanURL + '/' + id);
               return $http.get(scanURL + '/' + id);
           };
       }])
;
