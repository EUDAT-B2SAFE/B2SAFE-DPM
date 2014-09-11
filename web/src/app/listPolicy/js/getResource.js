function getResource($http, system, site)  {
    var getObj = $http({method: "GET", 
        url: "/cgi-bin/dpm/query_resource.py", 
        params: {qtype: "resources", system: system, site: site}
    });
    return getObj;
}
