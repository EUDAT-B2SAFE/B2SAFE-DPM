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
                    'build/admin/dpm_app.js.template': ['src/app/createPolicy/js/createUtils.js',
                                            'src/app/common/js/common_utils.js',
                                            'src/app/*/js/*.js', 
                                            '!src/app/admin/js/*.js',
                                            '!src/app/createProfile/js/*.js'],
                    'build/admin/register_app.js.template': [
                    'src/app/createProfile/js/register_app.js',
                    'src/app/common/js/common_utils.js',
                    'src/app/createProfile/js/*.js'],
                    'build/admin/admin_profile_app.js.template': [
                    'src/app/admin/js/admin_profile_app.js',
                    'src/app/admin/js/*.js'],
                    'build/admin/frontPageApp.js.template': [
                    'src/app/frontPage/js/frontPageApp.js',
                    'src/app/frontPage/js/FrontPageCtrl.js'],
                    'build/admin/errorUtils.js.template': [
                    'src/app/createProfile/js/errorUtils.js']
                },
            },
            // Build the config file - we have different locations for a
            // local installation and a production installation
            local_config: {
               files: {'build/cgi/dpm/config/policy.cfg.template': 
                    ['src/app/common/config/policy.cfg.template'],
               },
            },
            prod_config: {
                files: {'build/cgi/dpm/config/policy_schema.cfg':
                    ['src/app/common/config/policy_stub.cfg',
                     'src/app/common/config/policy_prod.cfg',
                     'src/app/common/config/dpm_admin_prod.cfg'],
                     'build/admin/policy_dbs.cfg':
                     ['src/app/common/config/policy_prod.cfg',
                     'src/app/common/config/admin_prod.cfg'],
                },
            },
            rzg_config: {
                files: {'build/cgi/dpm/config/policy_schema.cfg':
                    ['src/app/common/config/policy_stub.cfg',
                     'src/app/common/config/policy_rzg.cfg',
                     'src/app/common/config/dpm_admin_rzg.cfg'],
                     'build/admin/policy_dbs.cfg':
                     ['src/app/common/config/policy_rzg.cfg',
                     'src/app/common/config/admin_rzg.cfg'],
                },
            },
            // Build the css stylesheet
            css: {
                files: {"build/html/dpm/css/dpm.css": ['src/app/*/css/*',
                        '!/src/app/admin/css/*',
                        '!src/app/frontPage/css/*'],
                        "build/html/dpm/css/admin.css": ['src/app/admin/css/*'],
                        "build/html/dpm/css/frontpage.css":[
                        "src/app/frontPage/css/*"],
                },
            },
        },
        copy: {
            python: {
                files: [{expand: true, src: ['src/app/*/python/*.py', 
                                             '!src/app/*/python/configure_dpm.py'],
                                dest: 'build/cgi/dpm', flatten: true},
                    {src: 'src/app/common/python/configure_dpm.py',
                    dest: 'build/admin/configure_dpm.py'},
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
                    dest: 'build/html/dpm/script/bootstrap'},
                    {expand: true, cwd: 'src/script/bootstrap',
                    src: ['bootstrap-gh-pages/**'],
                    dest: 'build/html/dpm/script/bootstrap'},
                    {expand: true, cwd: 'src/script/ng-table-master',
                    src: ['**'],
                    dest: 'build/html/dpm/script/ng-table-master'},
                    {expand: true, cwd: 'src/script/jquery',
                    src: ['**'],
                    dest: 'build/html/dpm/script/jquery'},
                    {expand: true, cwd: 'src/script/angular',
                    src: ['**'],
                    dest: 'build/html/dpm//script/angular'}],
            },
            // Copy config files (only those not processed before)
            config: {
                files: [{expand: true,
                    src: ['src/app/common/config/*.data'],
                    dest: 'build/admin', flatten: true},
                    {expand: true,
                        src: ['src/app/common/config/*.template'],
                        dest: 'build/admin', flatten: true},
                    {expand: true,
                        src: ['src/app/common/config/*.schema'],
                        dest: 'build/admin', flatten: true},
                    {expand: true,
                        src: ['src/app/admin/config/*.txt'],
                        dest: 'build/cgi/dpm/config', flatten: true},
                ],
            },
            local_txt: {
                files: [{expand: true,
                    src: ['src/app/common/config/dpm_admin_local.txt'],
                    dest: 'build/cgi/dpm/config', flatten: true},
                ],
            },
            prod_txt: {
                files: [{expand: true,
                    src: ['src/app/common/config/dpm_admin_prod.txt'],
                    dest: 'build/cgi/dpm/config', flatten: true},
                ],
            },
            rzg_txt: {
                files: [{expand: true,
                    src: ['src/app/common/config/dpm_admin_rzg.txt'],
                    dest: 'build/cgi/dpm/config', flatten: true},
                ],
            },
            // Copy the html files
            html: {
                files: [{expand: true,
                            src: ['src/app/common/html/dpm.html',
                                'src/app/common/html/closed.html',
                                'src/app/common/html/declined.html',
                                'src/app/common/html/pending.html'],
                            dest: 'build/html/dpm', flatten: true},
                        {expand: true,
                            src: ['src/app/common/html/.htaccess'],
                            dest: 'build/html/dpm', flatten: true},
                        {expand: true,
                            src: ['src/app/createProfile/index.html'],
                            dest: 'build/html/dpm', flatten: true},
                        {expand: true,
                            cwd: 'src/app/createPolicy/html',
                            src: ['**', '!index.html'],
                            dest: 'build/html/dpm/template'},
                        {expand: true,
                            cwd: 'src/app/createProfile/html',
                            src: ['**', '!acknowledge.html', '!reg_tpl.html'],
                            dest: 'build/html/dpm'},
                        {expand: true,
                            cwd: 'src/app/createProfile/error_html',
                            src: ['**'],
                            dest: 'build/html/dpm/errors'},
                        {expand: true,
                            cwd: 'src/app/createProfile/html',
                            src: ['acknowledge.html', 'reg_tpl.html'],
                            dest: 'build/html/dpm/template'},
                        {expand: true,
                            cwd: 'src/app/displayLog/html',
                            src: ['**'],
                            dest: 'build/html/dpm/template'},
                        {expand: true,
                            cwd: 'src/app/listPolicy/html',
                            src: ['**'],
                            dest: 'build/html/dpm/template'},
                        {expand: true,
                            cwd: 'src/app/common/img',
                            src: ['**'],
                            dest: 'build/html/dpm/img'},
                        {expand: true,
                            src: ['src/app/admin/html/admin_profile.html'],
                            dest: 'build/html/dpm', flatten: 'true'},
                        {expand: true,
                            src: ['src/app/frontPage/html/frontpage.html'],
                            dest: 'build/html/dpm', flatten: 'true'},
                       ],
            }
        }
    });
    var env = grunt.option('env') || 'dev';
    if (env === 'prod') {
        grunt.registerTask('build', ['jshint', 'concat:js', 
                'concat:prod_config', 'concat:css', 'copy:python',
                'copy:script', 'copy:html', 'copy:config', 
                'copy:prod_txt']);
    } else if (env === "rzg") {
        grunt.registerTask('build', ['jshint', 'concat:js', 
                'concat:rzg_config', 'concat:css', 'copy:python',
                'copy:script', 'copy:html', 'copy:config', 
                'copy:rzg_txt']);
    } else {
        grunt.registerTask('build', ['jshint', 'concat:js',
                'concat:local_config', 'concat:css', 'copy:python',
                'copy:script', 'copy:html', 'copy:config',
                'copy:local_txt']);
    }
    grunt.registerTask('default', 'jshint');

};
