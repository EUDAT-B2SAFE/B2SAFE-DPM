function adminProfileCtrl($scope, $http, reqAction, ngTableParams) {
    $scope.data = [];
    $scope.show_msg = false;
    $scope.profile_cols = [];
    $scope.reqAction = reqAction;
    var getprofiles = $http({method:"GET", 
        url: "/cgi-bin/dpm/getprofiles.py"});
    var reqList = getprofiles.then(function(result) {
        alert(angular.toJson(result));
        $scope.profile_cols = result.data.cols;
        $scope.data = result.data.rows;
        $scope.profiles = new ngTableParams({
            page: 1,
            count: 10},
            {
                total: $scope.data.length,
                getData: function($defer, params) {
                    $defer.resolve($scope.data.slice((params.page() - 1) * 
                            params.count(), 
                            params.page() * params.count()));
                }
            });
    });
    
    $scope.disableOption = function(status_options) {
        disable = false;
        if (status_options.length === 0) {
            disable = true;
        }
        return disable;
    };

    reqList.then(function(result) {
        // Once selected fill in the text field for the email message
        // to the user
        $scope.selectReq = function() {
            $scope.show_msg = false;
            var userInfo = {uid: this.profile_data.values[0].name, 
                firstname: this.profile_data.values[2].name,
                lastname: this.profile_data.values[1].name,
                email: this.profile_data.values[4].name,
                role: this.profile_data.values[5].name,
                community: this.profile_data.values[6].name,
                approval: this.reqApproval};
            var getMessage = $http({method: "POST", 
                            url: "/cgi-bin/dpm/getMessage.py",
                            data: angular.toJson(userInfo)
                            });
            getMessage.then(function(response){
                $scope.userInfo = userInfo;
                $scope.e_body = response.data.msg;
                $scope.e_subject = response.data.subject;
                $scope.show_msg = true;
            });
        };
    });

    $scope.submitEmail = function() {
        // Check the length of the email strings
        if ($scope.e_body.length === 0) {
            alert("Error: The message body cannot be empty");
            return;
        }
        if ($scope.e_subject.length === 0) {
            alert("Error: The subject cannot be empty");
            return;
        }
        $scope.userInfo.e_body = $scope.e_body;
        $scope.userInfo.e_subject = $scope.e_subject;
        // Email the user and update the database
        var update_email = $http({method: "POST",
            url: "/cgi-bin/dpm/updateAndEmail.py",
            data: angular.toJson($scope.userInfo)
        });
        update_email.then(function(response) {
            alert("response is " + response.data);
        });

    };
}