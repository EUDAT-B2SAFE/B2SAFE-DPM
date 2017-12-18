dpmApp.factory('listaction', function() {
  var alist = [{"name": "Modify"}, 
               {"name": "Reject"}];
  var rlist = [{"name": "Modify"},
               {"name": "Reactivate"}];
    return {"active": alist, "removed": rlist};
});
