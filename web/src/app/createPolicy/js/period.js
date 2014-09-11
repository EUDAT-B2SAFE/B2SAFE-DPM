function getPeriod() {
    var periodObj = {};
    var weekday = [{name: "*"}];
    for (i = 0; i < 7; i++) {
        weekday.push({name: i});
    }

    var month = new Array({name: "*"});
    for (i = 0; i < 12; i++) {
        month.push({name: i});
    }
 
    var day = new Array({name: "*"});
    for (i = 0; i < 32; i++) {
        day.push({name: i});
    }
 
    var hour = new Array({name: "*"});
    for (i = 0; i < 24; i++) {
        hour.push({name: i});
    }
 
    var minute = new Array({name: "*"});
    for (i = 0; i < 60; i++) {
        minute.push({name: i});
    }
    periodObj = {month: month, weekday: weekday, day: day, hour: hour,
        minute: minute};
    return periodObj;
}
