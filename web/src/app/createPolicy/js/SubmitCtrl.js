function submitCtrl($scope, $location, $window, $route, submitFlag, policy, 
        pristineFlags, invalidFlags, $http, page) {
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
        // We can now set the id for the policy before sending to the
        // database
        policy.id = policy.uuid;
        $http.post("${CGI_URL}/storePolicy.py", JSON.stringify(policy),
                {headers: "Content-Type: application/x-www-form-urlencoded"})
            .then(function(results) {
                var data = results.data;
                if (data.policy_exists) {
                    alert("The policy exists in the database");
                } else {
                    alert("Policy successfully stored in the database");
                }
                // Reset the policy and reload the page which puts us on
                // the default page - the policy listing
                var new_policy = {};
                new_policy = resetPolicy(policy);
                $scope.policy = new_policy;
                // alert("scope is " + JSON.stringify($scope.policy));
                $window.location.reload();
            },
            function(data, status, headers, config) {
                alert("error is " + data);
            });
    };

}
