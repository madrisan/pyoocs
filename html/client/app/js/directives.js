(function() {
  var app = angular.module('scan-directives', []);

  app.directive("scanReports", function() {
    return {
      restrict: 'E',
      templateUrl: "scan-reports.html"
    };
  });
})();
