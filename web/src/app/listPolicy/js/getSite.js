function getSite($http, system) {
    var getObj = $http({method: "GET", 
        url: "/cgi-bin/dpm/query_resource.py", params: {qtype: "sites", 
            system: system}
    });
    return getObj;
}
