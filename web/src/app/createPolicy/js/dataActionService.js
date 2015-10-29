dpmApp.service('data_action', function() {
    var actions = {types:[],
        operations:[], triggers:[]};
    return {
        getActions: function() {
            return actions;
        },
        setActions: function(loc) {
            actions = loc;
        }
    };
});
