function submitCtrl($scope, $location, $window, $route, submitFlag, policy,
        pristineFlags, invalidFlags, $http, page) {

    $scope.setSubmitted = function(validObj) {
      console.log('valid objs: is ' + JSON.stringify(validObj));
      console.log('type ' + validObj.type.$pristine);
      console.log('trigger ' + validObj.trigger.$pristine);
      //console.log('srccoll ' + validObj.srcid.$pristine);
      console.log('tgtcoll ' + validObj.tgtid.$pristine);

      var flago = submitFlag.getObj();
      console.log('submitting policy ' + JSON.stringify(policy));
      flago.fieldsOK = checkFields(validObj, pristineFlags, invalidFlags,
              flago, policy);
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
        console.log('storing the policy ' + JSON.stringify(policy));
        $http.post('${CGI_URL}/storePolicy.py', JSON.stringify(policy),
                {headers: 'Content-Type: application/x-www-form-urlencoded'})
            .then(function(results) {
                var data = results.data;
                if (data.policy_exists) {
                    alert('The policy exists in the database');
                } else {
                    alert('Policy successfully stored in the database');
                }
                // Reset the policy and reload the page which puts us on
                // the default page - the policy listing
                var newPolicy = {};
                newPolicy = resetPolicy(policy);
                $scope.policy = newPolicy;
                // alert("scope is " + JSON.stringify($scope.policy));
                $window.location.reload();
            },
            function(data, status, headers, config) {
                alert('error is ' + data);
            });
    };

    // TODO: We will need to alter this as it's not correct 5/Jan/16
    $scope.collDefined = function() {
      var collFlag = false;
      var i = 0;
      for (i = 0; i < $scope.policy.collections.length; i++) {
        if ($scope.policy.collections[i].type.name === 'collection') {
          collFlag = true;
          break;
        }
      }
      return collFlag;
    };

    // TODO: We will need to alter this as it's not correct - AH 5/Jan/16
    $scope.pidDefined = function() {
      var pidFlag = false;
      var i = 0;
      for (i = 0; i < $scope.policy.collections.length; i++) {
        if ($scope.policy.collections[i].type.name === 'pid') {
          pidFlag = true;
          break;
        }
      }
      return pidFlag;
    };
}
