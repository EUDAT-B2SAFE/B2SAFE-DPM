function getActionTrigger($http, action, type) {
    var getObj = $http({method: "GET",
            url: "${CGI_URL}/query_actions.py",
            params: {qtype: "triggers",
                operation: action, type: type}
        });
    return getObj;
}
