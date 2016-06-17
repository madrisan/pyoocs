(function() {
    var app = angular.module('scanControllers',
                             ['ui-notification', 'scanServices']);

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

    app.controller('scanController', ['$scope', 'scanService',
        function($scope, scanService) {
            $scope.showServerList = false;
            $scope.servers = [];

            $scope.mainMessage = 'Loading ...';
            $scope.detailedMessage = '';

            scanService.getServerList().then(
                function(response) {
                    console.log('scanService.getServerList() succeeded');
                    $scope.servers = response;
                    $scope.showServerList = true;
                    $scope.bootstrap_label = bootstrap_label;

                    for(var i = 0; i < $scope.servers.length; i++) {
                        var passed = parseInt($scope.servers[i].passed, 10),
                            warnings = parseInt($scope.servers[i].warnings, 10),
                            criticals = parseInt($scope.servers[i].criticals, 10),
                            total = passed + warnings + criticals;

                        var ppassed = Math.round(passed * 100 / total),
                            pwarnings = Math.round(warnings * 100 / total),
                            pcriticals = Math.round(criticals * 100 / total);

                        $scope.servers[i].ppassed = ppassed;
                        $scope.servers[i].pwarnings = pwarnings;
                        $scope.servers[i].pcriticals = pcriticals;

                        //console.log('% ' + ppassed + ' ' + pwarnings + ' ' + pcriticals);
                    }
                },
                function(response) {
                    $scope.mainMessage = "Error " + response.status +
                        " (" + response.statusText + ")";
                    $scope.detailedMessage = response.data.error;
                }
            );
        }
    ]);

    app.controller('scandetailController',
                   ['$scope', '$stateParams', 'scandetailService',
        function($scope, $stateParams, scandetailService) {
            $scope.showScan = false;
            $scope.mainMessage = 'Loading ...';
            $scope.detailedMessage = '';

            $scope.hostname = {};
            $scope.distribution = {};
            $scope.modules = {};

            scandetailService.getJSONdata()
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
                        $scope.mainMessage = "Error " + response.status +
                            " (" + response.statusText + ")";
                        $scope.detailedMessage = response.data.error;
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

    app.controller('headerController',
        ['$scope', '$rootScope', 'authFactory',
        function($scope, $rootScope, authFactory) {
            if (authFactory.isAuthenticated()) {
                $scope.loggedIn = true;
                $scope.loggedUser = authFactory.getAuthenticatedUser();
            } else {
                $scope.loggedIn = false;
                $scope.loggedUser = '';
            }

            $scope.logOut = function() {
                authFactory.logout();

                $scope.loggedIn = false;
                $scope.loggedUser = '';

                window.location = '/';
            };

            $rootScope.$on('login:successful', function() {
                $scope.loggedIn = true;
                $scope.loggedUser = authFactory.getAuthenticatedUser();
            });

        }]);

    app.controller('loginController',
        ['$scope', '$localStorage', 'authFactory', 'Notification',
        function($scope, $localStorage, authFactory, Notification) {
            $scope.credentials = {};
            $scope.loginError = false;

            $scope.submit = function(credentials) {
                $scope.credentials = angular.copy(credentials);

                //console.log('email   : ' + $scope.credentials.email);
                //console.log('password: ' + $scope.credentials.password);
                //console.log('remember: ' + $scope.credentials.rememberMe);

                if($scope.credentials.rememberMe) {
                    $localStorage.storeObject('userinfo', {
                        email: $scope.credentials.email,
                        password: $scope.credentials.password
                    });
                }

                var promise = authFactory.login(
                    $scope.credentials.email,
                    $scope.credentials.password
                );
                promise.then(function(message) {
                    console.log('authFactory.login promise: ' + message);
                }, function(reason) {
                    console.log('authFactory.login promise: ' +
                                JSON.stringify(reason.statusText));
                    $scope.loginErrorNotification();
                });
            };

            $scope.loginErrorNotification = function() {
                Notification.error({
                    message: 'Incorrect login credentials',
                    positionX: 'center',
                    positionY: 'top',
                    delay: 3000
                });
            };

        }]);
})();
