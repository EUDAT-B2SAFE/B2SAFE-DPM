var dpmApp = angular.module("dpmApp", ["ngRoute", "ui.bootstrap", "ngTable"]);

// The list of routes. Each 'page' of the form is a route
var locList = [{url: "/personal", path: "template/personal.html"},
               {url: "/dataset_action", path: "template/dataset_action.html"},
               {url: "/summary", path: "template/summary.html"}
              ];

var logList = [{url: "/listlogs", path: "template/listlogs.html"}];

var maxPage = 1;
var minPage = 0;
var ds_count = 0;

function dpmFormConfig($routeProvider) {
    $routeProvider.
        when("/", {
            controller: personalCtrl,
            templateUrl: locList[0].path
        }).
        when(locList[0].url, {
            controller: personalCtrl,
            templateUrl: locList[0].path
        }).
        when(locList[1].url, {
            controller: datasetCtrl,
            templateUrl: locList[1].path
        }).
        when(locList[2].url, {
            controller: confirmCtrl,
            templateUrl: locList[2].path
        }).
        when(logList[0].url, {
            controller: logsCtrl,
            templateUrl: logList[0].path
        }).
        otherwise({
            redirectTo: "/"
        });
}

dpmApp.config(dpmFormConfig);

function storeData(arr, val) {
    var duplicate = false;
    var i;
    for (i = 0; i < arr.length; i++) {
        if (val == arr[i].name) {
            duplicate = true;
            break;
        }
    }
    if (! duplicate) {
        arr.push({name: val});
    }
    return arr;
}


function createGuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,
                function(c) {
                    var r = Math.random() * 16|0, v = c === 'x' ? r : (r&0x3|0x8);
                    return v.toString(16);
                });
}

function getIsoDate(idate) {
    var t_date;
    var cur_date = idate.getDate();
    var cur_month = idate.getMonth() + 1;
    var cur_year = idate.getFullYear();
    t_date = cur_year + "-" + cur_month + "-" + cur_date;
    return t_date;
}

