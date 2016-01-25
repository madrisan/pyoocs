angular.module('oocsApp')

       .constant('scanURL', '/scan')

       .service('ScanService', ['$http', 'scanURL', function($http, scanURL) {
           'use strict';

           this.getServerList = function() {
               return $http.get(scanURL);
           };
       }])

       .service('ScanDetailService', ['$resource', 'scanURL', function($resource, scanURL) {
           'use strict';

           this.getJSONdata = function() {
               //console.log('DEBUG: executing http ' + scanURL + '/' + id);
               return $resource(scanURL + '/:id', null, {'update': {method: 'PUT'}});
           };
       }])
;
