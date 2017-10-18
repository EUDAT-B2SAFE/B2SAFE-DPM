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
        localStorage.setItem(test, "test");
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
                            return true;
                        }
                    }
                }).error(function(data, status){
                    var width = 600;
                    var height = 300;
                    var leftPosition = (screen.width) ? (screen.width-w)/2 : 0;
                    var topPosition = (screen.height) ? (screen.height-h)/2 : 0;
                    var settings = "height="+height+",width="+width+
                        ",top="+topPosition+",left="+leftPosition+
                        ",scrollbars=yes,resizable";
                    window.open("${HTML_OPEN}", "Session Timedout",
                                settings);
                    if (checkLocalStorage()) {
                        localStorage.setItem("session_renew", "displayed");
                    }
                    console.log("error is " + status);
                    return false;
                });
}