function actionCtrl($scope, $http, $injector, policy, disabled_flags, 
        data_action, submitFlag) {
    $scope.policy = policy;
    $injector.invoke(dpmCtrl, this, {$scope: $scope});

    var disabled_flags_obj = disabled_flags.getFlags();
    var action_obj = data_action.getActions();

    $scope.operations = action_obj.operations;
    $scope.triggers = action_obj.triggers;
    $scope.types = action_obj.types;
    $scope.location_types = action_obj.location_types;

    $scope.action_type = disabled_flags_obj.action_type;
    $scope.action_trigger = disabled_flags_obj.action_trigger;
    $scope.tgt_organisation_disabled = disabled_flags_obj.tgt_organisation;
    
    // Read in the available actions
    $http({method: "GET",
        url: "/cgi-bin/dpm/query_actions.py",
        params: {qtype: "operations"}}).success(function(data, status,
                headers, config) {
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                        action_obj.operations = 
                            storeData(action_obj.operations,
                                data[idx][0]);
                        }
                    }
                $scope.operations = action_obj.operations;
                data_action.setActions(action_obj);
    });
    weekday = new Array({name: "*"});
    for (i = 0; i < 7; i++) {
        weekday.push({name: i});
    }

    month = new Array({name: "*"});
    for (i = 0; i < 12; i++) {
        month.push({name: i});
    }
 
    day = new Array({name: "*"});
    for (i = 0; i < 32; i++) {
        day.push({name: i});
    }
 
    hour = new Array({name: "*"});
    for (i = 0; i < 24; i++) {
        hour.push({name: i});
    }
 
    minute = new Array({name: "*"});
    for (i = 0; i < 60; i++) {
        minute.push({name: i});
    }

    $scope.period = {month: month, weekday: weekday, day: day, 
        hour: hour, minute: minute};
   
    // Only show the date fields for the date option
    var tdate = new Date();
    $scope.showDate = function(trname) {
        var show = false;
        if (trname == "date") {
            show = true;
            if (typeof $scope.trigger_date == "undefined") {
                $scope.trigger_date = tdate;
                $scope.policy.trigger_date = getIsoDate(tdate);
            }
        }
        return show; 
    };

    $scope.datClear = function() {
    };
    $scope.datOpen = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };

    $scope.updateDate = function() {
        $scope.policy.trigger_date = getIsoDate($scope.trigger_date);
    };

    // Only show the period fields for the periodic option
    $scope.showPeriod = function(trname) {
        var show = false;
        if (trname == "period") {
            show = true;
            $scope.policy.trigger_period = $scope.period;
        }
        return show;
    };

    // function to enable the action type option
    $scope.changeType = function() {
        $http({method: "GET",
            url: "/cgi-bin/dpm/query_actions.py",
            params: {qtype: "types",
                operation: $scope.policy.action.name}
        }).success(function(data,
                status, headers, config) {
                    action_obj.types = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            action_obj.types = 
                            storeData(action_obj.types, data[idx][0]);
                        }
                    }
                    $scope.types = action_obj.types;
                    data_action.setActions(action_obj);
                });
        disabled_flags_obj.action_type = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.pristineFlags.action.action = false;
        $scope.policy.type.name = '--- Select a Type ---';
        $scope.action_type = disabled_flags_obj.action_type;
    };


    // function to enable the trigger option
    $scope.changeTrigger = function() {
        $http({method: "GET",
            url: "/cgi-bin/dpm/query_actions.py",
            params: {qtype: "triggers",
                operation: $scope.policy.action.name,
                type: $scope.policy.type.name}
        }).success(function(data,
                status, headers, config) {
                    action_obj.triggers = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            action_obj.triggers = 
                            storeData(action_obj.triggers, data[idx][0]);
                        }
                    }
                    $scope.triggers = action_obj.triggers;
                    data_action.setActions(action_obj);
                });
        disabled_flags_obj.action_trigger = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.pristineFlags.action.type = false;
        $scope.policy.trigger.name = "--- Select a Trigger ---";
        $scope.action_trigger = disabled_flags_obj.action_trigger;
    };

    // Read from the database the available locations
    $scope.changeOrganisation = function() {
        $http({method: "GET", 
            url: "/cgi-bin/dpm/query_actions.py", 
            params: {qtype: "organisations"}}).success(function(data, 
                status, headers, config) {
                    action_obj.organisations = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            action_obj.organisations = 
                                storeData(action_obj.organisations, 
                                    data[idx][0]);
                        }
                    }
                    $scope.organisations = action_obj.organisations;
                    data_action.setActions(action_obj);
                    disabled_flags_obj.tgt_organisation = false;
                    disabled_flags.setFlags(disabled_flags_obj);
                    $scope.pristineFlags.action.trigger = false;
                    $scope.policy.target.organisation.name = "--- Select an Organisation ---";
                    $scope.tgt_organisation_disabled = disabled_flags_obj.tgt_organisation;
 
        });
    };

    // invoke the SourceTarget control
    $injector.invoke(sourceTargetCtrl, this, {$scope: $scope});
}

function confirmCtrl($scope, $injector, page, submitFlag, policy) {
    $scope.policy = policy;
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
    // We need to reset the active flag so we don't automatically
    // trigger the submitForm code
    var flago = submitFlag.getObj();
    flago.active = false;
    flago.flag = false;
    flago.confirm = true;
    submitFlag.setObj(flago);
}

