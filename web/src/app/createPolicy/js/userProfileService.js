dpmApp.factory("userProfileService", function($http) {
    $http({method: "GET",
        url: "${CGI_URL}/getProfile.py"}).then(function(results) {
            var data = results.data;
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
