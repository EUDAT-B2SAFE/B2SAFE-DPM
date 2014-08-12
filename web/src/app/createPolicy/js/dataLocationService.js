dpmApp.service('data_location', function() {
    var locations = {source_systems:[],
        source_sites:[], source_resources:[],
        target_systems:[], target_sites:[], 
        target_resources:[], location_types:[]};
    return {
        getLocations: function() {
            return locations;
        },
        setLocations: function(loc) {
            locations = loc;
        }
    };
});
