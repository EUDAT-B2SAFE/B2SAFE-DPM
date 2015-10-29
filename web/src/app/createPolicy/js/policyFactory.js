var policy = function() {
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
    var source_organisation = new Array({name: "--- Select an Organisation ---"});
    var target_organisation = {name: "--- Select an Organisation ---"};
    var weekday = {name: "*"};
    var day = {name: "*"};
    var month ={name: "*"};
    var hour = {name: "*"};
    var minute = {name: "*"};

    var period = {weekday: weekday, month: month, day: day, hour: hour,
        minute: minute};

    var sources = new Array({
        loctype: loctype,
        organisation: source_organisation,
        system: source_system,
        site: source_site,
        path: '',
        resource: source_resource
    });
    var target = {
        loctype: loctype,
        organisation: target_organisation,
        system: target_system,
        site: target_site,
        path: "",
        resource: target_resource
    };
    var collections = new Array({name: "", type: {name: ""}});

    var policyObj = {name: "", id: "",
        version: "1.0", uuid: "", author: "", community: "",
        collections: collections,
        action: action,
        type: type,
        trigger: trigger,
        trigger_date: "",
        trigger_period: period,
        sources: sources,
        target: target};
    return policyObj;
};

// create a factory to generate a policy object
dpmApp.factory("policy", policy);
