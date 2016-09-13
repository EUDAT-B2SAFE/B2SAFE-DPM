var identifierFlags = function() {
  var showSrcPIDs = [];
  var showSrcPolicy = [];
  var showSrcColls = [];
  var showTgtColls = [];
  var showTgtPIDs = [];
  var identifierFlagObj = {showSrcPIDs: showSrcPIDs, showSrcColls: showSrcColls,
  showTgtColls: showTgtColls, showTgtPIDs: showTgtPIDs,
  showSrcPolicy: showSrcPolicy};
  return identifierFlagObj;
};

dpmApp.factory('identifierFlags', identifierFlags);
