var checkRegisterApp = angular.module("checkRegisterApp", []);

function checkRegisterCtrl($scope, $http) {
    // Make a call to the database to find if the user is registered and
    // logged in
    $http({method: "GET",
        url: "/cgi-bin/dpm/check_register.py"}).then(function(response) {
            var data = response.data;
            window.location.href = data;
        });
}
