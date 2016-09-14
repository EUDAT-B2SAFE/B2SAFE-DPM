function datasetCtrl($scope, $http, $controller, $injector, data_identifier,
  policy, pristineFlags, invalidFlags, dataLocation, identifierFlags,
        submitFlag) {
    $scope.policy = policy;
    $scope.src_policies = [];
    $scope.showSrcPolColl = false;
    $scope.showSrcPolPid = false;
    $scope.showSrcColl = identifierFlags.showSrcColls;
    $scope.showTgtColl = identifierFlags.showTgtColls;
    $scope.showSrcPID = identifierFlags.showSrcPIDs;
    $scope.showTgtPID = identifierFlags.showTgtPIDs;
    $scope.showSrcPolicy = identifierFlags.showSrcPolicy;
    $scope.pristineFlags = pristineFlags;
    $scope.invalidFlags = invalidFlags;
    var locations = dataLocation.getLocations();
    var collType = '';
    $scope.policy.policy_action_id.name = "--- Select ---";

    // Call the base dpm controller for the next/previous pages
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
    var identifiers = data_identifier.getIdentifiers();

    // Read in the available identifier types using promises to avoid
    // problems with asynch calls
    var getIdentifiers = $http({method: 'GET',
                    url: '${CGI_URL}/query_actions.py',
                    params: {qtype: 'identifiers'}});

    getIdentifiers.then(function(results) {
        var data = results.data;
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                identifiers.types = storeData(identifiers.types,
                    data[idx][0]);
            }
        }
        $scope.identifier_types = identifiers.types;
        $scope.target_identifier_types = [];
        for (var i = 0; i < identifiers.types.length; i++) {
          if (identifiers.types[i].name !== "policy") {
            $scope.target_identifier_types.push({'name':
              identifiers.types[i].name});
          }
        }
        data_identifier.setIdentifiers(identifiers);
    });

    $scope.currentPage = 0;

