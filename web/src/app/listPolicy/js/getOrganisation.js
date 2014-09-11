function getOrganisation($http) {
    var getObj = $http({method: "GET", 
        url: "/cgi-bin/dpm/query_actions.py", 
        params: {qtype: "organisations"}});
    return getObj;
}
