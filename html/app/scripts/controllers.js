var oocsAppModule = angular.module('oocsApp');

var getkeys = function(data) {
    var keys = [];
    for (var key in data) {
        if (data.hasOwnProperty(key)) {
            keys.push(key);
        }
    }
    return keys;
};

oocsAppModule.controller('ScanController', ['$scope', 'ScanService',
    function($scope, ScanService) {

        'use strict';

        $scope.showServerList = false;
        $scope.urls = [];

        ScanService.getServerList()
        .then(
            function(response) {
                $scope.urls = response.data;
                $scope.showServerList = true;
            },
            function(response) {
                $scope.message = "Error: " + response.status + " " + response.statusText;
            }
        );
    }
]);

oocsAppModule.controller('ScanDetailController',
    ['$scope', '$stateParams', 'ScanDetailService',
    function($scope, $stateParams, ScanDetailService) {

        'use strict';

        //console.log('executing the dispatchJSONdata() body...');

        $scope.showScan = false;
        $scope.message = "Loading ...";

        $scope.hostname = {};
        $scope.distribution = {};
        $scope.modules = {};

        ScanDetailService.getJSONdata()
            .get({id:parseInt($stateParams.id, 10)})
            .$promise.then(
                function(response) {
                    var jsondata = response;

                    $scope.hostname = getkeys(jsondata)[0];
                    //console.log('hostname: ' + $scope.hostname);

                    $scope.distribution = jsondata[$scope.hostname].distribution;
                    //console.log('distribution: ' + $scope.distribution.description);

                    $scope.modules = getkeys(jsondata[$scope.hostname].modules);
                    //console.log($scope.modules);

                    $scope.getModuleData = function (moduleName) {
                        var checks = jsondata[$scope.hostname].modules[moduleName].checks,
                            status = jsondata[$scope.hostname].modules[moduleName].status;

                        return {
                            checks : checks,
                            status : status
                        };
                    };

                    var scan_summary = jsondata[$scope.hostname].summary;
                    //console.log('summary: ' + JSON.stringify(scan_summary));

                    $scope.max_severity = scan_summary.max_severity;
                    //console.log('max_severity: ' + $scope.max_severity);

                    $scope.infos = scan_summary.infos;
                    //console.log('infos: ' + $scope.infos);
                    $scope.warnings = scan_summary.warnings;
                    //console.log('warnings: ' + $scope.warnings);
                    $scope.criticals = scan_summary.criticals;
                    //console.log('criticals: ' + $scope.criticals);

                    $scope.totals = $scope.infos + $scope.warnings + $scope.criticals;

                    $scope.max_severity_label = function() {
                        var severities = {
                            'success' : 'label-success',
                            'warning' : 'label-warning',
                            'critical': 'label-danger'
                        };

                        var label = severities[$scope.max_severity];
                        return label ? label : 'label-default';
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

    }
]);

oocsAppModule.controller('AboutController', ['$scope', function($scope) {
    'use strict';

    }
]);
