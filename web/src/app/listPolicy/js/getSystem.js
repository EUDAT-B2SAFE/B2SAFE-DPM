function getSystem($http) {
    var getObj = $http({method: "GET", 
        url: "${CGI_URL}/query_resource.py", params: {qtype: "systems"}});
    return getObj;
}