function dpmCtrl($scope, $location, page, invalidFlag, submitFlag) {
    
    $scope.invalidFlag = invalidFlag;

    if (page.firstPage === true) {
        $location.url(locList[page.count].url);
        page.firstPage = false;
    }
    $scope.nextPage = function nextPage(evnt, invalid) {
        if (invalid) {
            $scope.invalidFlag.policyName = true;
            $scope.invalidFlag.policyVersion = true;
            $scope.invalidFlag.policyAuthor = true;
            $scope.invalidFlag.policyCommunity = true;
        } else {
            $scope.invalidFlag.policyVersion = false;
            $scope.invalidFlag.policyAuthor = false;
            $scope.invalidFlag.policyCommunity = false;
            $scope.invalidFlag.policyName = false;
            if (page.count < maxPage) {
                page.count += 1;
                $location.url(locList[page.count].url);
            }
        }
    };
    $scope.prevPage = function prevPage() {
        flago = submitFlag.getObj();
        if (flago.submitted && !flago.flag) {
            flago.flag = true;
            flago.confirm = false;
            submitFlag.setObj(flago);
        }
        if (page.count > minPage) {
            page.count -= 1;
            $location.url(locList[page.count].url);
        }
    };
    $scope.firstPage = function () {
        var showP = true;
        if (page.count <= minPage) {
            showP = false;
        }
        return showP;
    };
    $scope.lastPage = function () {
        var showP = true;
        if (page.count >= maxPage) {
            showP = false;
        }
        return showP;
    };
    $scope.showSubmit = function() {
        var showS = false;
        var flago = submitFlag.getObj();
        if (flago.flag || page.count >= maxPage) {
            if (flago.submitted && !flago.flag) {
                showS = false;
            } else {
                showS = true;
            }
        }
        return showS;
    };
    $scope.showConfirm = function() {
        var showC = false;
        var flago = submitFlag.getObj();
        if (flago.confirm) {
            showC = true;
        }
        return showC;
    };
}

function datasetCtrl($scope, $http, $injector, data_identifier, policy, 
        pristineFlags, invalidFlags, submitFlag) {
    $scope.policy = policy;
    $scope.pristineFlags = pristineFlags;
    $scope.invalidFlags = invalidFlags;

    // Call the base dpm controller for the next/previous pages
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
    var identifier_obj = data_identifier.getIdentifiers();
    
    // Read in the available identifier types
    $http({method: "GET",
        url: "/cgi-bin/dpm/query_actions.py",
        params: {qtype: "identifiers"}}).success(function(data, status,
                headers, config) {
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            identifier_obj.types = 
                            storeData(identifier_obj.types,
                                data[idx][0]);
                        }
                    }
                $scope.identifier_types = identifier_obj.types;
                data_identifier.setIdentifiers(identifier_obj);
    });
    
    $scope.currentPage = 0;

    $scope.addMore = function() {
        ds_count += 1;
        var id = "dataset_" + ds_count; 
        var flago = submitFlag.getObj();
        flago.active = false;
        submitFlag.setObj(flago);
        $scope.policy.collections.push({name: "", type: {name: ""}});
        $scope.invalidFlags.dataset.push({pid: true, coll: true});
        $scope.pristineFlags.dataset.push({pid: true, coll: true});
    };
    $scope.numberOfPages = function() {
        return Math.ceil($scope.policy.collections.length/3);
    };
    $scope.removeCollection = function(array, index) {
        array.splice(index, 1);
    };

    // Only show the collection fields for the PID option
    $scope.showCollection = function(trname) {
        var show = false;
        var tname = trname.replace(/^\s+|\s+$/g, '');
        if (tname == "PID") {
            show = true;
        }
        return show;
    };

    // If the dataset select changes update our pristine flag
    // the invalid flag needs to be handled manually since we
    // can have multiple datasets
    $scope.changeDataset = function(index) {
        $scope.pristineFlags.dataset[index].pid = false;
        if ($scope.policy.collections[index].type.name) {
            $scope.invalidFlags.dataset[index].pid = false;
        } else {
            $scope.invalidFlags.dataset[index].pid = true;
        }
    };

    // If the dataset coll is changed update the flags
    $scope.changeColl = function(index) {
        $scope.pristineFlags.dataset[index].coll = false;
        if ($scope.policy.collections[index].name &&
                $scope.policy.collections[index].name.length >= 3) {
            $scope.invalidFlags.dataset[index].coll = false;
        } else {
            $scope.invalidFlags.dataset[index].coll = true;
        }
    };

    // Call the action controller
    $injector.invoke(actionCtrl, this, {$scope: $scope});
}

function personalCtrl($scope, $rootScope, $injector, policy) {
    $scope.policy = policy;
    $scope.policy.uuid = createGuid();
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
}

