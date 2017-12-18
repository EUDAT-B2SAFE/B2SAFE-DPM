function modifyCtrl($scope, $window, $controller, policy, $http, data_identifier,
                    userProfile, policyService) {

    var periodChanged = false;

    $scope.currentSourcePage = 0;
    $scope.currentTargetPage = 0;

    $scope.showSrcColl = [];
    $scope.showSrcPID = [];
    $scope.showSrcPolicy = [];
    $scope.showTgtColl = [];
    $scope.showTgtPID = [];
    $scope.showTgtPolicy = [];
 
    // We need to make a copy of the original policy so any updates
    // can be compared
    $scope.origPolicy = copyPol(policy);
    console.log("origPolicy is " + JSON.stringify($scope.origPolicy));
    console.log("policy is " + JSON.stringify($scope.policy));

    $controller('datasetCtrl', {$scope: $scope});
    $controller('actionCtrl', {$scope: $scope});

    // Must explicitly update the typeselected
    for (var idxs = 0; idxs < policy.sources.length; idxs++) {
        $scope.typeSelected(idxs, 'source');
    }
    for (var idxt = 0; idxt < policy.targets.length; idxt++) {
        $scope.typeSelected(idxt, 'target');
    }
    // If the policy has a period type we need to pass the string and
    // fill the corresponding values
    $scope.policy = policyService.getObj();
    policy = parsePeriod($scope.policy);

    // Flags to detect if a policy element changes
    $scope.polChanged = {title: null, sources: [], targets: [],
        type: null, trigger_name: null, trigger_value: null,
        organisation: null, location: null, system: null, action: null,
        site: null, path: null, resource: null};

    $scope.invalidFlags = {action: {period: false, period_date: false},
                           sources: [], targets: []};
    $scope.pristineFlags = {action: {action: false, type: false, trigger: false, 
                                    period: false, trigger_date: false,
                                    period_date: false},
                           sources: [], targets: []};
    
    if ($scope.policy.trigger.name === 'date/time') {
        $scope.updateTrigger();
    }
    if ($scope.policy.sources.length > 1) {
        $scope.showAddTargets = false;
    }
    if ($scope.policy.targets.length > 1) {
        $scope.showAddSources = false;
    }
    for (var sindex =  0; sindex < $scope.policy.sources.length; sindex++) {
        $scope.polChanged.sources.push({collection: null, pid: null, policy: null,
                                        hostname: null, identifier: null});
        $scope.invalidFlags.sources.push({organisation: false, system: false,
                                         site: false, resource: false, pid: false,
                                         coll: false});
        $scope.pristineFlags.sources.push({organisation: false, location_type: false,
                                           system: false, site: false, resource: false,
                                           coll: false, pid: false});
    }
    for (var tindex = 0; tindex < $scope.policy.targets.length; tindex++) {
        $scope.polChanged.targets.push({collection: null, pid: null, hostname: null,
                                        identifier: null});
        $scope.invalidFlags.targets.push({organisation: false, system: false,
                                         site: false, resource: false, pid: false,
                                         coll: false});
        $scope.pristineFlags.targets.push({organisation: false, location_type: false,
                                           system: false, site: false, resource: false,
                                           coll: false, pid: false});
    }

    $scope.backToList = function() {
        $scope.$parent.changeLoc("template/listtable.html");
    };

    $scope.ulist = [userProfile.username];
    $scope.comlist = userProfile.communities;

    $scope.titleChange = function() {
        if ($scope.policy.name != $scope.origPolicy.name) {
            $scope.polChanged.title = true;
        } else {
            $scope.polChanged.title = false;
        }
    };

    $scope.changePeriod = function() {
        var periodval = [$scope.policy.trigger_period.weekday.name,
            $scope.policy.trigger_period.month.name,
            $scope.policy.trigger_period.day.name,
            $scope.policy.trigger_period.hour.name,
            $scope.policy.trigger_period.minute.name];
        trigger_value = periodval.join(", ");
            if (trigger_value != $scope.origPolicy.trigger.value) {
                $scopr.polChanged.trigger_value = true;
            } else {
                $scope.polChanged.trigger_value = false;
            }
    };

    // Record if the organisation changes
    $scope.organisationChange = function() {
        if ($scope.orgList.length > 1) {
            if ($scope.target.organisation.name !=
                    $scope.origPolicy.target.organisation.name) {
                        $scope.polChanged.organisation = true;
            } else {
                $scope.polChanged.organisation = false;
            }
        }
    };

    // Record if the location changes
    $scope.locationChange = function() {
        if ($scope.locTypes.length > 1) {
            if ($scope.policy.target.loctype.name !=
                    $scope.origPolicy.target.loctype.name) {
                        $scope.polChanged.location = true;
            } else {
                $scope.polChanged.location = false;
            }
        }
    };

    $scope.authorChange = function() {
        if ($scope.policy.author != $scope.origPolicy.author) {
            $scope.polChanged.author = true;
        } else {
            $scope.polChanged.author = false;
        }
    };

    $scope.identifierChange = function() {
        // We need to reset the collection flag since the identifier is
        // higher level
        $scope.polChanged.collection[this.$index] = false;
        if ($scope.pidList.length > 1) {
            if (policy.collections[this.$index].type !=
                    $scope.origPolicy.collections[this.$index].type) {
                $scope.polChanged.identifier[this.$index] = true;
            } else {
                $scope.polChanged.identifier[this.$index] = false;
            }
        }
    };

    $scope.collectionChange = function() {
        if (policy.collections[this.$index].name !=
                $scope.origPolicy.collections[this.$index].name) {
                    $scope.polChanged.collection[this.$index] = true;
        } else {
            $scope.polChanged.collection[this.$index] = false;
        }
    };

    $scope.communityChange = function() {
        if ($scope.comlist.length > 1) {
            if ($scope.policy.community != $scope.origPolicy.community) {
                $scope.polChanged.community = true;
            } else {
                $scope.polChanged.community = false;
            }
        }
    };

    // Read the available identifier types
    pidList = [];
    $http({method: "GET",
        url: "${CGI_URL}/query_actions.py",
        params: {qtype: "identifiers"}}).then(function(results) {
            var data = results.data;
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    pidList.push(data[idx][0]);
                }
            }
            $scope.pidList = pidList;
    });

    // Read the list of actions
    $http({method: "GET",
        url: "${CGI_URL}/query_actions.py",
        params: {qtype: "operations"}}).then(function(results) {
            var data = results.data;
            var opList = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    opList.push(data[idx][0]);
                }
            }
            $scope.actionList = opList;
    });

    // Read the action types
    var getTypObj = getActionType($http, $scope.policy.action.name);

    getTypObj.success(function(data,
                status, headers, config) {
                    var typeList = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            typeList.push(data[idx][0]);
                        }
                    }
                    $scope.typeList = typeList;
                });

    // If the action changes need to update the list of types
    // and reset the type default (since it may not correspond
    $scope.actionChange = function() {
        var getTypObj = getActionType($http, $scope.policy.action.name);
        getTypObj.then(function(results) {
            var data = results.data;
            var typeList = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    typeList.push(data[idx][0]);
                }
            }
            $scope.typeList = typeList;
        });
        // Is the action different to original?
        // need to reset the type flag as the two are coupled
        $scope.polChanged.type = false;
        if ($scope.actionList.length > 1) {
            if ($scope.policy.action.name != $scope.origPolicy.action.name) {
                $scope.polChanged.action = true;
            } else {
                $scope.polChanged.action = false;
            }
        }
    };

    // Record if the type has changed and reload the trigger list
    $scope.typeChange = function() {
        var getTrgObj = getActionTrigger($http, $scope.policy.action.name,
                $scope.policy.type.name);
        getTrgObj.then(function(results) {
            var data = results.data;
            var triggerList = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    triggerList.push(data[idx][0]);
                }
            }
            $scope.triggerList = triggerList;
        });
        if ($scope.typeList.length >= 1) {
            console.log("orig " + $scope.origPolicy.type.name + " now " +
                    $scope.policy.type.name);
            if ($scope.policy.type.name != $scope.origPolicy.type.name) {
                $scope.polChanged.type = true;
            } else {
                $scope.polChanged.type = false;
            }
        }
    };

    // Get the triggers
    var getTrgObj = getActionTrigger($http, $scope.policy.action.name,
            $scope.policy.type.name);
    getTrgObj.then(function(results) {
        var data = results.data;
        var triggerList = [];
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                triggerList.push(data[idx][0]);
            }
        }
        $scope.triggerList = triggerList;
    });

    // Record a change in the trigger
    $scope.triggerChange = function() {
        if ($scope.triggerList.length > 1) {
            if ($scope.policy.trigger.name != $scope.origPolicy.trigger.name) {
                $scope.polChanged.trigger_name = true;
            } else {
                $scope.polChanged.trigger_name = false;
            }
        }
    };

    // Get the organisation from the database
    var getOrgObj = getOrganisation($http);
    getOrgObj.success(function(data, status, headers, config) {
        var orgList = [];
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                orgList.push(data[idx][0]);
            }
        }
        $scope.orgList = orgList;
    });

    // Get the location type
    var getLocObj = getLocation($http, $scope.policy.action.name,
            $scope.policy.type.name, $scope.policy.trigger.name);
    getLocObj.then(function(results) {
        var data = results.data;
        var locTypes = [];
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                locTypes.push(data[idx][0]);
            }
        }
        $scope.locTypes = locTypes;
    });

    // Get the list of systems
    var getSysObj = getSystem($http);
    getSysObj.then(function(results) {
        var data = results.data;
        var sysList = [];
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                sysList.push(data[idx][0]);
            }
        }
        $scope.sysList = sysList;
    });

    // Show the date if the trigger type is date
    $scope.showDate = function(trgname) {
        var show = false;
        if (trgname === "date") {
            show = true;
            $scope.trigger_date = $scope.policy.trigger.value;
        }
        return show;
    };

    // Update the date
    $scope.updatePeriodDate = function() {
        console.log("updatePeriodDate called " + $scope.policy.dateString);
        if (($scope.policy.dateString != $scope.origPolicy.dateString)) {
            $scope.polChanged.trigger_value = true;
        } else {
            $scope.polChanged.trigger_value = false;
        }
        $scope.policy.trigger.value = getIsoDate($scope.policy.dateString);
    };

    // Handle the opening of the calendar from the icon
    $scope.datOpen = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };

    $scope.period = getPeriod();

    // Record changes to the path
    $scope.pathChange = function() {
        if (this.policy.target.path != $scope.origPolicy.target.path) {
            $scope.polChanged.path = true;
        } else {
            $scope.polChanged.path = false;
        }
    };

    // Record the fact that the resource changed
    $scope.resourceChange = function() {
        if ($scope.resList.length > 1) {
            if (this.policy.target.resource.name !=
                $scope.origPolicy.target.resource.name) {
                    $scope.polChanged.resource = true;
            } else {
                $scope.polChanged.resource = false;
            }
        }
    };

    // Parse the period trigger and set the corresponding types
    function parsePeriod(apolicy) {
        if (apolicy.trigger.name === "period") {
            vals = apolicy.trigger.value.split(', ');
            apolicy.trigger_period.weekday.name = vals[4];
            apolicy.trigger_period.month.name = vals[3];
            apolicy.trigger_period.day.name = vals[2];
            apolicy.trigger_period.hour.name = vals[1];
            apolicy.trigger_period.minute.name = vals[0];
        }
        return apolicy;
    }

    // submit the policy to the database
    $scope.updatePolicy = function() {
        // Check if the policy has been changed
        console.log("polChanged is " + JSON.stringify($scope.polChanged));
        console.log("policy updated is " + JSON.stringify($scope.policy));
        console.log("pristineflags " + JSON.stringify($scope.pristineFlags));
        console.log("invalidFlags " + JSON.stringify($scope.invalidFlags));
        var polChangedObj = checkPolChanged($scope.polChanged, $scope.policy, $scope.origPolicy, $scope.invalidFlags);
        console.log("polChangedObj " + polChangedObj.changed + " invalid " + polChangedObj.invalid);
        $scope.invalidFlags = polChangedObj.invalidFlags;
        if (polChangedObj.changed) {
            if (polChangedObj.invalid === false) {
                policy.uuid = createGuid();
                $http.post("${CGI_URL}/storeModifiedPolicy.py",
                        JSON.stringify(policy),
                        {headers: "Content-Type: application/x-www-form-urlencoded"}).success(function(data, status, headers, config)
                            {
                                if (data.policy_exists) {
                                    alert("The policy exists in the database");
                                } else {
                                    alert("Updated policy has been successfully stored in the database");
                                }
                                $window.location.reload();
                            }).error(function(data, status, headers, config)
                                {
                                    alert("Problem with storing the policy");
                                    alert(data);
                                });
            } else {
                console.log("invalidFlags " + JSON.stringify($scope.invalidFlags));
                $scope.submitted = true;
            }
        } else {
            alert("Policy is unmodified. Will not update the stored policy");
        }
    };
}
