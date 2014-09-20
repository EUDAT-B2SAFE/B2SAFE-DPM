function resetPolicy(apol) {
    // Rest the policy object apart from the personal information
    var action = {name: "--- Select an Action ---"};
    var type = {name: "--- Select a Type ---"};
    var trigger = {name: "--- Select a Trigger ---"};
    var source_system = {name: "--- Select a System ---"};
    var source_site = {name: "--- Select a Site ---"};
    var source_resource = {name: "--- Select a Resource ---"};
    var target_system = {name: "--- Select a System ---"};
    var target_site = {name: "--- Select a Site ---"};
    var target_resource = {name: "--- Select a Resource ---"};
    var loctype = {name: "--- Select a Location type ---"};
    var organisation = {name: "--- Select an Organisation ---"};
    var weekday = {name: "*"};
    var day = {name: "*"};
    var month ={name: "*"};
    var hour = {name: "*"};
    var minute = {name: "*"};

    var period = {weekday: weekday, month: month, day: day, hour: hour,
        minute: minute};
    
    var source = {
        loctype: loctype,
        organisation: organisation,
        system: source_system,
        site: source_site,
        path: "",
        resource: source_resource
    };
    var target = {
        loctype: loctype,
        organisation: organisation,
        system: target_system,
        site: target_site,
        path: "",
        resource: target_resource
    };

    var opol = {};
    opol.name = "";
    opol.version = "1.0";
    opol.author = apol.author;
    opol.community = apol.community;
    opol.id = "";
    opol.uuid = "";
    opol.collections = new Array({name: "", type: {name: ""}});
    opol.action = action;
    opol.type = type;
    opol.trigger = trigger;
    opol.trigger_date = "";
    opol.trigger_period = period;
    opol.source = source; 
    opol.target = target;

    return opol;
}
