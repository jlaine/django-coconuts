'use strict';
module.exports = function (grunt) {
    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        jshint: {
            files: ['coconuts/js/coconuts.js']
        },
        karma: {
            unit: {
                configFile: 'config/karma-unit.conf.js'
            }
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                src: 'coconuts/js/coconuts.js',
                dest: 'coconuts/js/coconuts.min.js'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-karma');
    grunt.registerTask('default', ['jshint', 'uglify']);
};
