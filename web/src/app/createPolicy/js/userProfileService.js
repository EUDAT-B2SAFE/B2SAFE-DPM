dpmApp.factory("userProfileService", function($http) {
    $http({method: "GET",
        url: "/cgi-bin/dpm/getProfile.py"}).success(function(data, status,
                headers, config) {
                    userProfile.username = data.profile[0].username;
                    userProfile.email = data.profile[0].email;
                    userProfile.communities = data.profile[0].communities;
                    if (userProfile.communities.length === 1) {
                        $scope.community_number = "one";
                    } else {
                        $scope.community_number = "many";
                    }
                    policy.author = data.profile[0].username;
                    $scope.policy = policy;
    });
});