function sourceTargetCtrl($scope, $http, $injector, policy, disabled_flags, 
        data_location, submitFlag) {
    $scope.policy = policy;
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
    var disabled_flags_obj = disabled_flags.getFlags();
    var loc_obj = data_location.getLocations();

    $scope.src_systems = loc_obj.source_systems;
    $scope.tgt_systems = loc_obj.target_systems;
    $scope.src_sites = loc_obj.source_sites;
    $scope.tgt_sites = loc_obj.target_sites;
    $scope.src_resources = loc_obj.source_resources;
    $scope.tgt_resources = loc_obj.target_resources;
    $scope.src_site_disabled = disabled_flags_obj.source_site;
    $scope.tgt_site_disabled = disabled_flags_obj.target_site;
    $scope.src_resource_disabled = disabled_flags_obj.source_resource;
    $scope.tgt_resource_disabled = disabled_flags_obj.target_resource;
    $scope.tgt_system_disabled = disabled_flags_obj.tgt_system;
    $scope.tgt_loc_type_disabled = disabled_flags_obj.tgt_loc_type;

    // Read from the database the available locations
    $scope.changeLocation = function() {
        $http({method: "GET", 
            url: "/cgi-bin/dpm/query_actions.py", 
            params: {qtype: "locations",
                 operation: $scope.policy.action.name,
                 type: $scope.policy.type.name,
                 trigger: $scope.policy.trigger.name
                 }}).success(function(data, 
                status, headers, config) {
                    loc_obj.location_types = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            loc_obj.location_types = 
                                storeData(loc_obj.location_types, 
                                    data[idx][0]);
                        }
                    }
                    $scope.location_types = loc_obj.location_types;
                    data_location.setLocations(loc_obj);
                    disabled_flags_obj.tgt_loc_type = false;
                    disabled_flags.setFlags(disabled_flags_obj);
                    $scope.pristineFlags.target.organisation = false;
                    $scope.policy.target.loctype.name = "--- Select a Location Type ---";
                    $scope.tgt_loc_type_disabled = disabled_flags_obj.tgt_loc_type;
 
        });
    };


    // Read from the database the available systems
    $scope.changeSystem = function() {
        $http({method: "GET", 
            url: "/cgi-bin/dpm/query_resource.py", 
            params: {qtype: "systems"}}).success(function(data, 
                status, headers, config) {
                    loc_obj.source_systems = [];
                    loc_obj.target_systems = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            loc_obj.source_systems = 
                                storeData(loc_obj.source_systems, 
                                    data[idx][0]);
                            loc_obj.target_systems = 
                                storeData(loc_obj.target_systems, 
                                    data[idx][0]);
                        }
                    }
                    $scope.src_systems = loc_obj.source_systems;
                    $scope.tgt_systems = loc_obj.target_systems; 
                    data_location.setLocations(loc_obj);
                    disabled_flags_obj.tgt_system = false;
                    disabled_flags.setFlags(disabled_flags_obj);
                    $scope.pristineFlags.target.location_type = false;
                    $scope.policy.target.system.name = "--- Select a System ---";
                    $scope.tgt_system_disabled = disabled_flags_obj.tgt_system;
        });
    };

    // Once the system has been selected populate the sites list for the
    // source
    $scope.changeSrcSite = function() {
        $http({method: "GET", 
            url: "/cgi-bin/dpm/query_resource.py", 
            params: {qtype: "sites", 
                system: $scope.policy.source.system.name}
        }).success(function(data, 
                status, headers, config) {
                    loc_obj.source_sites = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            loc_obj.source_sites = 
                                storeData(loc_obj.source_sites,
                                    data[idx][0]);
                        }
                    }
                    $scope.src_sites = loc_obj.source_sites;
                    data_location.setLocations(loc_obj);
                });
        disabled_flags_obj.source_site = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.policy.source.site.name = "--- Select a Site ---";
        $scope.src_site_disabled = disabled_flags_obj.source_site;
    };

    // Once the system has been selected populate the sites list
    $scope.changeTgtSite = function() {
        $http({method: "GET", 
            url: "/cgi-bin/dpm/query_resource.py", 
            params: {qtype: "sites", 
                system: $scope.policy.target.system.name}
        }).success(function(data, 
                status, headers, config) {
                    loc_obj.target_sites = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            $scope.tgt_sites =
                                storeData(loc_obj.target_sites, 
                                    data[idx][0]);
                        }
                    }
                });
        disabled_flags_obj.target_site = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.policy.target.site.name = "--- Select a Site ---";
        $scope.pristineFlags.target.system = false;
        $scope.tgt_site_disabled = disabled_flags_obj.target_site;
    };

    // Once the site has been selected populate the source resources list
    $scope.changeSrcResource = function() {
        $http({method: "GET",
            url: "/cgi-bin/dpm/query_resource.py",
            params: {qtype: "resources",
                system: $scope.policy.source.system.name,
                site: $scope.policy.source.site.name}
        }).success(function(data,
                status, headers, config) {
                    loc_obj.source_resources = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            $scope.src_resources =
                                storeData(loc_obj.source_resources,
                                    data[idx][0]);
                        }
                    }
            });
        disabled_flags_obj.source_resource = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.policy.source.resource.name = "--- Select a Resource ---";
        $scope.src_resource_disabled = disabled_flags_obj.source_resource;
    };

    // Once the site has been selected populate the resources list
    $scope.changeTgtResource = function() {
        $http({method: "GET",
            url: "/cgi-bin/dpm/query_resource.py",
            params: {qtype: "resources",
            system: $scope.policy.target.system.name,
            site: $scope.policy.target.site.name}
        }).success(function(data,
                status, headers, config) {
                    loc_obj.target_resources = [];
                    for (var idx = 0; idx < data.length; ++idx) {
                        if (data[idx].length > 0) {
                            $scope.tgt_resources =
                                storeData(loc_obj.target_resources, 
                                    data[idx][0]);
                        }
                    }
                });
        disabled_flags_obj.target_resource = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.pristineFlags.target.site = false;
        $scope.policy.target.resource.name = "--- Select a Resource ---";
        $scope.tgt_resource_disabled = disabled_flags_obj.target_resource;
 
    };

    // Function to update the pristine flag (we need this as the state
    // is not presered when we go back a page)
    $scope.updateTgtResource = function() {
        $scope.pristineFlags.target.resource = false;
    };
}

