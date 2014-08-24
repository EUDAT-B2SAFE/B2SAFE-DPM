function listCtrl($scope, $sce, $http, $route, 
        $filter, $location, logPageList,
        logData, policy, polList, userProfile, listaction, ngTableParams) {
            
    var keys = [];

    // Set the type of list action
    $scope.listaction = listaction;

    $scope.actionPolicy = function() {
        alert("the selected action is " + angular.toJson(this.pol_data));
        $scope.policy.name = this.pol_data.pol_vals[0].name;
        $scope.policy.version = this.pol_data.pol_vals[1].name;
        $scope.policy.author = this.pol_data.pol_vals[2].name;
        $scope.policy.uuid = this.pol_data.pol_vals[3].name;
        $scope.policy.community = this.pol_data.pol_vals[6].name;
        $scope.policy.collections = 0;
        $scope.policy.action.name = this.pol_data.pol_vals[9].name;
        $scope.policy.type.name = this.pol_data.pol_vals[10].name;
        // $scope.policy.trigger.name = this.pol_data.pol_vals[11].name;

        alert("policy is " + angular.toJson($scope.policy));
        var url = "";
        if (this.polselected.name === "Modify") {
            url = "template/modify.html";
        } else if (this.polselected.name === "Remove") {
            url = "template/remove.html";
        }
        $scope.$parent.changeLoc(url);
    };

    // Read in from the config file the database schema. These will
    // be our search fields
    $http({method: "GET",
        url: "/cgi-bin/dpm/getKeys.py"}).success(function(data, status,
                headers, config) {
                    var i;
                    var is_visible = false;
                    for (i = 0; i < data.length; i++) {
                        is_visible = (data[i][1] === 'true');
                        keys.push({idx: i, name: data[i][0], visible: is_visible});
                    }
    });
    $scope.policy_columns = keys;
    $scope.updateKey = function(idx) {
        // Since the checkbutton just toggles we set the value to opposite
        // its current setting
        if ($scope.policy_columns[idx].visible === true) {
            $scope.policy_columns[idx].visible = false;
        } else {
            $scope.policy_columns[idx].visible = true;
        }
        // Need to loop over all the rows of data and set the visible flags
        // for each row
        var i = 0;
        for (i = 0; i < $scope.data.length; i++) {
            var j = 0;
            for (j = 0; j < $scope.data[i].pol_vals.length; j++) {
                if (idx == j) {
                    if ($scope.data[i].pol_vals[j].visible === false) {
                        $scope.data[i].pol_vals[j].visible = true;
                    } else {
                        $scope.data[i].pol_vals[j].visible = false;
                    }
                }
            }
        }
    };

    // 
    // Get the policies from the database as well as the log information
    var dvals = [];
    var dataSave = [];
    
    // Since the population of the author is asynchronous we can only execute
    // when the author is filled we need to make use of the promise
    userProfile.promise.then(function (response) {
        $http({method: "GET",
            url: "/cgi-bin/dpm/getPolicyData.py"}).success(function(data, 
                    status, headers, config) {
                        alert("we got " + JSON.stringify(data));

                        var i;
                        var j;
                        for (i = 0; i < data.length; i++) {
                            var ddvals = [];
                            var is_visible = false;
                            for (j = 0; j < data[i].length; j++) {
                                is_visible = (data[i][j][1] === 'true');
                                ddvals.push({name: data[i][j][0], 
                                    visible: is_visible});
                            }
                            dvals.push({pol_vals: ddvals, visible: true});
                        }
                        $scope.data = dvals;
                        var totlen = 0;
                        if ($scope.data.length > 0) {
                            totlen = $scope.data.length;
                        }
                        // Also save a copy of the data for quicker access
                        // when using filtering
                        dataSave = dvals;
                        $scope.tabs = new ngTableParams({
                            page: 1,
                            count: 10},
                        {
                            total: totlen,
                            getData: function($defer, params) {
                                $defer.resolve($scope.data.slice((params.page() - 1) * params.count(), params.page() * params.count()));
                
                                }
                            });
        });
    }
    );
    // Filter the policy so we only show those that 
    $scope.filterPolicy = function() {
        var i;
        var j;
        var count = 0;
        // We need to reset the array and repopulate from the saved list
        $scope.data = [];
        for (i = 0; i < dataSave.length; i++) {
            for (j = 0; j < dataSave[i].pol_vals.length; j++) {
                if (null == $scope.searchparam || $scope.searchparam.length === 0 || dataSave[i].pol_vals[j].name.indexOf($scope.searchparam) >= 0) {
                    $scope.data[count] = dataSave[i];
                    count += 1;
                    break;
                }             
            }
        }

        // We need to reset the page counter after filtering
        $scope.tabs.total($scope.data.length);
        $scope.tabs.reload();
    };
    $scope.reloadPolicyList = function() {
        // Get the policies from the database
        var dvals = [];
        $scope.data = [];
        userProfile.promise.then(
            $http({method: "GET",
                url: "/cgi-bin/dpm/getPolicyData.py",
                params: {username: policy.author} }).success(function(data, 
                    status, headers, config) {
                        var i;
                        var j;
                        for (i = 0; i < data.length; i++) {
                            var ddvals = [];
                            var is_visible = false;
                            for (j = 0; j < data[i].length; j++) {
                                is_visible = (data[i][j][1] === 'true');
                                ddvals.push({name: data[i][j][0], 
                                    visible: is_visible});
                            }
                            dvals.push({pol_vals: ddvals, visible: true});
                        }
                        dataSave = dvals;
                        $scope.data = dvals;

                        // We need to also make sure the filter is applied
                        // correctly before reloading the table
                        $scope.filterPolicy();
                        $scope.tabs.reload();

            })
        );
    };

    // Function to reset the highlight flags for rows
    $scope.resetFlag = function() {
        var i;
        for (i = 0; i < $scope.data.length; i++) {
            if ($scope.data[i].$selected === true) {
                $scope.data[i].$selected = false;
                break;
            }
        }
    };

    // Function to display the policy
    $scope.display_pol = function(pol_data) {
        // change the colour of the row to hightlight it
        
        // The 4th element is the id. Query the database to get the policy
        // corresponding to the uuid
        $http({method: "GET",
            url: "/cgi-bin/dpm/getPolicy.py",
            params: {uuid: pol_data.pol_vals[3].name} }).success(function(data, 
                status, headers, config) {
                    $scope.policy_obj = JSON.parse(data); 
                });
    };

    // Function to display the log information
    // (the flags for the tabs are in the parent of the parent)
    $scope.loadLogList = function() {
        logList.hide = false;
        logList.active = true;
        polList.active = false;
        $http({method: "GET",
            url: "/cgi-bin/dpm/getPolicyLog.py"}).success(function(data,
                    status, headers, config) {
                        logData = data;
                        $location.url(logList[0].url);
        });
        $scope.$parent.$parent.hideLog = logList.hide;
  //      $scope.$parent.$parent.loadLogs = logList.active;
//        $scope.$parent.$parent.listPolicy = polList.active;
        
    };
}
