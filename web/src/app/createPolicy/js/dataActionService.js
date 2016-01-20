dpmApp.service('data_action', function() {
  'use strict';
    var actions = {types:[], triggers:[]};
    return {
        getActions: function() {
            return actions;
        },
        setActions: function(loc) {
            actions = loc;
        }
    };
});
