// Factory to create a community manager object
registerApp.factory('cMgr', function() {
    var cMgr = {firstname: '', lastname: '', email: '', username: '',
                password: '', communities: [{name: ''}]};
    return cMgr;
});
