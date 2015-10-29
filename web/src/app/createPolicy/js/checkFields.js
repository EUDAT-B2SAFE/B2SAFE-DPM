function checkFields(validObj, pristineFlagsObj, invalidFlagsObj, flago,
  policy) {
    var fieldsOK = false;

    if (validObj) {
        fieldsOK = true;
        // We have to ignore the pristine flag in the case of
        // a person submitting and goes back to update the form
        // so we use our own flags
        if (!flago.submitted) {
            pristineFlagsObj.action.action = validObj.action.$pristine;
            pristineFlagsObj.action.type = validObj.type.$pristine;
            pristineFlagsObj.action.trigger = validObj.trigger.$pristine;
            pristineFlagsObj.target.organisation = validObj.tgtorganisation.$pristine;
            // pristineFlagsObj.target.location_type = validObj.location_type.$pristine;
            pristineFlagsObj.target.system = validObj.tgtsystem.$pristine;
            pristineFlagsObj.target.site = validObj.tgtsite.$pristine;
            pristineFlagsObj.target.resource = validObj.tgtresource.$pristine;
        }

        // Loop over all the flags for the dataset pid. On the first true
        // set the valid flag to false and break out
        var i;
        for (i=0; i < pristineFlagsObj.dataset.length; i++) {
            if (policy.collections[i].type.name === "pid") {
              if (pristineFlagsObj.dataset[i].pid === true ||
                  pristineFlagsObj.dataset[i].coll === true ||
                  invalidFlagsObj.dataset[i].pid === true ||
                  invalidFlagsObj.dataset[i].coll === true) {
                    fieldsOK = false;
                    break;
              }
            } else if (policy.collections[i].type.name === "collection") {
              if (pristineFlagsObj.sources[i].organisation === true ||
                  pristineFlagsObj.sources[i].system === true ||
                  pristineFlagsObj.sources[i].site === true ||
                  pristineFlagsObj.sources[i].resource === true ||
                  invalidFlagsObj.source[i].organisation === true ||
                  invalidFlagsObj.source[i].system === true ||
                  invalidFlagsObj.source[i].site === true ||
                  invalidFlagsObj.source[i].resource === true) {
                    fieldsOK = false;
                    break;
                  }
            }
        }

        if (pristineFlagsObj.action.action || validObj.action.$invalid) fieldsOK = false;
        if (pristineFlagsObj.action.type || validObj.type.$invalid) fieldsOK = false;
        if (pristineFlagsObj.action.trigger || validObj.trigger.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.organisation || validObj.tgtorganisation.$invalid) fieldsOK = false;
        // if (pristineFlagsObj.target.location_type || validObj.location_type.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.system || validObj.tgtsystem.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.site || validObj.tgtsite.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.resource || validObj.tgtresource.$invalid) fieldsOK = false;
    }
    return fieldsOK;
}
