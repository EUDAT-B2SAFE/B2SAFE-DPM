dpmApp.directive("validateSelect", function() {
    return {
        restrict: 'A',
        require: "ngModel",
        link: function(scope, elem, attrs, ctrl) {
            ctrl.$parsers.unshift(function(aval) {
                if (aval && aval.name !== "") {
                    ctrl.$setValidity("required", true);
                    return aval;
                } else {
                    ctrl.$setValidity("required", false);
                    return "";
                }
            });
        }
    };
});
