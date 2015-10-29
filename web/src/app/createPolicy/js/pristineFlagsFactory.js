function pristineFlags() {
    var dataset = new Array({pid: true, coll: true});
    var action = {action: true, type: true, trigger: true};
    var target = {organisation: true, location_type: true, system: true,
        site: true, resource: true};
    var sources = new Array({organisation: true, location_type: true, system: true,
        site: true, resource: true});
    var pristine = {dataset: dataset, action: action, sources: sources,
        target: target};
    return pristine;
}

// Create a factory for the pristine flags
dpmApp.factory("pristineFlags", pristineFlags);
