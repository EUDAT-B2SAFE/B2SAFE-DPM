dpmApp.service("disabled_flags", function() {
    var disabled_flags_obj = {action_type: true, action_trigger: true,
        tgt_loc_type: true, tgt_organisation: true,
        tgt_system: true, source_system: true,
        source_organisation: true,
        source_site: true, target_site: true,
        source_resource: true, target_resource: true};
    return {
        getFlags: function() {
            return disabled_flags_obj;
        },
        setFlags: function(obj) {
            disabled_flags_obj = obj;
        }
    };
});
