function getLogs($scope, ngTableParams, $http, showLog,
        author, uuids) {
    var getAuthor = $http({method: 'GET',
        url: '${CGI_URL}/getStatus.py',
        params: {username: author} }).then(function(results) {
            var data = results.data;
            var loglen = 0;
            var logData = [];
            if (data.data.length > 0) {
                loglen = data.data.length;
                // loop over the rows and set the visibility
                // for the row depending on whether the log id
                // is in the list of ids from the list page
                for (var i = 0; i < loglen; i++) {
                    var logVisible = false;
                    if (uuids.indexOf(data.data[i].policy_uniqueid) >= 0) {
                        logVisible = true;
                    }
                    var statusList = [];
                    for (var j = 0; j < data.columns.length; j++) {
                        statusList.push(data.data[i][data.columns[j]]);
                    }
                    console.log("statusList " + JSON.stringify(statusList));
                    logData.push({visible: logVisible, row: statusList});
                }
                $scope.logData = logData;
                $scope.data = logData;
            }
            $scope.logColumns = data.columns;
    });
}
