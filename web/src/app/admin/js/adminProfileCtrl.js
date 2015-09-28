function adminProfileCtrl($scope, $window, $http, reqAction, ngTableParams) {
    $scope.selectDisabled = [];
    $scope.data = [];
    $scope.show_msg = false;
    $scope.profile_cols = [];
    $scope.reqAction = reqAction;
    var getprofiles = $http({method:"GET", 
        url: "${CGI_URL}/getprofiles.py"});
    var reqList = getprofiles.then(function(result) {
        $scope.profile_cols = result.data.cols;
        $scope.data = result.data.rows;
        var j;
        for (j=0; j < $scope.data.length; j++) {
            $scope.selectDisabled.push(true);
        }
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
   
    $scope.enableSelect = function(index) {
        // First reset all flags to disabled since we want this to be
        // modal
        var k;
        for (k = 0; k < $scope.selectDisabled.length; k++) {
            if ($scope.selectDisabled[k] === false) {
                $scope.selectDisabled[k] = true;
                break;
            }
        }
        $scope.selectDisabled[index]=false;
    };

    $scope.checkDisabled = function(index) {
        return $scope.selectDisabled[index];
    };

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
                            url: "${CGI_URL}/getMessage.py",
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

    $scope.resetHighlight = function() {
        var i;
        for (i = 0; i < $scope.data.length; i++) {
            if ($scope.data[i].$selected === true) {
                $scope.data[i].$selected = false;
                break;
            }
        }
    };

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
            url: "${CGI_URL}/updateAndEmail.py",
            data: angular.toJson($scope.userInfo)
        });
        update_email.then(function(response) {
            var resp = response.data.replace(/\s/g, '');
            if (resp === 'msgSent') {
                alert("Status has been successfully updated");
                $window.location.reload();
            } else {
                alert("Problem sending the email message. Contact the DPM Administrator");
            }
        });

    };
}
