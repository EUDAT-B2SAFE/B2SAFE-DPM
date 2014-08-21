function personalCtrl($scope, $rootScope, $injector, policy) {
    $scope.policy = policy;
    $scope.policy.uuid = createGuid();
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
    $scope.changeCommunity = function(idx) {
    };
}
