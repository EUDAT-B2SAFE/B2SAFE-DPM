function confirmCtrl($scope, $injector, page, submitFlag, policy) {
    $scope.policy = policy;
    $injector.invoke(dpmCtrl, this, {$scope: $scope});
    // We need to reset the active flag so we don't automatically
    // trigger the submitForm code
    var flago = submitFlag.getObj();
    flago.active = false;
    flago.flag = false;
    flago.confirm = true;
    submitFlag.setObj(flago);
}
