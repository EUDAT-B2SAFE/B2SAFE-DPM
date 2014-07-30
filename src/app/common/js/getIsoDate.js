function getIsoDate(idate) {
    var t_date;
    var cur_date = idate.getDate();
    var cur_month = idate.getMonth() + 1;
    var cur_year = idate.getFullYear();
    t_date = cur_year + "-" + cur_month + "-" + cur_date;
    return t_date;
}
