registerApp.filter("startFrom", function() {
    return function(input, start) {
        start = +start;
        aslice = input.slice(start);
        return aslice;
    };
});
