function getLogs($scope, ngTableParams, $http, showLog, 
        author, uuids) {
    $http({method: "GET", url: "/cgi-bin/dpm/getPolicyLog.py",
            params: {username: author} }).success(function(data, 
                    status, headers, config) {
                        var loglen = 0;
                        var logData = [];
                        if (data.data.length > 0) {
                            loglen = data.data.length;
                        // loop over the rows and set the visibility
                        // for the row depending on whether the log id
                        // is in the list of ids from the list page
                            for (var i = 0; i < loglen; i++) {
                                var log_visible = false;
                                if (uuids.indexOf(data.data[i][1]) >= 0) {
                                    log_visible = true;
                                }
                                logData.push({visible: log_visible,
                                    row: data.data[i]});
                            }
                            $scope.logData = logData;
                            $scope.data = logData;
                        }
                        $scope.logColumns = data.columns;
//                        $scope.logtabs = new ngTableParams({page: 1, 
//                            count: 10}, 
//                            {
//                                counts: [],
//                                total: 1,
                                //total: loglen,
//                                getData: function($defer, params) {
//                                    $defer.resolve($scope.logData.slice((params.page() - 1) * params.count(), params.page() * params.count()));
                
                                 //   if (params.page() > 1) {
                                 //       showLog.name = false;
                                 //   } else {
                                 //       showLog.name = true;
                                 //   }
//                                }
//                            }); 
    });
}
