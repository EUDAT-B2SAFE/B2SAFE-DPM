dpmApp.service('policyService', function() {
    console.log("policyService is called");
    var policy = {};
    return {
        getObj: function() {
            return policy;
        },
        setObj: function(polin) {
            policy = polin;
        }
    };
});
