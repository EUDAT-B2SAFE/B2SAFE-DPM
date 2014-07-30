function checkFields(validObj, pristineFlagsObj, invalidFlagsObj, flago) {
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
            pristineFlagsObj.target.organisation = validObj.organisation.$pristine;
            pristineFlagsObj.target.location_type = validObj.location_type.$pristine;
            pristineFlagsObj.target.system = validObj.system.$pristine;
            pristineFlagsObj.target.site = validObj.site.$pristine;
            pristineFlagsObj.target.resource = validObj.resource.$pristine;
        }

        // Loop over all the flags for the dataset pid. On the first true
        // set the valid flag to false and break out
        var i;
        for (i=0; i < pristineFlagsObj.dataset.length; i++) {
            if (pristineFlagsObj.dataset[i].pid === true ||
                    pristineFlagsObj.dataset[i].coll === true ||
                    invalidFlagsObj.dataset[i].pid === true ||
                    invalidFlagsObj.dataset[i].coll === true) {
                fieldsOK = false;
                break;
            }
        }

        if (pristineFlagsObj.action.action || validObj.action.$invalid) fieldsOK = false;
        if (pristineFlagsObj.action.type || validObj.type.$invalid) fieldsOK = false;
        if (pristineFlagsObj.action.trigger || validObj.trigger.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.organisation || validObj.organisation.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.location_type || validObj.location_type.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.system || validObj.system.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.site || validObj.site.$invalid) fieldsOK = false;
        if (pristineFlagsObj.target.resource || validObj.resource.$invalid) fieldsOK = false;
    }
    return fieldsOK;
}
