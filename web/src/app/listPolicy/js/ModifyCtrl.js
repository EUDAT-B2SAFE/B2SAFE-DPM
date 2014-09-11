function modifyCtrl($scope, policy, $http, data_identifier, userProfile) {

    // We need to make a copy of the original policy so any updates
    // can be compared

    var origPolicy = copyPol(policy);

    // If the original policy had a period we need to parse the string
    // and set the defaults
    //TBD

    // Flags to detect if a policy element changes
    var polChanged = {title: null, community: null, identifier: [],
        collection: [], type: null, trigger_name: null, trigger_value: null,
        organisation: null, location: null, system: null, action: null,
        site: null, path: null, resource: null};

    $scope.backToList = function() {
        $scope.$parent.changeLoc("template/listtable.html");
    };
   
    $scope.ulist = [userProfile.username];
    $scope.comlist = userProfile.communities;
   
    $scope.titleChange = function() {
        if ($scope.policy.name != origPolicy.name) {
            polChanged.title = true;
        } else {
            polChanged.title = false;
        }
    };
    
    // Record if the organisation changes
    $scope.organisationChange = function() {
        if ($scope.orgList.length > 1) {
            if ($scope.target.organisation.name != 
                    origPolicy.target.organisation.name) {
                        polChanged.organisation = true;
            } else {
                polChanged.organisation = false;
            }
        }     
    };

    // Record if the location changes
    $scope.locationChange = function() {
        if ($scope.locTypes.length > 1) {
            if ($scope.policy.target.loctype.name != 
                    origPolicy.target.loctype.name) {
                        polChanged.location = true;
            } else {
                polChanged.location = false;
            }
        }
    };

    $scope.authorChange = function() {
        if ($scope.policy.author != origPolicy.author) {
            polChanged.author = true;
        } else {
            polChanged.author = false;
        }
    };
    
    $scope.identifierChange = function() {
        // We need to reset the collection flag since the identifier is
        // higher level
        polChanged.collection[this.$index] = false;
        if ($scope.pidList.length > 1) {
            if (policy.collections[this.$index].type != 
                    origPolicy.collections[this.$index].type) {
                polChanged.identifier[this.$index] = true;
            } else {
                polChanged.identifier[this.$index] = false;
            }
        }     
    };

    $scope.collectionChange = function() {
        if (policy.collections[this.$index].name != 
                origPolicy.collections[this.$index].name) {
                    polChanged.collection[this.$index] = true;
        } else {
            polChanged.collection[this.$index] = false;
        }
    };

    $scope.communityChange = function() {
        if ($scope.comlist.length > 1) {
            if ($scope.policy.community != origPolicy.community) {
                polChanged.community = true;
            } else {
                polChanged.community = false;
            }
        }    
    };

    // Read the available identifier types
    pidList = [];
    $http({method: "GET",
        url: "/cgi-bin/dpm/query_actions.py",
        params: {qtype: "identifiers"}}).success(function(data, status,
                headers, config) {
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            pidList.push(data[idx][0]); 
                        }
                    }
                    $scope.pidList = pidList;
    });

    // Read the list of actions
    $http({method: "GET",
        url: "/cgi-bin/dpm/query_actions.py",
        params: {qtype: "operations"}}).success(function(data, status,
                headers, config) {
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
        getTypObj.success(function(data, status, headers, config) {
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
        polChanged.type = false;
        if ($scope.actionList.length > 1) {
            if ($scope.policy.action.name != origPolicy.action.name) {
                polChanged.action = true;
            } else {
                polChanged.action = false;
            }
        } 
    };
    
    // Record if the type has changed and reload the trigger list
    $scope.typeChange = function() {
        var getTrgObj = getActionTrigger($http, $scope.policy.action.name,
                $scope.policy.type.name);
        getTrgObj.success(function(data, status, headers, config) {
            var triggerList = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    triggerList.push(data[idx][0]);
                }
            }
            $scope.triggerList = triggerList;
        });

        if ($scope.typeList.length > 1) {
            if ($scope.policy.type.name != origPolicy.type.name) {
                polChanged.type = true;
            } else {
                polChanged.type = false;
            }
        }
    };

    // Get the triggers
    var getTrgObj = getActionTrigger($http, $scope.policy.action.name,
            $scope.policy.type.name);
    getTrgObj.success(function(data, status, headers, config) {
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
            if ($scope.policy.trigger.name != origPolicy.trigger.name) {
                polChanged.trigger_name = true;
            } else {
                polChanged.trigger_name = false;
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
    getLocObj.success(function(data, status, headers, config) {
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
    getSysObj.success(function(data, status, headers, config) {
        var sysList = [];
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                sysList.push(data[idx][0]);
            }
        }
        $scope.sysList = sysList;
    });
    
    // Get the list of sites
    var getSiteObj = getSite($http, $scope.policy.target.system.name);
    getSiteObj.success(function(data, status, headers, config) {
        var siteList = [];
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                siteList.push(data[idx][0]);
            }
        }
        $scope.siteList = siteList;
    });

    // Get the list of resources
    var getResObj = getResource($http, $scope.policy.target.system.name,
            $scope.policy.target.site.name);
    getResObj.success(function(data, status, headers, config) {
        var resList = [];
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                resList.push(data[idx][0]);
            }
        }
        $scope.resList = resList;
    });
    
    // If the system changes we need to keep a record
    $scope.systemChange = function() {
        if ($scope.sysList.length > 1) {
            polChanged.site = false;
            if ($scope.policy.target.system.name != 
                    origPolicy.target.system.name) {
                polChanged.system = true;
            } else {
                polChanged.system = false;
            }
        } 
    };

    // If the site changes we need to reload the resources
    $scope.siteChange = function() {
        var getResObj = getResource($http, 
                $scope.policy.target.system.name,
                $scope.policy.target.site.name);
        getResObj.success(function(data, status, headers, config) {
            var resList = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    resList.push(data[idx][0]);
                }
            }
            $scope.resList = resList;
        });
        // If we only have one site the flag will not change so 
        polChanged.resource = false;
        if ($scope.siteList.length > 1) {
            if (origPolicy.target.site.name != 
                    $scope.policy.target.site.name) {
                        polChanged.site = true;
            } else {
                polChanged.site = false;
            }
        }
    };

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
    $scope.updateDate = function() {
        if (($scope.trigger_date != origPolicy.trigger.value)) {
            polChanged.trigger_value = true;
        } else {
            polChanged.trigger_value = false;
        }
        $scope.policy.trigger.value = getIsoDate($scope.trigger_date);
    };

    // Handle the opening of the calendar from the icon
    $scope.datOpen = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };

    $scope.period = getPeriod();

    // Show the period
    $scope.showPeriod = function(trgname) {
        var show = false;
        if (trgname === "period") {
            show = true;
        }
        return show;
    };

    // Record changes to the path
    $scope.pathChange = function() {
        if (this.policy.target.path != origPolicy.target.path) {
            polChanged.path = true;
        } else {
            polChanged.path = false;
        }
    };

    // Record the fact that the resource changed
    $scope.resourceChange = function() {
        if ($scope.resList.length > 1) {
            if (this.policy.target.resource.name != 
                origPolicy.target.resource.name) {
                    polChanged.resource = true;
            } else {
                polChanged.resource = false;
            }
        } 
    };

    // submit the policy to the database
    $scope.updatePolicy = function() {
        // Check if the policy has been changed
        var polChangedObj = checkPolChanged(polChanged);
        if (polChangedObj.changed) { 
            if (polChangedObj.invalid.length === 0) {
                $http.post("/cgi-bin/dpm/storeModifiedPolicy.py", 
                        JSON.stringify(policy),
                        {headers: "Content-Type: application/x-www-form-urlencoded"}).success(function(data, status, headers, config) 
                            {
                                alert("Updated policy has been successfully stored in the database");
                                if (data.policy_exists) {
                                    alert("The policy exists in the database");
                                }
                            }).error(function(data, status, headers, config)
                                {
                                    alert("Problem with storing the policy");
                                    alert(data);
                                });
            } else {
                alert("there is a problem " + angular.toJson(data));
            }
        } else {
            alert("Policy is unmodified. Will not update the stored policy");
        }
    };
}
