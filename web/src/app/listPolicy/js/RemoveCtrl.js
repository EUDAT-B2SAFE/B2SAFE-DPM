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
                data: angular.toJson({uuid: $scope.policy.saved_uuid})});
            rmpolicy.then(function(response) {
                alert('Policy has been removed');
                $window.location.reload();
            });
        }
    };

    // console.log("policy is " + JSON.stringify(policy));

    $scope.collDefined = function() {
      var collFlag = false;
      var i = 0;
      for (i = 0; i < $scope.policy.collections.length; i++) {
        if ($scope.policy.collections[i].type === 'collection') {
          collFlag = true;
          break;
        }
      }
      return collFlag;
    };

    $scope.pidDefined = function() {
      var pidFlag = false;
      var i = 0;
      for (i = 0; i < $scope.policy.collections.length; i++) {
        if ($scope.policy.collections[i].type === 'pid') {
          pidFlag = true;
          break;
        }
      }
      return pidFlag;
    };
}
