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
    $scope.policy.policy_action_id.name = "";

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
        $scope.tgt_id_types = [];
        $scope.id_types = [];
        for (var i = 0; i < identifiers.types.length; i++) {
          if (identifiers.types[i].name !== "policy") {
            $scope.target_identifier_types.push({'name':
              identifiers.types[i].name});
            $scope.tgt_id_types.push(identifiers.types[i].name);
          }
          $scope.id_types.push(identifiers.types[i].name);
        }
        data_identifier.setIdentifiers(identifiers);
    });

    $scope.currentSourcePage = 0;
    $scope.currentTargetPage = 0;
    $scope.showAddSources = true;
    $scope.showAddTargets = true;

    $scope.addMoreSources = function() {
        $scope.showAddTargets = false;
        var flags = submitFlag.getObj();
        flags.active = false;
        submitFlag.setObj(flags);
        if (typeof $scope.polChanged !== "undefined") {
            $scope.polChanged.sources.push({pid: null, collection: null, policy: null,
                                            hostname: null, identifier: null});
        }
        $scope.policy.sources.push({identifier: {name: ''}, hostname: '', type: '',
            organisation: {name: 'EUDAT'}, system: '', resource: {name: ''}});
        $scope.pristineFlags.sources.push({organisation: true,
          location_type: true, system: true, site: true, resource: true});
        $scope.invalidFlags.sources.push({coll: true, pid: true});
        $scope.currentSourcePage = Math.ceil($scope.policy.sources.length/3) - 1;
    };
    $scope.numberOfSourcePages = function() {
        return Math.ceil($scope.policy.sources.length/3);
    };
    $scope.removeSourceCollection = function(array, index) {
        array.splice(index, 1);
    };


    $scope.addMoreTargets = function() {
        $scope.showAddSources = false;
        var flago = submitFlag.getObj();
        flago.active = false;
        submitFlag.setObj(flago);
        if (typeof $scope.polChanged !== "undefined") {
            $scope.polChanged.targets.push({pid: null, collection: null,
                                            hostname: null, identifier: null});
        }
        $scope.policy.targets.push({identifier: '', hostname: '', type: '',
            organisation: {name: 'EUDAT'}, system: '', resource: {name: ''}});
        $scope.pristineFlags.targets.push({organisation: true,
          location_type: true, system: true, site: true, resource: true});
        $scope.invalidFlags.targets.push({coll: true, pid: true});
        $scope.currentTargetPage = Math.ceil($scope.policy.targets.length/3) - 1;
    };
    $scope.numberOfTargetPages = function() {
        return Math.ceil($scope.policy.targets.length/3);
    };
    $scope.removeSource = function(array, index) {
        array.splice(index, 1);
        if (array.length === 1) {
            $scope.showAddTargets = true;
        }
        if (typeof $scope.polChanged !== "undefined") {
            $scope.polChanged.sources.splice(index, 1);
        }
        $scope.pristineFlags.sources.splice(index, 1);
        $scope.invalidFlags.sources.splice(index, 1);
    };
    $scope.removeTarget = function(array, index) {
        array.splice(index, 1);
        if (array.length == 1) {
            $scope.showAddSources = true;
        }
        if (typeof $scope.polChanged !== "undefined") {
            $scope.polChanged.targets.splice(index, 1);
        }
        $scope.pristineFlags.targets.splice(index, 1);
        $scope.invalidFlags.targets.splice(index, 1);
    };



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
          if ($scope.pristineFlags.sources.length - 1 < index) {
              $scope.pristineFlags.sources.push({});
              $scope.invalidFlags.sources.push({});
          }
          $scope.pristineFlags.sources[index].location_type = false;
          typeName = $scope.policy.sources[index].type.name.replace(/^\s+|\s+$/g, '');
          if (typeName === 'collection') {
              if (typeof $scope.origPolicy !== "undefined") {
                  if ($scope.origPolicy.sources.length < $scope.policy.sources.length || 
                          $scope.origPolicy.sources[index].type.name !== typeName) {
                      $scope.polChanged.sources[index].collection = true;
                      $scope.polChanged.sources[index].pid = false;
                      $scope.polChanged.sources[index].policy = false;
                      $scope.policy.sources[index].identifier.name = "";
                      $scope.policy.sources[index].hostname.name = "--- Select ---";
                   } else {
                      $scope.policy.sources[index].identifier.name = $scope.origPolicy.sources[index].identifier.name;
                      $scope.policy.sources[index].hostname.name = $scope.origPolicy.sources[index].hostname.name;
                   }
              }
            $scope.invalidFlags.sources[index].coll = false;
            $scope.pristineFlags.sources[index].coll = false;
            $scope.policy.policy_action_id.name = "";
            $scope.showSrcColl[index] = true;
            $scope.showSrcPolColl = false;
            $scope.showSrcPolicy[index] = false;
            $scope.showSrcPID[index] = false;
          } else if (typeName === 'pid') {
              if (typeof $scope.origPolicy !== "undefined") {
                  if ($scope.origPolicy.sources.length < $scope.policy.sources.length ||
                          $scope.origPolicy.sources[index].type.name !== typeName) {
                      $scope.polChanged.sources[index].collection = false;
                      $scope.polChanged.sources[index].pid = true;
                      $scope.polChanged.sources[index].policy = false;
                      $scope.policy.sources[index].identifier.name = "";
                      $scope.policy.sources[index].hostname.name = "--- Select ---";
                   } else {
                      $scope.policy.sources[index].identifier.name = $scope.origPolicy.sources[index].identifier.name;
                      $scope.policy.sources[index].hostname.name = $scope.origPolicy.sources[index].hostname.name;
                   }
              }
            $scope.invalidFlags.sources[index].pid = false;
            $scope.pristineFlags.sources[index].pid = false;
            $scope.policy.policy_action_id.name = "";
            $scope.showSrcPID[index] = true;
            $scope.showSrcPolColl = false;
            $scope.showSrcPolicy[index] = false;
            $scope.showSrcColl[index] = false;
          } else if (typeName === 'policy') {
               if (typeof $scope.origPolicy !== "undefined") {
                  if ($scope.origPolicy.sources.length < $scope.policy.sources.length ||
                          $scope.origPolicy.sources[index].type.name !== typeName) {
                      $scope.polChanged.sources[index].collection = false;
                      $scope.polChanged.sources[index].pid = false;
                      $scope.polChanged.sources[index].policy = true;
                      $scope.policy.sources[index].identifier.name = "";
                      $scope.policy.sources[index].hostname.name = "--- Select ---";
                   } else {
                      $scope.policy.sources[index].identifier.name = $scope.origPolicy.sources[index].identifier.name;
                      $scope.policy.sources[index].hostname.name = $scope.origPolicy.sources[index].hostname.name;
                   }
              }
            $scope.invalidFlags.sources[index].identifier = false;
            $scope.pristineFlags.sources[index].identifier = false;
            $scope.policy.policy_action_id.name = "--- Select ---";
            $scope.showSrcPID[index] = false;
            $scope.showSrcColl[index] = false;
            getPolicies(index);
          }
        }
        if (ctype === 'target') {
          if ($scope.pristineFlags.targets.length - 1 < index) {
              $scope.pristineFlags.targets.push({});
              $scope.invalidFlags.targets.push({});
          }
          $scope.pristineFlags.targets[index].location_type = false;
          typeName = $scope.policy.targets[index].type.name.replace(/^\s+|\s+$/g, '');
          if (typeName === 'collection') {
              if (typeof $scope.origPolicy !== "undefined") {
                  if ($scope.origPolicy.targets.length < $scope.policy.targets.length ||
                          $scope.origPolicy.targets[index].type.name !== typeName) {
                      $scope.polChanged.targets[index].collection = true;
                      $scope.polChanged.targets[index].pid = false;
                      $scope.policy.targets[index].identifier.name = "";
                      $scope.policy.targets[index].hostname.name = "--- Select ---";
                   } else {
                      $scope.policy.targets[index].identifier.name = $scope.origPolicy.targets[index].identifier.name;
                      $scope.policy.targets[index].hostname.name = $scope.origPolicy.targets[index].hostname.name;
                   }
              }
            $scope.pristineFlags.targets[index].coll = false;
            $scope.invalidFlags.targets[index].coll = false;
            $scope.showTgtColl[index] = true;
            $scope.showTgtPID[index] = false;
          } else if (typeName === 'pid') {
              if (typeof $scope.origPolicy !== "undefined") {
                  if ($scope.origPolicy.targets.length < $scope.policy.targets.length ||
                          $scope.origPolicy.targets[index].type.name !== typeName) {
                      $scope.polChanged.targets[index].pid = true;
                      $scope.polChanged.targets[index].collection = false;
                      $scope.policy.targets[index].identifier.name = "";
                      $scope.policy.targets[index].hostname.name = "--- Select ---";
                   } else {
                      $scope.policy.targets[index].identifier.name = $scope.origPolicy.targets[index].identifier.name;
                      $scope.policy.targets[index].hostname.name = $scope.origPolicy.targets[index].hostname.name;
                   }
              }
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
        if (typeof $scope.origPolicy !== "undefined") {
           $scope.polChanged.sources[index].hostname = true;
        }
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
        if (typeof $scope.origPolicy !== "undefined") {
           $scope.polChanged.targets[index].hostname = true;
        }
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
      var policies = $http({method: 'GET', url: '${CGI_URL}/fetch_policies.py',
                            params: {community: $scope.policy.community}});
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
      $scope.pristineFlags.identifiers[index].name = false;
      if (typeof $scope.origPolicy !== "undefined") {
         $scope.polChanged.sources[index].type = true;
      }
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
      if (location === 'source') {
          if (typeof $scope.origPolicy !== "undefined") {
             $scope.polChanged.sources[index].identifier = true;
             if (type === 'collection') {
                 $scope.polChanged.sources[index].collection = true;
             }
             if (type === 'pid') {
                 $scope.polChanged.sources[index].pid = true;
             }
             if (type === 'policy') {
                 $scope.polChanged.sources[index].policy = true;
             }
          }
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
          if (typeof $scope.origPolicy !== "undefined") {
             $scope.polChanged.targets[index].identifier = true;
             if (type === 'collection') {
                 $scope.polChanged.targets[index].collection = true;
             }
             if (type === 'pid') {
                 $scope.polChanged.targets[index].pid = true;
             }
          }
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
