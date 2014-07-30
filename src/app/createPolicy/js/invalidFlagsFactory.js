function invalidFlags() {
    var dataset = new Array({pid: true, coll: true});
    var invalids = {dataset: dataset};
    return invalids;
}
dpmApp.factory("invalidFlags", invalidFlags);
