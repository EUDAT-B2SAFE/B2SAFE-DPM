// Service for handling pages
var page = function() {
    this.firstPage = true;
    this.count = 0;
};
// Register the service with the module
dpmApp.service("page", page);
