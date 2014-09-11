function getActionTrigger($http, action, type) {
    var getObj = $http({method: "GET",
            url: "/cgi-bin/dpm/query_actions.py",
            params: {qtype: "triggers",
                operation: action, type: type}
        });
    return getObj;
}
