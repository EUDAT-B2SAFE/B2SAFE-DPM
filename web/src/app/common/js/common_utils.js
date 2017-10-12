// Function for getting the user profile
function getProfile($http) {
    return $http({method: "GET", url: "${CGI_URL}/getProfile.py"});
}

// Function to get the user environment variable
function getUserEnv($http) {
    return $http({method: "GET", url: "${CGI_URL}/getUserEnv.py"});
}

function checkAccess($http) {
    $http({method: "GET", url: "${CGI_URL}/checkAccess.py"}).success(
                function(data, status){
                    if (status === 200){
                        if (data.connection === "successful") {
                            return true;
                        }
                    }
                }).error(function(data, status){
                    console.log("error is " + status);
                });
}
