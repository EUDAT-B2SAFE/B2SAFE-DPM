function checkPolChanged(polObj, policy, origPolicy, invalidFlags) {
    var invalidPol = false;
    var polHasChanged = false;
    var polInvalid = false;

    // has the policy changed (we only need to find one example)
    for (var key in polObj) {
        if (polObj[key] === true) {
            polHasChanged = true;
            break;
        }
    }
    if (polHasChanged === false) {
        if ((policy.sources.length !== origPolicy.sources.length) || 
                (policy.targets.length !== origPolicy.targets.length)) {
            polHasChanged = true;
        }
    }
    for (var index1 = 0; index1 <= polObj.sources.length; index1++) {
        for (var skey in polObj.sources[index1]) {
            if (polObj.sources[index1][skey] === true) {
                polHasChanged = true;
                console.log("skey " + skey + " policy.sources: " + JSON.stringify(policy.sources[index1]));
                if (skey === "collection" || skey === "pid") {
                    if (policy.sources[index1].identifier.name.length  <= 0) {
                        invalidFlags.sources[index1].coll = true;
                        polInvalid = true;
                    }
                }
                break;
            } else {
                invalidFlags.sources[index1].coll = false;
            }
        }
    }
    for (var index2 = 0; index2 <= polObj.targets.length; index2++) {
        for (var tkey in polObj.targets[index2]) {
            if (polObj.targets[index2][tkey] === true) {
                polHasChanged = true;
                break;
            }
        }
    }
    // Are any of the attributes that have changed invalid
    
    return {changed: polHasChanged, invalid: polInvalid, invalidFlags: invalidFlags};
}
