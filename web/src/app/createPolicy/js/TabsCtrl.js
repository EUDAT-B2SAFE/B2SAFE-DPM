function tabsCtrl($scope, $http, logPageList, $route, polList, userProfile,
        policy) {
    $scope.list_url = "template/listtable.html";
    $scope.hideLog = logPageList.hide;
    $scope.displayLog = logPageList.active;
    $scope.listPolicy = polList.active;
    // Get the username from the environment. We need a promise to
    // work with the results when ready
    userProfile.promise = $http({method: "GET",
        url: "/cgi-bin/dpm/getProfile.py"}).then(function(response) {
            var data = response.data;
            userProfile.username = data.profile[0].username;
            userProfile.email = data.profile[0].email;
            userProfile.communities = data.profile[1].communities;
            if (userProfile.communities.length === 1) {
                $scope.community_number = "one";
                $scope.communities = userProfile.communities[0];
                policy.community = userProfile.communities[0];
            } else {
                $scope.community_number = "many";
                $scope.communities = userProfile.communities;
            }
            policy.author = data.profile[0].username;
            $scope.policy = policy;
    });

    // Function to change the location of the for the list view
    $scope.changeLoc = function (turl) {
        alert("parent scope function called " + turl);
        $scope.list_url = turl;
        $route.reload();
    };
}