function submitCtrl($scope, $location, submitFlag, policy, pristineFlags, 
        invalidFlags, $http, page) {
    $scope.setSubmitted = function(validObj) {
        var flago = submitFlag.getObj();
        flago.fieldsOK = checkFields(validObj, pristineFlags, invalidFlags,
                flago);
        flago.active = true;
        flago.submitted = true;
        submitFlag.setObj(flago);
        $scope.submitted = flago.submitted;
    };
    $scope.submitForm = function () {
        var flago = submitFlag.getObj();
        if (flago.fieldsOK) {
            if (flago.active) {
                $location.url(locList[locList.length-1].url);
                page.count = locList.length - 1;
            }
        } else {
            if (flago.active) {
                alert("The form is invalid. Check fields for errors");
                flago.submitted = false;
            }
        }
    };
    $scope.confirmOK = function() {
        $http.post("/cgi-bin/dpm/storePolicy.py", JSON.stringify(policy),
                {headers: "Content-Type: application/x-www-form-urlencoded"})
            .success(function(data, status, headers, config) {
                alert("Policy successfully stored in the database");
                if (data.policy_exists) {
                    alert("The policy exists in the database");
                }
            }).error(function(data, status, headers, config) {
                alert("error is " + data);
            });

    };

}

function tabsCtrl($scope, $http, logPageList, polList, userProfile,
        policy) {
    $scope.hideLog = logPageList.hide;
    $scope.displayLog = logPageList.active;
    $scope.listPolicy = polList.active;
    // Get the username from the environment. We need a promise to
    // work with the results when ready
    userProfile.promise = $http({method: "GET",
        url: "/cgi-bin/dpm/getProfile.py"}).then(function(response) {
            var data = response.data;
            userProfile.username = data.profile[0].username;
            userProfile.email = data.profile[0].email;
            userProfile.communities = data.profile[0].communities;
            policy.author = data.profile[0].username;
            $scope.policy = policy;
    });
}

