//function tabsCtrl($scope, $http, logPageList, polList, userProfile,
//        policy) {
function tabsCtrl($scope, $http, logPageList, polList, policy) {
    $scope.hideLog = logPageList.hide;
    $scope.displayLog = logPageList.active;
    $scope.listPolicy = polList.active;
    // Get the username from the environment. We need a promise to
    // work with the results when ready
//    userProfile.promise = $http({method: "GET",
//        url: "/cgi-bin/dpm/getProfile.py"}).then(function(response) {
//            var data = response.data;
//            userProfile.username = data.profile[0].username;
//            userProfile.email = data.profile[0].email;
//            userProfile.communities = data.profile[0].communities;
//            policy.author = data.profile[0].username;
//            $scope.policy = policy;
//    });
}
