dpmApp.service('data_action', function() {
    var actions = {types:[],
        operations:[], triggers:[], organisations:[]};
    return {
        getActions: function() {
            return actions;
        },
        setActions: function(loc) {
            actions = loc;
        }
    };
});