function checkFields(validObj, pristineFlagsObj, invalidFlagsObj, flago) {
    var fieldsOK = false;
 
    if (validObj) {
        fieldsOK = true;
        // We have to ignore the pristine flag in the case of
        // a person submitting and goes back to update the form
        // so we use our own flags
        if (!flago.submitted) {
            pristineFlagsObj.action.action = validObj.action.$pristine;
            pristineFlagsObj.action.type = validObj.type.$pristine;
            pristineFlagsObj.action.trigger = validObj.trigger.$pristine;
            pristineFlagsObj.target.organisation = validObj.organisation.$pristine;
            pristineFlagsObj.target.location_type = validObj.location_type.$pristine;
            pristineFlagsObj.target.system = validObj.system.$pristine;
            pristineFlagsObj.target.site = validObj.site.$pristine;
            pristineFlagsObj.target.resource = validObj.resource.$pristine;
        }

        // Loop over all the flags for the dataset pid. On the first true
        // set the valid flag to false and break out
        var i;
        for (i=0; i < pristineFlagsObj.dataset.length; i++) {
            if (pristineFlagsObj.dataset[i].pid === true ||
                    pristineFlagsObj.dataset[i].coll === true ||
                    invalidFlagsObj.dataset[i].pid === true ||
                    invalidFlagsObj.dataset[i].coll === true) {
                fieldsOK = false;
                break;
            }
        }

        if (pristineFlagsObj.action.action || validObj.action.$invalid) fieldsOK = false;
        if (pristineFlagsObj.action.type || validObj.type.$invalid) fieldsOK = false;
        if (pristineFlagsObj.action.trigger || validObj.trigger.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.organisation || validObj.organisation.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.location_type || validObj.location_type.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.system || validObj.system.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.site || validObj.site.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.resource || validObj.resource.$invalid) fieldsOK = false;
    }
    return fieldsOK;
}

dpmApp.service('data_action', function() {
    var actions = {types:[],
        operations:[], triggers:[], organisations:[]};
    return {
        getActions: function() {
            return actions;
        },
        setActions: function(loc) {
            actions = loc;
        }
    };
});

dpmApp.service('data_identifier', function() {
    var identifiers = {types:[]};
    return {
        getIdentifiers: function() {
            return identifiers;
        },
        setIdentifiers: function(loc) {
            identifiers = loc;
        }
    };
});

dpmApp.service('data_location', function() {
    var locations = {source_systems:[],
        source_sites:[], source_resources:[],
        target_systems:[], target_sites:[], 
        target_resources:[], location_types:[]};
    return {
        getLocations: function() {
            return locations;
        },
        setLocations: function(loc) {
            locations = loc;
        }
    };
});

dpmApp.service("disabled_flags", function() {
    var disabled_flags_obj = {action_type: true, action_trigger: true,
        tgt_loc_type: true, tgt_organisation: true,
        tgt_system: true, source_system: true,
        source_site: true, target_site: true,
        source_resource: true, target_resource: true};
    return {
        getFlags: function() {
            return disabled_flags_obj;
        },
        setFlags: function(obj) {
            disabled_flags_obj = obj;
        }
    };
});

dpmApp.factory('invalidFlag', function() {
    var validObj = {"policyName": false,
        "policyVersion": false,
        "policyAuthor": false,
        "policyCommunity": false
    };
    return validObj;
});

function invalidFlags() {
    var dataset = new Array({pid: true, coll: true});
    var invalids = {dataset: dataset};
    return invalids;
}
dpmApp.factory("invalidFlags", invalidFlags);

// Service for handling pages
var page = function() {
    this.firstPage = true;
    this.count = 0;
};
// Register the service with the module
dpmApp.service("page", page);

var policy = function() {
    var action = {name: "--- Select an Action ---"};
    var type = {name: "--- Select a Type ---"};
    var trigger = {name: "--- Select a Trigger ---"};
    var source_system = {name: "--- Select a System ---"};
    var source_site = {name: "--- Select a Site ---"};
    var source_resource = {name: "--- Select a Resource ---"};
    var target_system = {name: "--- Select a System ---"};
    var target_site = {name: "--- Select a Site ---"};
    var target_resource = {name: "--- Select a Resource ---"};
    var loctype = {name: "--- Select a Location type ---"};
    var organisation = {name: "--- Select an Organisation ---"};
    var weekday = {name: "*"};
    var day = {name: "*"};
    var month ={name: "*"};
    var hour = {name: "*"};
    var minute = {name: "*"};

    var period = {weekday: weekday, month: month, day: day, hour: hour,
        minute: minute};
    
    var source = {
        loctype: loctype,
        organisation: organisation,
        system: source_system,
        site: source_site,
        path: "",
        resource: source_resource
    };
    var target = {
        loctype: loctype,
        organisation: organisation,
        system: target_system,
        site: target_site,
        path: "",
        resource: target_resource
    };
    var collections = new Array({name: "", type: {name: ""}});

    var policyObj = {name: "",
        version: "", uuid: "", author: "", community: "", 
        collections: collections, 
        action: action,
        type: type,
        trigger: trigger,
        trigger_date: "",
        trigger_period: period,
        source: source, 
        target: target};
    return policyObj;
};

