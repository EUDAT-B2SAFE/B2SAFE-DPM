function invalidFlags() {
    var communities = [{community: true}];
    var invalids = {communities: communities};
    return invalids;
}

registerApp.factory('invalidFlags', invalidFlags);
