module.exports = function (grunt) {
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-copy');

    grunt.initConfig({
        // Lint our javascript files
        jshint: {
            options: {
                eqnull: true
            },
            all: ['Gruntfile.js', 'src/app/*/js/*.js']
        },
        concat: {
            // Build the javascript module from the individual controllers
            // services, factories etc
            // Order is important! The module needs to be defined first
            // then everything else
            js: {
                files: {
                    'build/js/dpm_app.js': ['src/app/createPolicy/js/createUtils.js',
                                            'src/app/common/js/common_utils.js',
                                            'src/app/*/js/*.js', 
                                            '!src/app/admin/js/*.js',
                                            '!src/app/createProfile/js/*.js'],
                    'build/js/register_app.js': [
                    'src/app/createProfile/js/register_app.js',
                    'src/app/common/js/common_utils.js',
                    'src/app/createProfile/js/*.js'],
                    'build/js/admin_profile_app.js': [
                    'src/app/admin/js/admin_profile_app.js',
                    'src/app/admin/js/*.js'],
                    'build/js/frontPageApp.js': [
                    'src/app/frontPage/js/frontPageApp.js',
                    'src/app/frontPage/js/FrontPageCtrl.js'],
                },
            },
            // Build the config file - we have different locations for a
            // local installation and a production installation
            local_config: {
               files: {'build/cgi/dpm/config/policy_schema.cfg': 
                   ['src/app/common/config/policy_stub.cfg', 
                    'src/app/common/config/policy_local.cfg'],
                    'build/admin/policy_dbs.cfg': 
                    ['src/app/common/config/policy_local.cfg',
                     'src/app/common/config/admin.cfg'],
               },
            },
            prod_config: {
                files: {'build/cgi/dpm/config/policy_schema.cfg':
                    ['src/app/common/config/policy_stub.cfg',
                     'src/app/common/config/policy_prod.cfg'],
                     'build/admin/policy_dbs.cfg':
                     ['src/app/common/config/policy_prod.cfg',
                     'src/app/common/config/admin.cfg'],
                },
            },
            // Build the css stylesheet
            css: {
                files: {"build/css/dpm.css": ['src/app/*/css/*',
                        '!/src/app/admin/css/*',
                        '!src/app/frontPage/css/*'],
                        "build/css/admin.css": ['src/app/admin/css/*'],
                        "build/css/frontpage.css":[
                        "src/app/frontPage/css/*"],
                },
            },
        },
        copy: {
            python: {
                files: [{expand: true, src: ['src/app/*/python/*.py', 
                                             '!src/app/*/python/populate_db.py'],
                                dest: 'build/cgi/dpm', flatten: true},
                    {src: 'src/app/createPolicy/python/populate_db.py',
                    dest: 'build/admin/populate_db.py'},
                    {expand: true, 
                    src: ['src/app/createPolicy/python/generateDS-2.12b/**'], 
                                dest: 'build/cgi/dpm/generateDS-2.12b', 
                                flatten: true}],
            },
            options: {
            mode: true
            },
            // Copy third party scripts
            script: {
                files: [{expand: true, cwd: 'src/script/bootstrap',
                    src: ['dist/**'],
                    dest: 'build/script/bootstrap'},
                    {expand: true, cwd: 'src/script/bootstrap',
                    src: ['bootstrap-gh-pages/**'],
                    dest: 'build/script/bootstrap'},
                    {expand: true, cwd: 'src/script/ng-table-master',
                    src: ['**'],
                    dest: 'build/script/ng-table-master'},
                    {expand: true, cwd: 'src/script/jquery',
                    src: ['**'],
                    dest: 'build/script/jquery'},
                    {expand: true, cwd: 'src/script/angular',
                    src: ['**'],
                    dest: 'build/script/angular'}],
            },
            // Copy config files (only those not processed before)
            config: {
                files: [{expand: true,
                    src: ['src/app/common/config/*.data'],
                    dest: 'build/admin', flatten: true},
                    {expand: true,
                        src: ['src/app/common/config/*.schema'],
                        dest: 'build/admin', flatten: true},
                    {expand: true,
                        src: ['src/app/admin/config/*.txt'],
                        dest: 'build/cgi/dpm/config', flatten: true},
                ],
            },
            // Copy the html files
            html: {
                files: [{expand: true,
                            src: ['src/app/common/html/dpm.html'],
                            dest: 'build', flatten: true},
                        {expand: true,
                            src: ['src/app/common/html/.htaccess'],
                            dest: 'build', flatten: true},
                        {expand: true,
                            src: ['src/app/createProfile/index.html'],
                            dest: 'build', flatten: true},
                        {expand: true,
                            cwd: 'src/app/createPolicy/html',
                            src: ['**', '!index.html'],
                            dest: 'build/template'},
                        {expand: true,
                            cwd: 'src/app/createProfile/html',
                            src: ['**', '!acknowledge.html', '!reg_tpl.html'],
                            dest: 'build'},
                        {expand: true,
                            cwd: 'src/app/createProfile/error_html',
                            src: ['**'],
                            dest: 'build/errors'},
                        {expand: true,
                            cwd: 'src/app/createProfile/html',
                            src: ['acknowledge.html', 'reg_tpl.html'],
                            dest: 'build/template'},
                        {expand: true,
                            cwd: 'src/app/displayLog/html',
                            src: ['**'],
                            dest: 'build/template'},
                        {expand: true,
                            cwd: 'src/app/listPolicy/html',
                            src: ['**'],
                            dest: 'build/template'},
                        {expand: true,
                            cwd: 'src/app/common/img',
                            src: ['**'],
                            dest: 'build/img'},
                        {expand: true,
                            src: ['src/app/admin/html/admin_profile.html'],
                            dest: 'build', flatten: 'true'},
                        {expand: true,
                            src: ['src/app/frontPage/html/frontpage.html'],
                            dest: 'build', flatten: 'true'},
                        ],
            }
        }
    });
    var env = grunt.option('env') || 'dev';
    if (env === 'prod') {
        grunt.registerTask('build', ['jshint', 'concat:js', 
                'concat:prod_config', 'concat:css', 'copy:python',
                'copy:script', 'copy:html', 'copy:config']);
    } else {
        grunt.registerTask('build', ['jshint', 'concat:js',
                'concat:local_config', 'concat:css', 'copy:python',
                'copy:script', 'copy:html', 'copy:config']);
    }
    grunt.registerTask('default', 'jshint');

};
