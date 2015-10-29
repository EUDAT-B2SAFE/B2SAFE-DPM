function datasetCtrl($scope, $http, $injector, data_identifier, policy,
        pristineFlags, invalidFlags, disabled_flags, data_location,
        submitFlag) {
    $scope.policy = policy;
    $scope.pristineFlags = pristineFlags;
    $scope.invalidFlags = invalidFlags;
    var disabled_flags_obj = disabled_flags.getFlags();
    $scope.src_system_disabled = disabled_flags_obj.source_system;
    var loc_obj = data_location.getLocations();

    // Call the base dpm controller for the next/previous pages
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
    var identifier_obj = data_identifier.getIdentifiers();

    // Read in the available identifier types using promises to avoid
    // problems with asynch calls
    var get_identifiers = $http({method: 'GET',
                    url: '${CGI_URL}/query_actions.py',
                    params: {qtype: 'identifiers'}});

    get_identifiers.then(function(results) {
        var data = results.data;
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                identifier_obj.types = storeData(identifier_obj.types,
                    data[idx][0]);
            }
        }
        $scope.identifier_types = identifier_obj.types;
        data_identifier.setIdentifiers(identifier_obj);
    });

    $scope.currentPage = 0;

    $scope.addMore = function() {
        ds_count += 1;
        var id = 'dataset_' + ds_count;
        var flago = submitFlag.getObj();
        flago.active = false;
        submitFlag.setObj(flago);
        $scope.policy.collections.push({name: '', type: {name: ''}});
        $scope.invalidFlags.dataset.push({pid: true, coll: true});
        $scope.pristineFlags.dataset.push({pid: true, coll: true});
        $scope.pristineFlags.sources.push({organisation: true,
          location_type: true, system: true, site: true, resource: true});
        $scope.policy.sources.push({loctype: '', organisation: '',
          system: '', site: '', path: '', resource: ''
        });
        $scope.submitted = false;
        $scope.invalidFlags.source.push({organisation: true, system: true,
          site: true, resource: true});
    };
    $scope.numberOfPages = function() {
        return Math.ceil($scope.policy.collections.length/3);
    };
    $scope.removeCollection = function(array, index) {
        array.splice(index, 1);
    };

    // Show the source collection for the collection option
    $scope.showSrcColl = function(trname) {
      var show = false;
      var tname = trname.replace(/^\s+|\s+$/g, '');
      if (tname === 'collection') {
        show = true;
      }
      return show;
    };

    // Only show the collection fields for the PID option
    $scope.showCollection = function(trname) {
        var show = false;
        var tname = trname.replace(/^\s+|\s+$/g, '');
        if (tname === 'pid') {
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
        if ($scope.policy.collections[index].type.name === 'collection') {
          changeSrcOrganisation(index);
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

    // Get the systems from the database
    $scope.changeSourceSystem = function (index) {
      var default_org = '--- Select an Organisation ---';
      var get_systems = $http({method: 'GET',
        url: '${CGI_URL}/query_resource.py',
        params: {qtype: 'systems'}});

        get_systems.then(function(results) {
            var data = results.data;
            loc_obj.source_systems = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    loc_obj.source_systems =
                        storeData(loc_obj.source_systems, data[idx][0]);
                }
            }
            $scope.src_systems = loc_obj.source_systems;
            data_location.setLocations(loc_obj);
            disabled_flags_obj.source_system = false;
            disabled_flags.setFlags(disabled_flags_obj);
            $scope.pristineFlags.sources[index].location_type = false;
            $scope.policy.sources[index].system.name = '--- Select a System ---';
            $scope.src_system_disabled = disabled_flags_obj.source_system;
        });

        // Set the validation flags for the organisation
        $scope.pristineFlags.sources[index].organisation = false;
        if ($scope.policy.sources[index].organisation.name &&
            $scope.policy.sources[index].organisation.name != default_org) {
            $scope.invalidFlags.source[index].organisation = false;
        } else {
            $scope.invalidFlags.source[index].organisation = true;
        }
    };

    // Get the organisations for the sources
    function changeSrcOrganisation(index) {
        var default_org = '--- Select an Organisation ---';
        var get_organisations = $http({method: 'GET',
            url: '${CGI_URL}/query_actions.py',
            params: {qtype: 'organisations'}});

        get_organisations.then(function(results) {
            var data = results.data;
            loc_obj.source_organisations = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    loc_obj.source_organisations =
                        storeData(loc_obj.source_organisations, data[idx][0]);
                }
            }
            $scope.organisations = loc_obj.source_organisations;
            data_location.setLocations(loc_obj);
            disabled_flags_obj.source_organisation = false;
            disabled_flags.setFlags(disabled_flags_obj);
            $scope.policy.sources[index].organisation.name = default_org;
            $scope.src_organisation_disabled = disabled_flags_obj.source_organisation;

            // Set the validation flags
            $scope.pristineFlags.sources[index].organisation = false;
            if ($scope.policy.sources[index].organisation.name &&
                $scope.policy.sources[index].organisation.name !=
                default_org) {
                $scope.invalidFlags.source[index].organisation = false;
            } else {
              $scope.invalidFlags.source[index].organisation = true;
            }
        });
    }
}
