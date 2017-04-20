function reactivateCtrl($scope, $http, $window, policy) {

    // Back to the list
    $scope.backToList = function() {
        $scope.$parent.changeLoc("template/listtable.html");
    };

    // Reactivate the policy
    // This means marking the policy as not being deleted
    $scope.reactivatePolicy = function() {
        var resp = confirm("Are you sure?");
        if (resp === true) {
            var reactivatepolicy = $http({method: "POST",
                url: "${CGI_URL}/reactivatePolicy.py",
                data: angular.toJson({uuid: $scope.policy.saved_uuid,
                policy: JSON.stringify($scope.policy),
                name: $scope.policy.name,
                version: $scope.policy.version,
                community: $scope.policy.community})});
            reactivatepolicy.then(function(response) {
                alert("The policy has been reactivated");
                $window.location.reload();
            });
        }
    };

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
