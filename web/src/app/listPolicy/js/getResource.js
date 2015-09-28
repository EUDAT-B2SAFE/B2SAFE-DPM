function getResource($http, system, site)  {
    var getObj = $http({method: "GET", 
        url: "${CGI_URL}/query_resource.py", 
        params: {qtype: "resources", system: system, site: site}
    });
    return getObj;
}
