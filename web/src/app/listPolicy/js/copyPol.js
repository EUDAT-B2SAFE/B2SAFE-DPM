function copyPol(pol1) {
    // Make a deep copy of a policy
    var pol2 = {};
    pol2.name = pol1.name;
    pol2.version = pol1.version;
    pol2.author = pol1.author;
    pol2.uuid = pol1.uuid;
    pol2.family = pol1.family;
    pol2.community = pol1.community;
    pol2.action = {name: pol1.action};
    pol2.type = {name: pol1.type.name};
    pol2.trigger = {name: pol1.trigger.name, value: pol1.trigger.value};
    pol2.sources = [];
    for (var is=0; is < pol1.sources.length; is++) {
        hostname = "";
        if (pol1.sources[is].type.name === "collection") {
            hostname = pol1.sources[is].hostname.name;
        } else if (pol1.sources[is].type.name === "policy") {
            if (typeof pol1.sources[is].hostname !== "undefined") {
                hostname = pol1.sources[is].hostname.name;
            }
        }

        pol2.sources.push({"resource": {"name":""},
                           "organisation": {"name":"EUDAT"},
                           "hostname": {"name": hostname},
                           "system":{"name":"iRODS"},
                           "identifier": {"name": pol1.sources[is].identifier.name},
                           "type": {"name": pol1.sources[is].type.name}});
    }
    pol2.targets = [];
    for (var it=0; it < pol1.targets.length; it++) {
        hostname = "";
        if (pol1.targets[it].type.name === "collection") {
            hostname = pol1.targets[it].hostname.name;
        }
        pol2.targets.push({"resource": {"name":""},
                            "organisation": {"name":"EUDAT"},
                            "hostname": {"name": hostname},
                            "system":{"name":"iRODS"},
                            "identifier": {"name": pol1.targets[it].identifier.name},
                            "type": {"name": pol1.targets[it].type.name}});
    }
    return pol2;
}
