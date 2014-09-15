function removeCtrl($scope, $http, policy) {
   
    // Back to the list
    $scope.backToList = function() {
        $scope.$parent.changeLoc("template/listtable.html");
    };

    // Delete the policy
    $scope.removePolicy = function() {
        var rmpolicy = $http({method: "POST", 
            url: "/cgi-bin/dpm/removePolicy.py",
            data: angular.toJson({uuid: $scope.policy.saved_uuid})});
        rmpolicy.then(function(response) {
            alert("Policy has been removed");
        });
    };
}