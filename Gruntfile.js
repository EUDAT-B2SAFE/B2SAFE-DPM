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
            js: {
                files: {
                    'build/js/dpm_app.js': ['src/app/*/js/*.js'],
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
                files: {"build/css/dpm.css": ['src/app/*/css/*'],
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
                ],
            },
            // Copy the html files
            html: {
                files: [{expand: true,
                            src: ['src/app/common/html/index.html'],
                            dest: 'build', flatten: true},
                        {expand: true,
                            cwd: 'src/app/createPolicy/html',
                            src: ['**'],
                            dest: 'build/template'},
                        {expand: true,
                            cwd: 'src/app/createProfile/html',
                            src: ['**'],
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
                        ],
            }
        }
    });
    var env = grunt.option('env') || 'dev';
    if (env === 'prod') {
        grunt.registerTask('build', ['jshint', 'concat:js', 
                'concat:prod_config', 'copy']);
    } else {
        grunt.registerTask('build', ['jshint', 'concat:js',
                'concat:local_config', 'concat:css', 'copy:python',
                'copy:script', 'copy:html', 'copy:config']);
    }
    grunt.registerTask('default', 'jshint');

};
