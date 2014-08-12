dpmApp.service('logData', function() {
    var logDataObj = [];
    return {
        getObj: function() {
            return logDataObj;
        },
        setObj: function(valobj) {
            logDataObj = valobj;
        }
    };
});