// create a factory to generate a policy object
dpmApp.factory("policy", policy);

function pristineFlags() {
    var dataset = new Array({pid: true, coll: true});
    var action = {action: true, type: true, trigger: true};
    var target = {organisation: true, location_type: true, system: true,
        site: true, resource: true}; 
    var pristine = {dataset: dataset, action: action, target: target};
    return pristine;
}

// Create a factory for the pristine flags
dpmApp.factory("pristineFlags", pristineFlags);

dpmApp.filter("startFrom", function() {
    return function(input, start) {
        start = +start;
        aslice = input.slice(start);
        return aslice;
    };
});

dpmApp.service('submitFlag', function() {
    var sflag = {flag: false, active: false, submitted: false, 
        fieldsOK: false, confirm: false};
    return {
        getObj: function() {
            return sflag;
        },
        setObj: function(valobj) {
            sflag = valobj;
        }
    };
});

dpmApp.factory("userProfileService", function($http) {
    $http({method: "GET",
        url: "/cgi-bin/dpm/getProfile.py"}).success(function(data, status,
                headers, config) {
                    userProfile.username = data.profile[0].username;
                    userProfile.email = data.profile[0].email;
                    userProfile.communities = data.profile[0].communities;
                    policy.author = data.profile[0].username;
                    $scope.policy = policy;
    });
});

dpmApp.directive("validateInputNumber", function() {
    return {
        restrict: 'A',
        require: "ngModel",
        link: function(scope, elem, attr, ctrl) {
            ctrl.$parsers.unshift(function(aval) {
                if (!isNaN(parseFloat(aval)) && isFinite(aval)) {
                    ctrl.$setValidity("required", true);
                    return aval;
                } else {
                    ctrl.$setValidity("required", false);
                    return undefined;
                }
            });
        }
    };
});

dpmApp.directive("validateSelect", function() {
    return {
        restrict: 'A',
        require: "ngModel",
        link: function(scope, elem, attrs, ctrl) {
            ctrl.$parsers.unshift(function(aval) {
                if (aval && aval.name !== "") {
                    ctrl.$setValidity("required", true);
                    return aval;
                } else {
                    ctrl.$setValidity("required", false);
                    return "";
                }
            });
        }
    };
});

dpmApp.factory('userProfile', function() {
    var profile = {"promise": undefined, "username": "", "email": "",
        "communities": ""};
    return profile;
});

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

dpmApp.service('logData', function() {
    var logDataObj = [];
    return {
        getObj: function() {
            return logDataObj;
        },
        setObj: function(valobj) {
            logDataObj = valobj;
        }
    };
});

dpmApp.factory('logPageList', function() {
    var logList = {"hide": true, "active": false};
    return logList;
});

function listCtrl($scope, $sce, $http, $filter, $location, logPageList,
        logData, policy, polList, userProfile, ngTableParams) {
    var keys = []; 

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

    // Get the policies from the database as well as the log information
    var dvals = [];
    var dataSave = [];
    
    // Since the population of the author is asynchronous we can only execute
    // when the author is filled we need to make use of the promise
    userProfile.promise.then(function (response) {
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
                        $scope.data = dvals;
                        // Also save a copy of the data for quicker access
                        // when using filtering
                        dataSave = dvals;
                        $scope.tabs = new ngTableParams({
                            page: 1,
                            count: 10},
                        {
                            total: $scope.data.length,
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

dpmApp.factory('polList', function() {
    var polList = {"hide": false, "active": true};
    return polList;
});
