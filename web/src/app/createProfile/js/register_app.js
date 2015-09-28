var registerApp = angular.module("registerApp", ["ngRoute"]);

function regConfig($routeProvider) {
    $routeProvider.
        when("/", {
            controller: registerCtrl,
            templateUrl: "template/reg_tpl.html"}).
        when("/acknowledge", {
            controller: acknowledgeCtrl,
            templateUrl: "template/acknowledge.html"}).
        otherwise({
            redirectTo: "/"
        });
}

registerApp.config(regConfig);

function regFormCtrl($scope, $http, $route, $location, cMgr, invalidFlags) {
    $scope.register_submitted = false;
    $scope.invalidFlags = invalidFlags;
    $scope.cm = cMgr;

    // Get the user environment
    getUserEnv($http).then(function(result) {
        $scope.cm.username = result.data;
    });
    
    // Get the communities and roles
    getCommunities = $http({method:"GET", url: "${CGI_URL}/getCommunities.py"}); 
    getCommunities.then(function(result) {
        $scope.comm_types = result.data;
        $scope.comm_roles = result.data.roles;
    });

    $scope.currentPage = 0;

    // Add more community fields
    $scope.addMore = function() {
        $scope.cm.communities.push({name: ''}); 
        $scope.invalidFlags.communities.push({community: true});
    };

    // Remove community field
    $scope.removeCommunity = function(array, index) {
        array.splice(index, 1);
    };

    // Set the number of pages for the communities field
    $scope.numberOfPages = function() {
        return Math.ceil($scope.cm.communities.length/3);
    };

    // If the community selection changes we need to update our invalid
    // flag
    $scope.changeCommunity = function(index) {
        if ($scope.cm.communities[index].name) {
            $scope.invalidFlags.communities[index].community = false;
        } else {
            $scope.invalidFlags.communities[index].community = true;
        }
    };

    // Issued a submit request
    $scope.submitReq = function() {
        $scope.register_submitted = true;
    };

    // Submit the form
    $scope.submitForm = function() {
        if ($scope.register_submitted) {
            if (! $scope.register.$invalid) {
                $http.post("${CGI_URL}/submitProfile.py", 
                        angular.toJson($scope.cm),
                        {headers: "Content-Type: application/x-www-form-urlencoded; charset=UTF-8;"}).then(
                            function(result){
                                var retval = result.data.replace(/\s/g, '');
                                if (retval === "roleExists") {
                                    alert("The user account is already registered for this role");
                                } else {
                                    // Have to reset the fields manually
                                    // as the $setPristine doesn't work
                                    //$scope.register.$setPristine();
                                    cMgr.firstname = '';
                                    cMgr.lastname = '';
                                    cMgr.email = '';
                                    cMgr.role = '';
                                    cMgr.username = '';
                                    cMgr.communities = [{name: ''}];
                                    $scope.cm = cMgr;
                                    $location.url("/acknowledge");
                                }
                            }, function(error){
                                alert("There was a problem submitting the request." +
                                " Please contact the Data Policy Manager for more information");
                            });
            }
        }
    };

    // Reset the form
    var result = '';
    $scope.resetForm = function() {
        // Get the user environment
        //getUserEnv($http).then(function(result) {
        //    $scope.cm.username = result.data;
        //});
        //$scope.cm.username = angular.copy(result.data);
        //$scope.register.$setPristine();
        window.location.reload();
    };
}
function registerCtrl($scope) {
}

function acknowledgeCtrl($scope) {
}

