// Function for getting the user profile
function getProfile($http) {
    return $http({method: "GET", url: "${CGI_URL}/getProfile.py"});
}

// Function to get the user environment variable
function getUserEnv($http) {
    return $http({method: "GET", url: "${CGI_URL}/getUserEnv.py"});
}

function checkLocalStorage() {
    var test = 'test';
    try {
        localStorage.setItem("test", "test");
        localStorage.removeItem(test);
        return true;
    } catch(e) {
        return false;
    } 
}

function checkAccess($http) {
    $http({method: "GET", url: "${CGI_URL}/checkAccess.py"}).success(
                function(data, status){
                    if (status === 200){
                        if (data.connection === "successful") {
                            var timeoutPage = document.getElementById("timeout-page");
                            timeoutPage.style.display = "none";
                            return true;
                        }
                    }
                }).error(function(data, status){
                   if (checkLocalStorage()) {
                        if (localStorage.getItem("session_renew") === null) {
                            var timeoutPage = document.getElementById("timeout-page");
                            timeoutPage.style.display = "block";
                            localStorage.setItem("session_renew", "displayed");
                        }
                    } else {
                        console.log("Cannot write to the localstorage.");
                    }
                    console.log("error is " + status);
                    return false;
                });
}
