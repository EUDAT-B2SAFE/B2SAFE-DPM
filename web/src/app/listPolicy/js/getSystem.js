function getSystem($http) {
    var getObj = $http({method: "GET", 
        url: "/cgi-bin/dpm/query_resource.py", params: {qtype: "systems"}});
    return getObj;
}
