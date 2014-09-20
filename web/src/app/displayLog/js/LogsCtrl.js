function logsCtrl($scope, $route, $interval, $http, logData, 
        policy, uuids, showLog, ngTableParams) {

    // Query the database for the log information
    getLogs($scope, ngTableParams, $http, showLog, policy.author, uuids);
    
    // Regularly query the database for any updates
    // (only run the repeat when we are actually displaying the log info
    // otherwise stop)
    if (showLog.name) {
        var repeatGetLogs = $interval(function() {
            getLogs($scope, ngTableParams, $http, showLog, policy.author, uuids);
        }, 6000, 0);
    }

    //Display the policy information
    $scope.loadPolicyList = function() {
        $interval.cancel(repeatGetLogs);
        showLog.name = false;
        var url="template/listtable.html";
        $scope.$parent.changeLoc(url);
    };
}
