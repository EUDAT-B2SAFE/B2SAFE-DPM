function listCtrl($scope, $sce, $http, $route,
        $filter, $location, logPageList,
        logData, policy, polList, uuids,
        showLog, userProfile, listaction, policyService,
        ngTableParams) {

    var keys = [];
    var dkeys = {};
    $scope.displayKeys = false;
    $scope.showingActive = true;
    $scope.showingRemoved = false;

    // Display the checkbox for the columns
    $scope.showCheckbox = function() {
        if ($scope.displayKeys === false) {
            $scope.displayKeys = true;
        } else {
            $scope.displayKeys = false;
        }
    };

    // Set the type of list action
    $scope.listaction = listaction.active;

    $scope.actionPolicy = function() {
        for (i = 0; i < keys.length; i++) {
            dkeys[keys[i].name] = keys[i].idx;
        }
        var polSelected = this.polselected.name; 
        $http({method: "GET", url: "${CGI_URL}/load_policy.py",
               params: {uuid: this.pol_data.pol_vals[dkeys.policy_uniqueid].name,
                        policyURL: this.pol_data.pol_vals[this.pol_data.pol_vals.length-3].name}}).then(function(results) {
            var data = results.data;
            console.log('data is ' + JSON.stringify(data));
            $scope.policy.name = data.name;
            $scope.policy.version = data.version;
            $scope.policy.author = data.author;
            $scope.policy.uuid = data.uuid;
            $scope.policy.id = data.uuid;
            $scope.policy.family = data.family;
            $scope.policy.community = data.community.toLowerCase();
            $scope.policy.sources = data.sources;
            $scope.policy.targets = data.targets;
            $scope.policy.action = {"name": data.trigger.name};
            $scope.policy.type.name = data.type.name;
            $scope.policy.trigger.name = data.trigger.name;
            $scope.policy.dateString = data.dateString;
            $scope.policy.trigger_date.name = data.trigger_date.name;
            $scope.policy.trigger_period = {"name": data.trigger_period.name};
            $scope.policy.trigger.value = "";
            $scope.$parent.pol_cand = $scope.policy;
            policyService.setObj($scope.policy);
        
            var url = "";
            if (polSelected === "Modify") {
                url = "template/modify.html";
            } else if (polSelected === "Reject") {
                url = "template/remove.html";
                $scope.policy.saved_uuid = $scope.policy.uuid;
            } else if (polSelected === "Reactivate") {
                url = "template/reactivate.html";
                $scope.policy.saved_uuid = $scope.policy.uuid;
            }
            $scope.$parent.changeLoc(url);
        });

    };

    // Read in from the config file the database schema. These will
    // be our search fields
    $http({method: "GET",
        url: "${CGI_URL}/getKeys.py"}).then(function(results) {
            var data = results.data;
            var i;
            var is_visible = false;
            for (i = 0; i < data.length; i++) {
                is_visible = (data[i][1] === 'true');
                keys.push({idx: i, name: data[i][0], visible: is_visible});
            }
            for (i = 0; i < keys.length; i++) {
                dkeys[keys[i].name] = keys[i].idx;
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
            url: "${CGI_URL}/getPolicyData.py"}).then(function(results) {
                var i;
                var j;
                var data = results.data;
                $scope.showingRemoved = false;
                $scope.showingActive = true;
                uuids = clearArray(uuids);
                for (i = 0; i < data.length; i++) {
                    var ddvals = [];
                    var is_visible = false;
                    var polrm = false;
                    for (j = 0; j < data[i].length; j++) {
                      if (j === 5) {
                        dat = new Date(parseInt(data[i][j][0])*1000);
                        data[i][j][0] = displayDate(dat);
                      }
                      is_visible = (data[i][j][1] === 'true');
                      ddvals.push({name: data[i][j][0], visible: is_visible});
                    }
                    // Set flag indicating whether to show removed
                    // policy to false by default.
                    if (data[i][data[i].length-1][0] === "REJECTED" || 
                            data[i][data[i].length-1][0] === "SUSPENDED") {
                        polrm = true;
                    }

                    if (polrm === true) {
                        dvals.push({pol_vals: ddvals, visible: false,
                            removed: polrm, listaction: listaction.removed});
                    } else {
                        dvals.push({pol_vals: ddvals, visible: true,
                            removed: polrm, listaction: listaction.active});
                    }

                    // Keep the uid for matching with the log files
                    uuids.push(data[i][dkeys.policy_uniqueid][0]);
                }

                $scope.data = dvals;
                var totlen = 0;
                if ($scope.data.length > 0) {
                    totlen = $scope.data.length;
                }

                // Also save a copy of the data for quicker access
                // when using filtering
                dataSave = dvals;

                $scope.tabs = new ngTableParams({page: 1, count: 10},
                        {
                            total: totlen,
                            getData: function($defer, params) {
                                $defer.resolve($scope.data.slice((params.page() - 1) * params.count(), params.page() * params.count()));

                            }
                        });
        });
    }
    );
    // Filter the policy so we only show those that have visibility selected
    $scope.filterPolicy = function() {
        var i;
        var j;
        var count = 0;
        // We need to reset the array and repopulate from the saved list
        $scope.data = [];
        uuids = clearArray(uuids);
        for (i = 0; i < dataSave.length; i++) {
            for (j = 0; j < dataSave[i].pol_vals.length; j++) {
                if (null == $scope.searchparam || $scope.searchparam.length === 0 || dataSave[i].pol_vals[j].name.indexOf($scope.searchparam) >= 0) {
                    if ($scope.showingActive === true) {
                        if (dataSave[i].removed === false) {
                            $scope.data[count] = dataSave[i];
                            uuids.push(dataSave[i].pol_vals[dkeys.policy_uniqueid].name);
                            count += 1;
                        }
                    } else if ($scope.showingRemoved === true) {
                        if (dataSave[i].removed === true) {
                            $scope.data[count] = dataSave[i];
                            uuids.push(dataSave[i].pol_vals[dkeys.policy_uniqueid].name);
                            count += 1;
                        }
                    }
                    break;
                }
            }
        }

        // We need to reset the page counter after filtering
        $scope.tabs.total($scope.data.length);
        $scope.tabs.reload();
    };

    // Clear the search
    $scope.clearSearch = function() {
        $scope.searchparam = '';
        $scope.filterPolicy();
    };

    $scope.reloadPolicyList = function() {
        // Get the policies from the database
        var dvals = [];
        $scope.data = [];
        $scope.showingActive = true;
        $scope.showingRemoved = false;
        userProfile.promise.then(
            $http({method: "GET",
                url: "${CGI_URL}/getPolicyData.py"}).success(function(data,
                    status, headers, config) {
                        var i;
                        var j;
                        uuids = clearArray(uuids);
                        for (i = 0; i < data.length; i++) {
                            var ddvals = [];
                            var is_visible = false;
                            var polrm = false;
                            for (j = 0; j < data[i].length; j++) {
                                if (j === 5) {
                                  var dat = new Date(parseInt(data[i][j][0])*1000);
                                  data[i][j][0] = displayDate(dat);
                                }
                                is_visible = (data[i][j][1] === 'true');
                                ddvals.push({name: data[i][j][0],
                                    visible: is_visible});
                            }
                            // Set flag indicating whether to show removed
                            // policy to false by default.
                            if (data[i][data[i].length-1][0] === "REJECTED" ||
                                    data[i][data[i].length-1][0 === "SUSPENDED"]) {
                                polrm = true;
                            }

                            if (polrm === true) {
                                dvals.push({pol_vals: ddvals, visible: false,
                                    removed: polrm, listaction: listaction.removed});
                            
                            } else {
                                dvals.push({pol_vals: ddvals, visible: true,
                                    removed: polrm, listaction: listaction.active});
                            }
                            uuids.push(data[i][dkeys.policy_uniqueid][0]);
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

    // Show only the active policies
    $scope.showActive = function() {
        var i;
        var j;
        var count = 0;
        // We need to reset the array and repopulate from the saved list
        $scope.data = [];
        uuids = clearArray(uuids);
        for (i = 0; i < dataSave.length; i++) {
            if (dataSave[i].removed === false) {
                if (dataSave[i].$selected === true) {
                    delete dataSave[i].$selected;
                }
                $scope.data[count] = dataSave[i];
                uuids.push(dataSave[i].pol_vals[dkeys.policy_uniqueid].name);
                count += 1;
            }
        }
        $scope.policy_obj = "";

        // We need to reset the page counter after filtering
        $scope.showingActive = true;
        $scope.showingRemoved = false;
        $scope.tabs.total($scope.data.length);
        $scope.tabs.reload();

    };

    // Show only the removed policies
    $scope.showRemoved = function() {
        var i;
        var j;
        // We need to reset the array and repopulate from the saved list
        $scope.data = [];
        uuids = clearArray(uuids);
        for (i = 0; i < dataSave.length; i++) {
            if (dataSave[i].removed === true) {
                if (dataSave[i].$selected === true) {
                    delete dataSave[i].$selected;
                }
                $scope.data.push(dataSave[i]);
                $scope.data[i].visible = true;
                uuids.push(dataSave[i].pol_vals[dkeys.policy_uniqueid].name);
            }
        }
        $scope.policy_obj = "";

        // We need to reset the page counter after filtering
        $scope.showingActive = false;
        $scope.showingRemoved = true;
        $scope.tabs.total($scope.data.length);
        $scope.tabs.reload();
    };

    // Function to reset the highlight flags for rows
    $scope.resetFlag = function() {
        uuids = clearArray(uuids);
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
        // The 4th element is the id. Query the database to get the policy
        // corresponding to the uuid
        $http({method: "GET",
            url: "${CGI_URL}/getPolicy.py",
            params: {uuid: pol_data.pol_vals[dkeys.policy_uniqueid].name,
                     policyURL:  pol_data.pol_vals[pol_data.pol_vals.length-3].name}}).then(function(results) {
                var data = results.data;
                uuids = clearArray(uuids);
                uuids.push(pol_data.pol_vals[dkeys.policy_uniqueid].name);
                $scope.policy_obj = JSON.parse(data);
        });
    };

    // Function to display the log information
    // (the flags for the tabs are in the parent of the parent)
    $scope.loadLogList = function() {
       var url = "template/listlogs.html";
       showLog.name = true;
       $scope.$parent.changeLoc(url);
    };
}

function displayDate(date) {
  var returnDate = '';
  var month = parseInt(date.getMonth()) + 1;
  var day = date.getDate();
  if (month < 10) {
    month = '0' + month;
  }
  if (day < 10) {
    day = '0' + date.getDate();
  }
  returnDate = date.getFullYear() + '-' + month + '-' + day;
  return returnDate;
}
