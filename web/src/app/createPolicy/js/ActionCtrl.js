function actionCtrl($scope, $http, $injector, policy, disabled_flags, 
        data_action, submitFlag) {
    $scope.policy = policy;
    $injector.invoke(dpmCtrl, this, {$scope: $scope});

    var disabled_flags_obj = disabled_flags.getFlags();
    var action_obj = data_action.getActions();

    $scope.operations = action_obj.operations;
    $scope.triggers = action_obj.triggers;
    $scope.types = action_obj.types;
    $scope.location_types = action_obj.location_types;

    $scope.action_type = disabled_flags_obj.action_type;
    $scope.action_trigger = disabled_flags_obj.action_trigger;
    $scope.tgt_organisation_disabled = disabled_flags_obj.tgt_organisation;
   
    // Read in the available actions using promises
    var actions = $http({method: "GET", 
        url: "/cgi-bin/dpm/query_actions.py",
        params: {qtype: "operations"}});

    actions.then(function (result) {
        var data = result.data;
        for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
                action_obj.operations = 
                    storeData(action_obj.operations, data[idx][0]);
            }
        }
        $scope.operations = action_obj.operations;
        data_action.setActions(action_obj);
    }
    );
    
    $scope.period = getPeriod();
   
    // Only show the date fields for the date option
    var tdate = new Date();
    $scope.showDate = function(trname) {
        var show = false;
        if (trname == "date") {
            show = true;
            if (typeof $scope.trigger_date == "undefined") {
                $scope.trigger_date = tdate;
                $scope.policy.trigger_date = getIsoDate(tdate);
            }
        }
        return show; 
    };

    $scope.datClear = function() {
    };
    $scope.datOpen = function($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };

    $scope.updateDate = function() {
        $scope.policy.trigger_date = getIsoDate($scope.trigger_date);
    };

    // Only show the period fields for the periodic option
    $scope.showPeriod = function(trname) {
        var show = false;
        if (trname == "period") {
            show = true;
        }
        return show;
    };

    // function to enable the action type option
    $scope.changeType = function() {
        var get_types = $http({method: "GET", 
            url: "/cgi-bin/dpm/query_actions.py", params: {qtype: "types",
                operation: $scope.policy.action.name} });
        get_types.then(function(results) {
            var data = results.data;
            action_obj.types = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    action_obj.types = 
                            storeData(action_obj.types, data[idx][0]);
                }
            }
            $scope.types = action_obj.types;
            data_action.setActions(action_obj);
        });
        disabled_flags_obj.action_type = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.pristineFlags.action.action = false;
        $scope.policy.type.name = '--- Select a Type ---';
        $scope.action_type = disabled_flags_obj.action_type;
    };


    // function to enable the trigger option
    $scope.changeTrigger = function() {
        var get_triggers = $http({method: "GET", 
            url: "/cgi-bin/dpm/query_actions.py", 
            params: {qtype: "triggers",
                operation: $scope.policy.action.name, 
            type: $scope.policy.type.name}
        });
        get_triggers.then(function(results) {
            var data = results.data;
            action_obj.triggers = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    action_obj.triggers = 
                        storeData(action_obj.triggers, data[idx][0]);
                }
            }
            $scope.triggers = action_obj.triggers;
            data_action.setActions(action_obj);
        });
        disabled_flags_obj.action_trigger = false;
        disabled_flags.setFlags(disabled_flags_obj);
        $scope.pristineFlags.action.type = false;
        $scope.policy.trigger.name = "--- Select a Trigger ---";
        $scope.action_trigger = disabled_flags_obj.action_trigger;
    };

    // Read from the database the available locations
    $scope.changeOrganisation = function() {
        var get_organisations = $http({method: "GET", 
            url: "/cgi-bin/dpm/query_actions.py", 
            params: {qtype: "organisations"}});
        
        get_organisations.then(function(results) {
            var data = results.data;
            action_obj.organisations = [];
            for (var idx = 0; idx < data.length; ++idx) {
                if (data[idx].length > 0) {
                    action_obj.organisations = 
                        storeData(action_obj.organisations, data[idx][0]);
                }
            }
            $scope.organisations = action_obj.organisations;
            data_action.setActions(action_obj);
            disabled_flags_obj.tgt_organisation = false;
            disabled_flags.setFlags(disabled_flags_obj);
            $scope.pristineFlags.action.trigger = false;
            $scope.policy.target.organisation.name = "--- Select an Organisation ---";
            $scope.tgt_organisation_disabled = disabled_flags_obj.tgt_organisation;
 
        });
    };

    // invoke the SourceTarget control
    $injector.invoke(sourceTargetCtrl, this, {$scope: $scope});
}
