function pristineFlags() {
    var action = {action: true, type: true, trigger: true, period: true,
      trigger_date: true, period_date: true};
    var targets = new Array({organisation: true, location_type: true,
      system: true, site: true, resource: true, coll: true, pid: true});
    var sources = new Array({organisation: true, location_type: true,
      system: true, site: true, resource: true, coll: true, pid: true});
    var pristine = {action: action, sources: sources, targets: targets};
    return pristine;
}

// Create a factory for the pristine flags
dpmApp.factory("pristineFlags", pristineFlags);
