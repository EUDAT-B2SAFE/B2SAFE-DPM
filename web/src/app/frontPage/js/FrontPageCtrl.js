function frontPageCtrl($scope, $http) {
    $scope.sendToDPM = function() {
        var geturl = $http({method: "POST",
                        url: "/cgi-bin/dpm/getURL.py", 
                        data: angular.toJson({name:"dpm"})}).then(function(response){
                            window.location.href = response.data;
                        });
    };

    $scope.sendToAdmin = function() {
        var geturl = $http({method: "POST",
                        url: "/cgi-bin/dpm/getURL.py", 
                        data: angular.toJson({name:"admin"})}).then(function(response){
                            window.location.href = response.data;
                        });
    };
}
