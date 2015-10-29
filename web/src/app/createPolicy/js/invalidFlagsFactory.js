function invalidFlags() {
    var dataset = new Array({pid: true, coll: true});
    var sources = new Array({organisation: true, system: true,
      site: true, resource: true});
    var invalids = {dataset: dataset, source: sources};
    return invalids;
}
dpmApp.factory('invalidFlags', invalidFlags);
