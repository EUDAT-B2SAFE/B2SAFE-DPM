function tabsCtrl($scope, $http, $interval, logPageList, $route, 
        polList, userProfile, policy, showLog, uuids) {
    $scope.list_url = "template/listtable.html";
    $scope.hideLog = logPageList.hide;
    $scope.displayLog = logPageList.active;
    $scope.listPolicy = polList.active;

    // Get the username from the environment. We need a promise to
    // work with the results when ready
    userProfile.promise = $http({method: "GET",
        url: "${CGI_URL}/getProfile.py"}).then(function(response) {
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
        // alert("parent scope function called " + turl);
        $scope.list_url = turl;
        $route.reload();
    };

    // Regularly check if access has timed-out, if so show  timeout page
    // Only show timeout page once
    var repeatCheck = $interval(function(){checkAccess($http);}, 900000, 0);

    // This code is no longer necessary as we don't do pop-ups
    /*
    if (checkLocalStorage()) {
        if (localStorage.getItem("session_renew")) {
            if (localStorage.getItem("session_renew") === "displayed") {
                $interval.cancel(repeatCheck);
            }
        } else {
            repeatCheck = $interval(function(){checkAccess($http);}, 9000, 0);
        }
    }
    $scope.$on('$destroy', function(){
        $interval.cancel(repeatCheck);
    });
    */
}
