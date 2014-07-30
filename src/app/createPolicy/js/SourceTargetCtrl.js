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
