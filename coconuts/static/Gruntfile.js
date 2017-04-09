'use strict';
module.exports = function (grunt) {
    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        copy: {
            css: {
                files: [
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules',
                        src: [
                            '**/bootstrap.min.css'
                        ],
                        dest: 'coconuts/css'
                    }
                ]
            },
            js: {
                files: [
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules',
                        src: [
                            '**/angular.min.js',
                            '**/angular-animate.min.js',
                            '**/angular-resource.min.js',
                            '**/angular-route.min.js',
                            '**/angular-touch.min.js',
                            '**/bootstrap.min.js',
                            '**/jquery.min.js'
                        ],
                        dest: 'coconuts/js'
                    }
                ]
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

    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.registerTask('default', ['copy', 'uglify']);
};