// TODO
// The code below needs updating to allow adding more than one source
// Unclear about datasets at the moment
/*
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
*/

    // When the source or target type is selected we populate the
    // select menus and display the correct fields
    $scope.typeSelected = function(index, ctype) {
      collType = ctype;
      var hosts = $http({method: 'GET', url: '${CGI_URL}/query_resource.py',
                        params: {qtype: 'sitePath'}});

      hosts.then(function(results) {
        var data = results.data;
        console.log('data is ' + JSON.stringify(data));

        locations.source_sites = [];
        locations.target_sites = [];
        locations.source_collections = [];

        locations.target_collections = [];
        for (var idx = 0; idx < data.length; ++idx) {
          if (data[idx].length > 0) {
            locations.source_sites.push({name: data[idx][0]});
            locations.target_sites.push({name: data[idx][0]});
            locations.source_collections.push({name: data[idx][1]});
            locations.target_collections.push({name: data[idx][1]});
          }
        }

        $scope.src_sites = locations.source_sites;
        $scope.tgt_sites = locations.target_sites;

        dataLocation.setLocations(locations);

        // Show the correct fields depending on the type chosen
        var typeName = '';
        if (ctype === 'source') {
          $scope.pristineFlags.sources[index].location_type = false;
          typeName = $scope.policy.sources[index].type.name.replace(/^\s+|\s+$/g, '');
          if (typeName === 'collection') {
            $scope.invalidFlags.sources[index].coll = false;
            $scope.pristineFlags.sources[index].coll = false;
            $scope.showSrcColl[index] = true;
            $scope.showSrcPolColl = false;
            $scope.showSrcPolicy[index] = false;
            $scope.showSrcPID[index] = false;
          } else if (typeName === 'pid') {
            $scope.invalidFlags.sources[index].pid = false;
            $scope.pristineFlags.sources[index].pid = false;
            $scope.showSrcPID[index] = true;
            $scope.showSrcPolColl = false;
            $scope.showSrcPolicy[index] = false;
            $scope.showSrcColl[index] = false;
          } else if (typeName === 'policy') {
            $scope.invalidFlags.sources[index].identifier = false;
            $scope.pristineFlags.sources[index].identifier = false;
            $scope.showSrcPID[index] = false;
            $scope.showSrcColl[index] = false;
            getPolicies(index);
          }
        }
        if (ctype === 'target') {
          $scope.pristineFlags.targets[index].location_type = false;
          typeName = $scope.policy.targets[index].type.name.replace(/^\s+|\s+$/g, '');
          if (typeName === 'collection') {
            $scope.pristineFlags.targets[index].coll = false;
            $scope.invalidFlags.targets[index].coll = false;
            $scope.showTgtColl[index] = true;
            $scope.showTgtPID[index] = false;
          } else if (typeName === 'pid') {
            $scope.invalidFlags.targets[index].pid = false;
            $scope.pristineFlags.targets[index].pid = false;
            $scope.showTgtPID[index] = true;
            $scope.showTgtColl[index] = false;
          }
        }
      });
    };

    function getCollIndex(site_name, sites) {
      var locIndex;
      var collIndex = -1;
      for (locIndex = 0; locIndex <= sites.length; locIndex++) {
        if (sites[locIndex].name === site_name) {
          collIndex = locIndex;
          break;
        }
      }
      return collIndex;
    }

    $scope.updateCollection = function(index, type) {
      var collIndex = -1;
      if (type === 'source') {
        $scope.pristineFlags.sources[index].pid = false;
        $scope.pristineFlags.sources[index].col = false;
        $scope.pristineFlags.sources[index].site = false;
        $scope.invalidFlags.sources[index].pid = false;
        $scope.invalidFlags.sources[index].col = false;
        collIndex = getCollIndex($scope.policy.sources[index].hostname.name,
          locations.source_sites);
        var sourceCopy = [];
        for (var i = 0; i < locations.source_collections.length; i++) {
          sourceCopy.push({'name': locations.source_collections[i].name});
        }
        $scope.policy.sources[index].identifier = sourceCopy[collIndex];
      } else if (type === 'target') {
        $scope.pristineFlags.targets[index].col = false;
        $scope.pristineFlags.targets[index].pid = false;
        $scope.pristineFlags.targets[index].site = false;
        $scope.invalidFlags.targets[index].col = false;
        $scope.invalidFlags.targets[index].pid = false;
        collIndex = getCollIndex($scope.policy.targets[index].hostname.name,
          locations.target_sites);
        var targetCopy = [];
        for (var j = 0; j < locations.target_collections.length; j++) {
          targetCopy.push({'name': locations.target_collections[j].name});
        }
        $scope.policy.targets[index].identifier = targetCopy[collIndex];
      }
    };

    // Get the policies from the database
    var policy_data = [];
    function getPolicies(index) {
      var policies = $http({method: 'GET', url: '${CGI_URL}/fetch_policies.py'});
      policies.then(function(results) {
        policy_data = results.data;
        // We want to now pre-fill the policies with values
        var pol_ids = [];
        for (var i = 0; i < policy_data.length; i++) {
          pol_ids.push({"name": policy_data[i].uniqueid});
        }
        $scope.src_policies[index] = pol_ids;
        $scope.showSrcPolicy[index] = true;
        $scope.policy.sources[index].hostname.name = "";
        $scope.policy.sources[index].identifier.name = "";
      });
    }

    $scope.updateSrcPolicy = function(index, ptype) {
      console.log("identifier is " + JSON.stringify($scope.policy.policy_action_id.name));
      $scope.pristineFlags.identifiers[index].name = false;
      for (var i = 0; i < policy_data.length; i++) {
        if ($scope.policy.policy_action_id.name === policy_data[i].uniqueid) {
          $scope.policy.sources[index].type.name = policy_data[i].type;
          if (policy_data[i].type === "collection") {
            $scope.showSrcPolColl = true;
            $scope.showSrcPolPid = true;
            $scope.pristineFlags.sources[index].site = false;
            $scope.pristineFlags.sources[index].coll = false;
            $scope.invalidFlags.sources[index].coll = false;
            $scope.policy.sources[index].hostname.name =
              policy_data[i].irodssite;
            $scope.policy.sources[index].identifier.name =
              policy_data[i].irodspath;
          } else if (policy_data[i].type === "pid") {
            $scope.showSrcPolPid = true;
            $scope.showSrcPolColl = false;
            $scope.invalidFlags.sources[index].pid = false;
            $scope.pristineFlags.sources[index].pid = false;
            $scope.policy.sources[index].hostname.name = "";
            $scope.policy.sources[index].identifier.name =
              policy_data[i].persistentIdentifier;
          }
        }
      }
    };

    // If the dataset coll is changed update the flags
    $scope.changeColl = function(index, location, type) {
      console.log('changeColl called ' + index + ' ' + location + ' ' + type);
      if (location === 'source') {
        if (type === 'collection') {
          $scope.pristineFlags.sources[index].coll = false;
          $scope.invalidFlags.sources[index].coll =
            checkFieldsValid('sources', index);
        } else if (type === 'pid') {
          $scope.pristineFlags.sources[index].pid = false;
          $scope.invalidFlags.sources[index].pid =
            checkFieldsValid('sources', index);
        }
      } else if (location === 'target') {
        if (type === 'collection') {
          $scope.pristineFlags.targets[index].coll = false;
          $scope.invalidFlags.targets[index].coll =
            checkFieldsValid('targets',index);
        } else if (type === 'pid') {
          $scope.pristineFlags.targets[index].pid = false;
          $scope.invalidFlags.targets[index].pid =
            checkFieldsValid('targets', index);
        }
      }
    };

    function checkFieldsValid(location, index) {
      var invalid = true;
      if ($scope.policy[location][index].identifier.name &&
          $scope.policy[location][index].identifier.name.length >= 3) {
            invalid = false;
      } else {
          invalid = true;
      }
      console.log('location ' + location + ' index ' + index + ' invalid ' + invalid);
      return invalid;
    }

    // Call the action controller
    $controller('actionCtrl', {$scope: $scope});

    // Get the systems from the database
    $scope.changeSourceSystem = function (index) {
      var default_org = '--- Select an Organisation ---';

        // Set the validation flags for the organisation
        $scope.pristineFlags.sources[index].organisation = false;
        if ($scope.policy.sources[index].organisation.name &&
            $scope.policy.sources[index].organisation.name != default_org) {
            $scope.invalidFlags.source[index].organisation = false;
        } else {
            $scope.invalidFlags.source[index].organisation = true;
        }
    };
}
