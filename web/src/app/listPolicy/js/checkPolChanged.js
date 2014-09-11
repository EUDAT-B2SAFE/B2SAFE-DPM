function checkPolChanged(polObj) {
    var invalidPol = false;
    var polHasChanged = false;
    var invalidFlags = [];

    // has the policy changed (we only need to find one example
    for (var key in polObj) {
        if (polObj[key] === true) {
            polHasChanged = true;
            break;
        }
    }
    
    // We need to check the combination of elements since some elements
    // work in conjunction:
    // identifier - collection
    // action - type
    // system - site
    // trigger name - trigger value
    // site - resource
    if (polHasChanged) {
        for (var i; i < polObj.identifier.length; i++) {
            if ((polObj.identifier[i] != null && 
                        polObj.collection[i] != null) &&
                    (polObj.identifier[i] != polObj.collection[i])) {
                invalidPol = true;
                if (polObj.identifier[i]) {
                    invalidFlags.push("collection");
                } else {
                    invalidFlags.push("identifier");
                }
            }
        }
        if ((polObj.action != null && polObj.type != null) &&
                (polObj.action != polObj.type)) {
            invalidPol = true;
            if (polObj.action) {
                invalidFlags.push("type");
            } else {
                invalidFlags.push("action");
            }
        }
        if ((polObj.system != null && polObj.site != null) && 
                (polObj.system != polObj.site)) {
            invalidPol = true;
            if (polObj.system) {
                invalidFlags.push("site");
            } else {
                invalidFlags.push("system");
            }
        }
        if ((polObj.site != null && polObj.resource != null) && 
                polObj.site != polObj.resource) {
            invalidPol = true;
            if (polObj.site) {
                invalidFlags.push("resource");
            } else {
                invalidFlags.push("site");
            }
        }
        if (polObj.trigger_name && ! polObj.trigger_value) {
            invalidPol = true;
            invalidFlags.push("trigger");
        }
    }
    return {changed: polHasChanged, invalid: invalidFlags};
}
