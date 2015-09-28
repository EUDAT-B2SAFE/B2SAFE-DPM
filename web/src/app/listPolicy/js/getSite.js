function getSite($http, system) {
    var getObj = $http({method: "GET", 
        url: "${CGI_URL}/query_resource.py", params: {qtype: "sites", 
            system: system}
    });
    return getObj;
}
