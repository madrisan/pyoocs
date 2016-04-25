(function() {
    var app = angular.module('scan-controllers', ['scan-services']);

    var getkeys = function(data) {
        var keys = [];
        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                keys.push(key);
            }
        }
        return keys;
    };

    // translate the json severity to the corresponding
    // bootstrap label color
    var bootstrap_label = function(severity) {
        var severities = {
            'success' : 'success',
            'warning' : 'warning',
            'critical': 'danger'
        };

        return severities[severity] || 'default';
    };

    app.controller('ScanController', ['$scope', 'ScanService',
        function($scope, ScanService) {
            $scope.showServerList = false;
            $scope.servers = [];

            ScanService.getServerList()
                .then(
                    function(response) {
                        $scope.servers = response.data;
                        $scope.showServerList = true;
                        $scope.bootstrap_label = bootstrap_label;
                    },
                    function(response) {
                        $scope.message = "Error: " + response.status + " " + response.statusText;
                    }
                );
            }
    ]);

    app.controller('ScanDetailController',
                   ['$scope', '$stateParams', 'ScanDetailService',
        function($scope, $stateParams, ScanDetailService) {
            $scope.showScan = false;
            $scope.message = "Loading ...";

            $scope.hostname = {};
            $scope.distribution = {};
            $scope.modules = {};

            ScanDetailService.getJSONdata()
                .get({id: $stateParams.id})
                .$promise.then(
                    function(jsondata) {
                        $scope.hostname = jsondata.hostname;
                        //console.log('hostname: ' + $scope.hostname);
                        $scope.distribution = jsondata.distribution;
                        //console.log('distribution: ' + $scope.distribution.description);
                        $scope.modules = getkeys(jsondata.modules);
                        //console.log('modules: ' + $scope.modules);

                        $scope.getModuleData = function (moduleName) {
                            var checks = jsondata.modules[moduleName].checks,
                                status = jsondata.modules[moduleName].status;

                            return { checks: checks, status: status };
                        };
                        //console.log('getModuleData(filesystem).checks = ' +
                        //    JSON.stringify($scope.getModuleData('filesystem').checks));

                        var scan_summary = jsondata.summary;
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
                            return "label-" + bootstrap_label($scope.max_severity);
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

    app.controller('AboutController', ['$scope', function($scope) {
    }]);
})();
