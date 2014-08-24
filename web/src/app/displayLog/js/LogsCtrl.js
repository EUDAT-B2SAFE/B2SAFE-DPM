function logsCtrl($scope, $http, logData, policy, ngTableParams) {
    // Query the database for the log information
    $http({method: "GET",
        url: "/cgi-bin/dpm/getPolicyLog.py",
       params: {username: policy.author} }).success(function(data, 
                status, headers, config) {
                    $scope.logData = data.data;
                    var loglen = 0;
                    if ($scope.logData.length > 0) {
                        loglen = $scope.logData.length;
                    }
                    $scope.logColumns = data.columns;
                    $scope.logtabs = new ngTableParams({page: 1, 
                        count: 10}, 
                        {
                            total: loglen,
                            getData: function($defer, params) {
                                $defer.resolve($scope.logData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
                
                            }
                        }); 
                });
}
