function checkFields(validObj, pristineFlagsObj, invalidFlagsObj, flago,
  policy) {
    var fieldsOK = false;

    if (validObj) {
        fieldsOK = true;
        if (pristineFlagsObj.action.type) {
          fieldsOK = false;
          return fieldsOK;
        }
        if (pristineFlagsObj.action.trigger) {
          fieldsOK = false;
          return fieldsOK;
        }
        if (policy.trigger.name === 'date/time') {
          if (invalidFlagsObj.action.period) {
            fieldsOK = false;
            return fieldsOK;
          }
          if (policy.trigger_date.name === 'date') {
            if (invalidFlagsObj.action.period_date) {
              fieldsOK = false;
              return fieldsOK;
            }
          }
        }
        console.log('after trigger fieldsOK ' + fieldsOK);
        console.log('pristineFlags ' + JSON.stringify(pristineFlagsObj.sources));
        console.log('policy sources ' + JSON.stringify(policy.sources));
        for (var i = 0; i < pristineFlagsObj.sources.length; i++) {
          if (policy.sources[i].type.name === 'collection'){
            fieldsOK = checkCollValid(pristineFlagsObj, invalidFlagsObj,
              policy, 'sources', i);
            if (! fieldsOK) {
              break;
            }
          } else if (policy.sources[i].type.name === 'pid') {
            fieldsOK = true;
          } else {
            fieldsOK = false;
            break;
          }
        }
        if (!fieldsOK) {
          return fieldsOK;
        }
        console.log('after sources fieldsOK ' + fieldsOK);
        for (i = 0; i < pristineFlagsObj.targets.length; i++) {
          if (policy.targets[i].type.name === 'collection') {
            fieldsOK = checkCollValid(pristineFlagsObj, invalidFlagsObj,
              policy, 'targets', i);
            if (! fieldsOK) {
              break;
            }
          } else if (policy.targets[i].type.name === 'pid') {
            fieldsOK = true;
          } else {
            fieldsOK = false;
          }
        }
        if (!fieldsOK) {
          return fieldsOK;
        }
        console.log('after targets fieldsOK ' + fieldsOK);
        // Loop over all the flags for the dataset pid. On the first true
        // set the valid flag to false and break out
        console.log('policy is ' + JSON.stringify(policy));
        console.log('source is ' + JSON.stringify(policy.sources[0]));
        console.log('target is ' + JSON.stringify(policy.targets[0]));
    }
    return fieldsOK;
}

function checkCollValid(pristineFlags, invalidFlags, policy, location, index) {
  var fieldsOK = true;
  if (pristineFlags[location][index].location_type ||
    pristineFlags[location][index].site) {
      console.log('location ' + pristineFlags[location][index].location_type);
      console.log('site ' + pristineFlags[location][index].site);
    fieldsOK = false;
  }
  if (policy[location][index].type.name === 'collection') {
    if (invalidFlags[location][index].coll ||
      pristineFlags[location][index].coll) {
        fieldsOK = false;
    }
  } else if (policy[location][index].type.name === 'pid') {
    if (invalidFlags[location][index].pid ||
      pristineFlags[location][index].pid) {
        fieldsOK = false;
    }
  }
  return fieldsOK;
}
