// Function for getting the user profile
function getProfile($http) {
    return $http({method: "GET", url: "/cgi-bin/dpm/getProfile.py"});
}

// Function to get the user environment variable
function getUserEnv($http) {
    return $http({method: "GET", url: "/cgi-bin/dpm/getUserEnv.py"});
}
