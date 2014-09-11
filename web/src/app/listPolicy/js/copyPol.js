function copyPol(pol1) {
    // Make a deep copy of a policy
    var pol2 = {};
    pol2.name = pol1.name;
    pol2.version = pol1.version;
    pol2.author = pol1.author;
    pol2.uuid = pol1.uuid;
    pol2.community = pol1.community;
    pol2.collections = [];    
    for (var i = 0; i < pol1.collections.length; i++) {
        var coll = {};
        coll = {name: pol1.collections[i].name, 
            type: pol1.collections[i].type};
        pol2.collections.push(coll);
    }
    pol2.action = {name: pol1.action.name};
    pol2.type = {name: pol1.type.name};
    pol2.trigger = {name: pol1.trigger.name, value: pol1.trigger.value};
    var loctype = {name: pol1.target.loctype.name};
    var organisation = {name: pol1.target.organisation.name};
    var site = {name: pol1.target.site.name};
    var resource = {name: pol1.target.resource.name};
    var system = {name: pol1.target.system.name};
    pol2.target = {organisation: organisation, site: site, system: system,
        loctype: loctype, resource: resource, path: pol1.target.path};
    return pol2;
}
