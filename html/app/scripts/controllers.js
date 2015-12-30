angular.module('oocsApp')

       .controller('ScanController', ['$scope', 'ScanService', function($scope, ScanService) {
           'use strict';

           $scope.showScan = false;
           $scope.message = "Loading ...";

           $scope.hostname = {};
           $scope.distribution = {};
           $scope.scan = {};

           ScanService.getJSONdata()
           .then(
               function(response) {

                   function getkeys(data) {
                       var keys = [];
                       for (var key in data) {
                           if (data.hasOwnProperty(key)) {
                               keys.push(key);
                           }
                       }
                       return keys;
                   }

                   var jsondata = response.data;
                   $scope.hostname = getkeys(jsondata)[0];
                   //console.log('hostname: ' + $scope.hostname);
                   $scope.distribution =
                       jsondata[$scope.hostname].distribution;
                   //console.log('distribution: ' + $scope.distribution.description);

                   $scope.modules = getkeys(jsondata[$scope.hostname].modules);
                   //console.log($scope.modules);

                   $scope.getModuleData = function (moduleName) {
                       var checks = jsondata[$scope.hostname].modules[moduleName].checks,
                           status = jsondata[$scope.hostname].modules[moduleName].status;

                       return {
                           checks  : checks,
                           status  : status
                       };
                   };

                   $scope.showScan = true;
               },
               function(response) {
                   $scope.message =
                       "Error: " + response.status + " " + response.statusText;
               }
           );

           $scope.tab = 1;
           $scope.issueClass = "";

           $scope.select = function(setTab) {
               $scope.tab = setTab;

               if (setTab === 2) {
                   $scope.issueClass = "critical";
               }
               else if (setTab === 3) {
                   $scope.issueClass = "warning";
               }
               else if (setTab === 4) {
                   $scope.issueClass = "passed";
               }
               else {
                   $scope.issueClass = "";
               }

               //console.log("issueClass: " + $scope.issueClass);
           };

           $scope.isSelected = function(checkTab) {
               return ($scope.tab === checkTab);
           };

           $scope.hideIssues = function(currIssueClass) {
               if ($scope.issueClass === "")
                   return false;

               if (currIssueClass != $scope.issueClass)
                   return true;

               return false;
           };

       }])

       .controller('AboutController', ['$scope', function($scope) {
           'use strict';

       }])
;