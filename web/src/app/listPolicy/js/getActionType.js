function getActionType($http, param) {
    var getObj = $http({method: "GET",
            url: "/cgi-bin/dpm/query_actions.py",
            params: {qtype: "types",
                operation: param}
        });
    return getObj;
}
