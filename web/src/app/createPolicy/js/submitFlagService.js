dpmApp.service('submitFlag', function() {
    var sflag = {flag: false, active: false, submitted: false, 
        fieldsOK: false, confirm: false};
    return {
        getObj: function() {
            return sflag;
        },
        setObj: function(valobj) {
            sflag = valobj;
        }
    };
});
