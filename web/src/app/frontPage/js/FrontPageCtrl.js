function frontPageCtrl($scope, $http) {
    $scope.sendToDPM = function() {
        $http({method: "POST", url: "${CGI_URL}/getURL.py", 
            data: angular.toJson({name:"dpm"})}).then(function(response){
                window.location.href = response.data;
        });
    };

    $scope.sendToAdmin = function() {
        $http({method: "POST", url: "${CGI_URL}/getURL.py", 
            data: angular.toJson({name:"admin"})}).then(function(response){
                window.location.href = response.data;
        });
    };
}
