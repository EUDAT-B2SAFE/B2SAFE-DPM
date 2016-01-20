function actionCtrl($scope, $http, $injector, $controller, policy,
  data_action) {
    'use strict';
    $scope.policy = policy;
    // $injector.invoke(dpmCtrl, this, {$scope: $scope});
    $controller('dpmCtrl', {$scope: $scope});

    var action_obj = data_action.getActions();

    // Remove this line $scope.operations = action_obj.operations;
    $scope.triggers = action_obj.triggers;
    // Remmove this line $scope.types = action_obj.types;
    $scope.actionTypes = action_obj.types;
    $scope.location_types = action_obj.location_types;

    // Read in the available actions using promises
    var getActions = $http({method: 'GET',
      url: '${CGI_URL}/query_actions.py', params: {qtype: 'types'} });

    getActions.then(function(results) {
      var data = results.data;
      action_obj.types = [];
      for (var idx = 0; idx < data.length; ++idx) {
        if (data[idx].length > 0) {
          action_obj.types = storeData(action_obj.types, data[idx][0]);
        }
      }
      $scope.actionTypes = action_obj.types;
      data_action.setActions(action_obj);
    });

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
        if (trname === 'date/time') {
            show = true;
        }
        return show;
    };

    // Check the period has been filled in correctly
    $scope.updatePeriod = function() {
      $scope.pristineFlags.action.period = false;
      $scope.invalidFlags.action.period = false;
      var elements = $scope.policy.trigger_period.name.split('-');
      if (elements.length < 6) {
        $scope.invalidFlags.action.period = true;
      } else {
        console.log('processing date ' + JSON.stringify(elements));
        for (var i = 0; i < elements.length; i++) {
          $scope.invalidFlags.action.period = true;
          if (i === 4) {
            if (elements[i] === '*' || (parseInt(elements[i]) >= 0 &&
              parseInt(elements[i]) <= 6)) {
              $scope.invalidFlags.action.period = false;
            } else {
              $scope.invalidFlags.action.period = true;
              break;
            }
          } else if (i === 5) {
            if (elements[i].length === 4) {
              if (elements[i] === '*' || ! isNaN(elements[i])) {
                $scope.invalidFlags.action.period = false;
              } else {
                $scope.invalidFlags.action.period = true;
                break;
              }
            }
          } else {
            if (i === 1) {
              if (elements[i] === '*' || (parseInt(elements[i]) >=0 &&
                parseInt(elements[i]) <= 59)) {
                $scope.invalidFlags.action.period = false;
              } else {
                $scope.invalidFlags.action.period = true;
                break;
              }
            } else if (i === 2) {
              if (elements[i] === '*' || (parseInt(elements[i]) >= 0 &&
                parseInt(elements[i]) <= 23)) {
                $scope.invalidFlags.action.period = false;
              } else {
                $scope.invalidFlags.action.period = true;
                break;
              }
            } else if (i === 3) {
              if (elements[i] === '*' || (parseInt(elements[i]) >=1 &&
                parseInt(elements[i]) <= 31)) {
                $scope.invalidFlags.action.period = false;
              } else {
                $scope.invalidFlags.action.period = true;
                break;
              }
            }
          }
        }
      }
      console.log('invalidFlags ' +$scope.invalidFlags.action.period);
    };

    // function to enable the trigger option
    $scope.changeTrigger = function(index) {
        var get_triggers = $http({method: 'GET',
            url: '${CGI_URL}/query_actions.py',
            params: {qtype: 'triggers'}
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
        $scope.pristineFlags.action.type = false;
        //$scope.policy.trigger.name = '--- Select ---';
    };

    // Update the Trigger
    $scope.updateTrigger = function() {
      $scope.pristineFlags.action.trigger = false;
    };

    // invoke the SourceTarget control
    // $injector.invoke(sourceTargetCtrl, this, {$scope: $scope});
    $controller('sourceTargetCtrl', {$scope: $scope});
}
