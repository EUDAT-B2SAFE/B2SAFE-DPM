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
        if (tname == "pid") {
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
