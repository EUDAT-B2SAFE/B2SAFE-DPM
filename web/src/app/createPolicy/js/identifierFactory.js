var identifierFlags = function() {
  var showSrcPIDs = [];
  var showSrcColls = [];
  var showTgtColls = [];
  var showTgtPIDs = [];
  var identifierFlagObj = {showSrcPIDs: showSrcPIDs, showSrcColls: showSrcColls,
  showTgtColls: showTgtColls, showTgtPIDs: showTgtPIDs};
  return identifierFlagObj;
};

dpmApp.factory('identifierFlags', identifierFlags);
