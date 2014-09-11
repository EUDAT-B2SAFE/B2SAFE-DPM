function getLocation($http, op, type, trig) {
    var getObj = $http({method: "GET", 
        url: "/cgi-bin/dpm/query_actions.py", params: {qtype: "locations", 
            operation: op, type: type, trigger: trig}});
    return getObj;
}
