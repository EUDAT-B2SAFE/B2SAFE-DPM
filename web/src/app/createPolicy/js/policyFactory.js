var policy = function() {
    var source_type = {name: '--- Select a Type ---'};
    var dateString = '';
    var target_type = {name: '--- Select a Type ---'};
    var type = {name: '--- Select a Type ---'};
    var trigger = {name: '--- Select ---'};
    var trigger_period = '';
    var trigger_date = {name: '--- Select ---'};
    var source_site = {name: '--- Select ---'};
    var source_system = {name: 'iRODS'};
    var source_resource = {name: ''};
    var target_system = {name: 'iRODS'};
    var target_site = {name: '--- Select ---'};
    var target_resource = {name: ''};
    var source_organisation = {name: 'EUDAT'};
    var target_organisation = {name: 'EUDAT'};
    var source_identifier = {name: ''};
    var target_identifier = {name: ''};

    var sources = new Array({
        identifier: source_identifier,
        type: source_type,
        organisation: source_organisation,
        system: source_system,
        hostname: source_site,
        resource: source_resource
    });

    var targets = new Array({
        identifier: target_identifier,
        type: target_type,
        organisation: target_organisation,
        system: target_system,
        hostname: target_site,
        resource: target_resource
    });

    var policyObj = {name: '', id: '',
        version: '1.0', uuid: '', author: '', community: '',
        type: type,
        trigger: trigger,
        trigger_period: trigger_period,
        trigger_date: trigger_date,
        dateString: dateString,
        sources: sources,
        targets: targets};
    return policyObj;
};

// create a factory to generate a policy object
dpmApp.factory('policy', policy);
