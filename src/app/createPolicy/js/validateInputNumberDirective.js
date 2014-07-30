dpmApp.directive("validateInputNumber", function() {
    return {
        restrict: 'A',
        require: "ngModel",
        link: function(scope, elem, attr, ctrl) {
            ctrl.$parsers.unshift(function(aval) {
                if (!isNaN(parseFloat(aval)) && isFinite(aval)) {
                    ctrl.$setValidity("required", true);
                    return aval;
                } else {
                    ctrl.$setValidity("required", false);
                    return undefined;
                }
            });
        }
    };
});
