dpmApp.service('data_identifier', function() {
    var identifiers = {types:[]};
    return {
        getIdentifiers: function() {
            return identifiers;
        },
        setIdentifiers: function(loc) {
            identifiers = loc;
        }
    };
});
