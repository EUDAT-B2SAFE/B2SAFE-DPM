var dpmApp = angular.module('dpmApp', ['ngRoute', 'ui.bootstrap', 'ngTable']);

// The list of routes. Each 'page' of the form is a route
var locList = [{url: '/personal', path: 'template/personal.html'},
               {url: '/dataset_action', path: 'template/dataset_action.html'},
               {url: '/summary', path: 'template/summary.html'},
              ];

var logList = [{url: '/listlogs', path: 'template/listlogs.html'}];

var maxPage = 1;
var minPage = 0;
var ds_count = 0;

function dpmFormConfig($routeProvider) {
    $routeProvider.
        when('/', {
            controller: personalCtrl,
            templateUrl: locList[0].path
        }).
        when(locList[0].url, {
            controller: personalCtrl,
            templateUrl: locList[0].path
        }).
        when(locList[1].url, {
            controller: datasetCtrl,
            templateUrl: locList[1].path
        }).
        when(locList[2].url, {
            controller: confirmCtrl,
            templateUrl: locList[2].path
        }).
        when(logList[0].url, {
            controller: logsCtrl,
            templateUrl: logList[0].path
        }).
        when('/complete', {
            controller: completeCtrl,
            templateUrl: 'template/complete.html'
        }).
        otherwise({
            redirectTo: '/'
        });
}

dpmApp.config(dpmFormConfig);

function storeData(arr, val) {
    var duplicate = false;
    var i;
    for (i = 0; i < arr.length; i++) {
        if (val == arr[i].name) {
            duplicate = true;
            break;
        }
    }
    if (! duplicate) {
        arr.push({name: val});
    }
    return arr;
}
