function removeCtrl($scope, $http, $window, policy) {

    // Back to the list
    $scope.backToList = function() {
        $scope.$parent.changeLoc('template/listtable.html');
    };

    // Delete the policy
    $scope.removePolicy = function() {
        var resp = confirm('Are you sure?');
        if (resp === true) {
            var rmpolicy = $http({method: 'POST',
                url: '${CGI_URL}/removePolicy.py',
                data: angular.toJson({uuid: $scope.policy.saved_uuid,
                    policy: JSON.stringify($scope.policy),
                    name: $scope.policy.name, version: $scope.policy.version,
                    community: $scope.policy.community})});
            rmpolicy.then(function(response) {
                alert('Policy has been removed');
                $window.location.reload();
            });
        }
    };

    console.log("policy to be removed is " + JSON.stringify(policy));

    $scope.collDefined = function(coll) {
      var collFlag = false;
      if (coll.type.name === 'collection') {
          collFlag = true;
      }
      return collFlag;
    };

    $scope.pidDefined = function(coll) {
      var pidFlag = false;
      if (coll.type.name === 'pid') {
          pidFlag = true;
      }
      return pidFlag;
    };
}
