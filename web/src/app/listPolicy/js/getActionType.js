function getActionType($http, param) {
    var getObj = $http({method: "GET",
            url: "${CGI_URL}/query_actions.py",
            params: {qtype: "types",
                operation: param}
        });
    return getObj;
}
