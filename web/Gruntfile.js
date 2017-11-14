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
               files: {'build/cgi/config/policy.cfg.template':
                    ['src/app/common/config/policy.cfg.template'],
               },
            },
            prod_config: {
                files: {'build/cgi/config/policy_schema.cfg':
                    ['src/app/common/config/policy_stub.cfg',
                     'src/app/common/config/policy_prod.cfg',
                     'src/app/common/config/dpm_admin_prod.cfg'],
                     'build/admin/policy_dbs.cfg':
                     ['src/app/common/config/policy_prod.cfg',
                     'src/app/common/config/admin_prod.cfg'],
                },
            },
            rzg_config: {
                files: {'build/cgi/config/policy_schema.cfg':
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
                files: {'build/html/css/dpm.css': ['src/app/*/css/*',
                        '!/src/app/admin/css/*',
                        '!src/app/frontPage/css/*'],
                        'build/html/css/admin.css': ['src/app/admin/css/*'],
                        'build/html/css/frontpage.css':[
                        'src/app/frontPage/css/*'],
                },
            },
        },
        copy: {
            python: {
                files: [{expand: true, src: ['src/app/*/python/*.py',
                                             '!src/app/*/python/configure_dpm.py',
                                             '!src/app/*/python/updatepolicy.py',
                                             '!src/app/*/python/querypolicy.py',
                                             '!src/app/*/python/fetch_policy.py',
                                             '!src/app/policyCLI/python/app/*.py'],
                                dest: 'build/cgi', flatten: true},
                    {src: 'src/app/common/python/configure_dpm.py',
                    dest: 'build/admin/configure_dpm.py'},
                    {expand: true,
                    src: ['src/app/createPolicy/python/generateDS-2.12b/**'],
                                dest: 'build/cgi/generateDS-2.12b',
                                flatten: true},
                    {expand: true,
                    src: ['src/app/policyCLI/python/app/*.py',
                    'src/app/policyCLI/python/app/*.wsgi',
                    'src/app/policyCLI/python/app/requirements.txt'],
                    dest: 'build/wsgi', flatten: true},
                    {expand: true, cwd: 'src/app/policyCLI/python/tests',
                    src: ['**'],
                    dest: 'build/wsgi-test'}],
            },
            options: {
            mode: true
            },
            // Copy third party scripts
            script: {
                files: [{expand: true, cwd: 'src/script/bootstrap',
                    src: ['dist/**'],
                    dest: 'build/html/script/bootstrap'},
                    {expand: true, cwd: 'src/script/bootstrap',
                    src: ['bootstrap-gh-pages/**'],
                    dest: 'build/html/script/bootstrap'},
                    {expand: true, cwd: 'src/script/ng-table-master',
                    src: ['**'],
                    dest: 'build/html/script/ng-table-master'},
                    {expand: true, cwd: 'src/script/jquery',
                    src: ['**'],
                    dest: 'build/html/script/jquery'},
                    {expand: true, cwd: 'src/script/angular',
                    src: ['**'],
                    dest: 'build/html/script/angular'},
                    {expand: true, cwd: 'src/script/bootstrap-datetimepicker-4.17.37/build',
                     src: ['**'],
                     dest: 'build/html/script/bootstrap-datetimepicker'},
                    {expand: true, cwd: 'src/script/moment-2.11.1/min',
                     src: ['**'],
                     dest: 'build/html/script/moment/min'},
                    {expand: true, cwd: 'src/script/later-1.2.0',
                     src: ['**'],
                     dest: 'build/html/script/later-1.2.0'}],
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
                        dest: 'build/cgi/config', flatten: true},
                ],
            },
            local_txt: {
                files: [{expand: true,
                    src: ['src/app/common/config/dpm_admin_local.txt'],
                    dest: 'build/cgi/config', flatten: true},
                ],
            },
            prod_txt: {
                files: [{expand: true,
                    src: ['src/app/common/config/dpm_admin_prod.txt'],
                    dest: 'build/cgi/config', flatten: true},
                ],
            },
            rzg_txt: {
                files: [{expand: true,
                    src: ['src/app/common/config/dpm_admin_rzg.txt'],
                    dest: 'build/cgi/config', flatten: true},
                ],
            },
            // Copy the html files
            html: {
                files: [{expand: true,
                            src: ['src/app/common/html/dpm.html.template',
                                'src/app/common/html/closed.html',
                                'src/app/common/html/declined.html',
                                'src/app/common/html/pending.html',
                                'src/app/common/html/session_renewed.html'],
                            dest: 'build/html', flatten: true},
                        {expand: true,
                            src: ['src/app/common/html/dpm.html.template'],
                            dest: 'build/admin', flatten: true},
                        {expand: true,
                            src: ['src/app/common/html/.htaccess'],
                            dest: 'build/html', flatten: true},
                        {expand: true,
                            src: ['src/app/createProfile/index.html'],
                            dest: 'build/html', flatten: true},
                        {expand: true,
                            cwd: 'src/app/createPolicy/html',
                            src: ['**', '!index.html'],
                            dest: 'build/html/template'},
                        {expand: true,
                            cwd: 'src/app/createProfile/html',
                            src: ['**', '!acknowledge.html', '!reg_tpl.html'],
                            dest: 'build/html'},
                        {expand: true,
                            cwd: 'src/app/createProfile/error_html',
                            src: ['**'],
                            dest: 'build/html/errors'},
                        {expand: true,
                            cwd: 'src/app/createProfile/html',
                            src: ['acknowledge.html', 'reg_tpl.html'],
                            dest: 'build/html/template'},
                        {expand: true,
                            cwd: 'src/app/displayLog/html',
                            src: ['**'],
                            dest: 'build/html/template'},
                        {expand: true,
                            cwd: 'src/app/listPolicy/html',
                            src: ['**'],
                            dest: 'build/html/template'},
                        {expand: true,
                            cwd: 'src/app/common/img',
                            src: ['**'],
                            dest: 'build/html/img'},
                        {expand: true,
                            src: ['src/app/admin/html/admin_profile.html'],
                            dest: 'build/html', flatten: 'true'},
                        {expand: true,
                            src: ['src/app/frontPage/html/frontpage.html'],
                            dest: 'build/html', flatten: 'true'},
                       ],
            }
        }
    });

    grunt.registerTask('build', ['jshint', 'concat:js',
                'concat:local_config', 'concat:css', 'copy:python',
                'copy:script', 'copy:html', 'copy:config',
                'copy:local_txt']);
    grunt.registerTask('default', 'jshint');
};
