function getOrganisation($http) {
    var getObj = $http({method: "GET", 
        url: "${CGI_URL}/query_actions.py", 
        params: {qtype: "organisations"}});
    return getObj;
}
