function invalidFlags() {
  var action = {period:true};
  var sources = new Array({organisation: true, system: true,
    site: true, resource: true, pid: true, coll: true});
  var targets = new Array({organisation: true, system: true,
    site: true, resource: true, pid: true, coll: true});
  var invalids = {action:action, sources: sources, targets: targets};
  return invalids;
}
dpmApp.factory('invalidFlags', invalidFlags);
