function actionCtrl($scope, $http, $injector, $controller, policy,
  data_action) {
    'use strict';
    $scope.policy = policy;
    // $injector.invoke(dpmCtrl, this, {$scope: $scope});
    $controller('dpmCtrl', {$scope: $scope});

    var action_obj = data_action.getActions();

    // Remove this line $scope.operations = action_obj.operations;
    $scope.triggers = action_obj.triggers;
    $scope.trigger_date = action_obj.trigger_date;
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
    $scope.showPeriodPeriod = function(trgDateType) {
      var show = false;
      if (typeof trgDateType !== 'undefined' && trgDateType !== 'date') {
        show = true;
      }
      return show;
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
      console.log('trigger_period ' + $scope.policy.trigger_period.name);
      var cron = later.parse.cron($scope.policy.trigger_period.name);
      console.log('cron is ' + JSON.stringify(cron));
      var cronElements = $scope.policy.trigger_period.name.split(' ');
      if (cronElements.length < 6) {
        $scope.invalidFlags.action.period = true;
      } else {
        var minutePattern = searchPattern('([1-5][0-9]|[0-9])');
        var minuteExp = new RegExp(minutePattern);
        $scope.invalidFlags.action.period = ! minuteExp.test(cronElements[0]);
        if (!$scope.invalidFlags.action.period) {
          var hourPattern = searchPattern('([2][0-3]|[1][0-9]|[0-9])');
          var hourExp = new RegExp(hourPattern);
          $scope.invalidFlags.action.period = ! hourExp.test(cronElements[1]);
        }
        if (!$scope.invalidFlags.action.period) {
          var datePattern = searchPattern('([3][0-1]|[1-2][0-9]|[0-9])');
          var dateExp = new RegExp(datePattern);
          $scope.invalidFlags.action.period = ! dateExp.test(cronElements[2]);
        }
        if (!$scope.invalidFlags.action.period) {
          var monthPattern = searchPattern('([1][0-2]|[0-9])');
          var monthExp = new RegExp(monthPattern);
          $scope.invalidFlags.action.period = ! monthExp.test(cronElements[3]);
        }
        if (!$scope.invalidFlags.action.period) {
          var dowPattern = searchPattern('([0-6])');
          var dowExp = new RegExp(dowPattern);
          $scope.invalidFlags.action.period = ! dowExp.test(cronElements[4]);
        }
        if (!$scope.invalidFlags.action.period) {
          var yearPattern = searchPattern('([2][0-9][0-9][0-9])');
          var yearExp = new RegExp(yearPattern);
          $scope.invalidFlags.action.period = ! yearExp.test(cronElements[5]);
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
      console.log('trigger value is ' + $scope.policy.trigger.name);
      if ($scope.policy.trigger.name === 'date/time') {
        var getTriggerDate = $http({method: 'GET',
            url: '${CGI_URL}/query_actions.py',
            params: {qtype: 'trigger_date'}});
        getTriggerDate.then(function(results) {
          var data = results.data;
          action_obj.trigger_date = [];
          action_obj.trigger_date_value = [];
          for (var idx = 0; idx < data.length; ++idx) {
            if (data[idx].length > 0) {
              action_obj.trigger_date = storeData(action_obj.trigger_date,
                                                  data[idx][0]);
              action_obj.trigger_date_value = storeData(action_obj.trigger_date_value,
                                                        data[idx][1]);
            }
          }
          $scope.trigger_date = action_obj.trigger_date;
          data_action.setActions(action_obj);
        });
      }
      $scope.pristineFlags.action.trigger = false;
    };

    $scope.updateTriggerDate = function() {
      var dateIndex = -1;
      for (var j=0; j < action_obj.trigger_date.length; ++j) {
        if (action_obj.trigger_date[j].name === $scope.policy.trigger_date.name) {
          dateIndex = j;
          break;
        }
      }
      if (dateIndex >= 0) {
        $scope.policy.trigger_period = {'name': action_obj.trigger_date_value[dateIndex].name};
      }
      //console.log('trigger_period ' + JSON.stringify(action_obj.trigger_date_value));
      $scope.pristineFlags.action.trigger_date = false;
      $scope.invalidFlags.action.period = false;
    };

    $('#periodDate').datetimepicker({
      locale: 'en-gb',
      format: 'YYYY-MM-DDTHH:mmZ'
    }).on('dp.change',
      function(e){
        //console.log('date is ' + e.date);
        //console.log('e is ' + JSON.stringify(e));
        var pDate = new Date(e.date);
        var month = pDate.getMonth() + 1;
        var hours = pDate.getHours();
        var dom = pDate.getDate();
        var minutes = pDate.getMinutes();
        if (dom <= 9) {
          dom = '0' + dom;
        }
        if (month <= 9) {
          month = '0' + month;
        }
        if (hours <= 9) {
          hours = '0' + hours;
        }
        if (minutes <= 9) {
          minutes = '0' + minutes;
        }
        var dateString = pDate.getFullYear() + '-' + month + '-' + dom + 'T' +
          hours + ':' + minutes + '+00:00';
        var cronString = minutes + ' ' + hours + ' ' + dom + ' ' + month +
          ' * ' + pDate.getFullYear();
        $scope.policy.trigger_period.name = cronString;
        $scope.policy.dateString = dateString;
        var dateStamp = Date.parse(dateString);
        if (isNaN(dateStamp) === true) {
          $scope.invalidFlags.action.period_date = true;
        } else {
          $scope.invalidFlags.action.period_date = false;
        }
        $scope.pristineFlags.action.period_date = false;
        // Since we are outside of angular we need to update the view
        $scope.$digest();
        //console.log('jquery flag ' + $scope.invalidFlags.action.period_date);
      }
    );

    $scope.showPeriodDate = function(periodType) {
      var show = false;
      if (typeof periodType !== 'undefined' && periodType === 'date') {
        show = true;
      }
      return show;
    };

    $scope.updatePeriodDate = function() {
      //console.log('we are called! ' + $scope.policy.trigger_period.name);
      //console.log('dateString ' + $scope.policy.dateString);
      var dateStamp = Date.parse($scope.policy.dateString);
      //console.log('dateStamp ' + dateStamp);
      if (isNaN(dateStamp) === true) {
        $scope.policy.trigger_period.name = "";
        $scope.invalidFlags.action.period_date = true;
      } else {
        $scope.invalidFlags.action.period_date = false;
      }
      //console.log('flag is ' + $scope.invalidFlags.action.period_date);
    };

    // invoke the SourceTarget control
    // $injector.invoke(sourceTargetCtrl, this, {$scope: $scope});
    $controller('sourceTargetCtrl', {$scope: $scope});
}

function searchPattern(patt1) {
  var pattern = '';
  var patt2 =  '^[*]$';
  var patt3 = '((' + patt1 + '[\\-]' + patt1 + '))|^(' + patt1 + '(,(' + patt1 +
    '[\\-]' + patt1 + ')|(,' + patt1 + '))+)$|(([*]|' + patt1 + ')[/]' + patt1 + ')';
  pattern = '^' + patt1 + '$' + '|' + patt2 + '|' + patt3;
  return pattern;
}
