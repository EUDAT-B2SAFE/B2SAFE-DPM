function submitCtrl($scope, $location, submitFlag, policy, pristineFlags, 
        invalidFlags, $http, page) {
    $scope.setSubmitted = function(validObj) {
        var flago = submitFlag.getObj();
        flago.fieldsOK = checkFields(validObj, pristineFlags, invalidFlags,
                flago);
        flago.active = true;
        flago.submitted = true;
        submitFlag.setObj(flago);
        $scope.submitted = flago.submitted;
    };
    $scope.submitForm = function () {
        var flago = submitFlag.getObj();
        if (flago.fieldsOK) {
            if (flago.active) {
                $location.url(locList[locList.length-1].url);
                page.count = locList.length - 1;
            }
        } else {
            if (flago.active) {
                alert("The form is invalid. Check fields for errors");
                flago.submitted = false;
            }
        }
    };
    $scope.confirmOK = function() {
        $http.post("/cgi-bin/dpm/storePolicy.py", JSON.stringify(policy),
                {headers: "Content-Type: application/x-www-form-urlencoded"})
            .success(function(data, status, headers, config) {
                alert("Policy successfully stored in the database");
                if (data.policy_exists) {
                    alert("The policy exists in the database");
                }
            }).error(function(data, status, headers, config) {
                alert("error is " + data);
            });

    };

}
