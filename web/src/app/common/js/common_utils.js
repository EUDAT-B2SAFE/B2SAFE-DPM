// Function for getting the user profile
function getProfile($http) {
    return $http({method: "GET", url: "${CGI_URL}/getProfile.py"});
}

// Function to get the user environment variable
function getUserEnv($http) {
    return $http({method: "GET", url: "${CGI_URL}/getUserEnv.py"});
}
