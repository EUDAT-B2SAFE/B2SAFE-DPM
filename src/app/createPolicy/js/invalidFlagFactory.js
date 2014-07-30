dpmApp.factory('invalidFlag', function() {
    var validObj = {"policyName": false,
        "policyVersion": false,
        "policyAuthor": false,
        "policyCommunity": false
    };
    return validObj;
});
