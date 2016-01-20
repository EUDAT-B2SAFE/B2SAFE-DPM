function sourceTargetCtrl($scope, $http, $controller, policy,
        dataLocation, submitFlag) {
    $scope.policy = policy;
    // $injector.invoke(dpmCtrl, {$scope: $scope});
    $controller('dpmCtrl', {$scope: $scope});

    var loc_obj = dataLocation.getLocations();

    $scope.src_systems = loc_obj.source_systems;
    $scope.tgt_systems = loc_obj.target_systems;
    $scope.src_sites = loc_obj.source_sites;
    $scope.tgt_sites = loc_obj.target_sites;
    $scope.src_resources = loc_obj.source_resources;
    $scope.tgt_resources = loc_obj.target_resources;

    // Read from the database the available systems
    $scope.changeTgtSystem = function() {
        var get_systems = $http({method: "GET",
            url: "${CGI_URL}/query_resource.py",
            params: {qtype: "systems"}});

        get_systems.then(function(results) {
            var data = results.data;
            loc_obj.source_systems = [];
            loc_obj.target_systems = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    loc_obj.source_systems =
                        storeData(loc_obj.source_systems, data[idx][0]);
                    loc_obj.target_systems =
                        storeData(loc_obj.target_systems, data[idx][0]);
                }
            }
            $scope.src_systems = loc_obj.source_systems;
            $scope.tgt_systems = loc_obj.target_systems;
            data_location.setLocations(loc_obj);
            $scope.pristineFlags.target.organisation = false;
            $scope.policy.target.system.name = "iRODS";
        });
    };

    // Once the system has been selected populate the sites list for the
    // source
    $scope.changeSrcSite = function(index) {
        var default_system = "iRODS";
        var get_sites = $http({method: "GET",
            url: "${CGI_URL}/query_resource.py",
            params: {qtype: "sites",
                system: $scope.policy.sources[index].system.name}});

        get_sites.then(function(results) {
            var data = results.data;
            loc_obj.source_sites = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    loc_obj.source_sites =
                        storeData(loc_obj.source_sites, data[idx][0]);
                }
            }
            $scope.src_sites = loc_obj.source_sites;
            data_location.setLocations(loc_obj);
        });
        $scope.policy.sources[index].hostname.name = "--- Select a Site ---";

        // Set the validation flags for the System
        $scope.pristineFlags.sources[index].system = false;
        if ($scope.policy.sources[index].system.name &&
            $scope.policy.sources[index].system.name !=
            default_system) {
            $scope.invalidFlags.source[index].system = false;
        } else {
            $scope.invalidFlags.source[index].system = true;
        }
    };

    // Once the system has been selected populate the sites list
    $scope.changeTgtSite = function() {
        var get_tgtsites = $http({method: "GET",
            url: "${CGI_URL}/query_resource.py",
            params: {qtype: "sites",
                system: $scope.policy.target.system.name} });
        get_tgtsites.then(function(results) {
            var data = results.data;
            loc_obj.target_sites = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    $scope.tgt_sites =
                        storeData(loc_obj.target_sites, data[idx][0]);
                }
            }
        });
        $scope.policy.target.hostname.name = "--- Select a Site ---";
        $scope.pristineFlags.target.system = false;
    };

    $scope.updateSrcResource = function(index) {
      var default_resource = "--- Select a Resource ---";
      var idx = $scope.src_resources.indexOf(
        $scope.policy.sources[index].resource);
      $scope.policy.sources[index].path = $scope.src_paths[idx].name;
      $scope.pristineFlags.sources[index].resource = false;
      if ($scope.policy.sources[index].resource.name &&
         $scope.policy.sources[index].resource.name !=
         default_resource) {
         $scope.invalidFlags.source[index].resource = false;
      } else {
         $scope.invalidFlags.source[index].resource = true;
      }
    };

    // Function to update the pristine flag (we need this as the state
    // is not presered when we go back a page)
    $scope.updateTgtResource = function() {
      var idx = $scope.tgt_resources.indexOf($scope.policy.target.resource);
      $scope.policy.target.path = $scope.tgt_paths[idx].name;
      $scope.pristineFlags.target.resource = false;
    };
}
