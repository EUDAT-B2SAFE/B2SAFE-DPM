function logsCtrl($scope, $http, logData, policy, ngTableParams) {
    // Query the database for the log information
    $http({method: "GET",
        url: "/cgi-bin/dpm/getPolicyLog.py",
       params: {username: policy.author} }).success(function(data, 
                status, headers, config) {
                    $scope.logData = data.data;
                    $scope.logColumns = data.columns;
                    $scope.logtabs = new ngTableParams({page: 1, 
                        count: 10}, 
                        {
                            total: $scope.logData.length,
                            getData: function($defer, params) {
                                $defer.resolve($scope.logData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
                
                            }
                        }); 
                });
}
