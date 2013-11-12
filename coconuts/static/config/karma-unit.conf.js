module.exports = function(config) {
    config.set({
        basePath: '..',
        files: [
            'coconuts/js/jquery.min.js',
            'coconuts/js/angular.min.js',
            'coconuts/js/angular-animate.min.js',
            'coconuts/js/angular-resource.min.js',
            'coconuts/js/angular-route.min.js',
            'coconuts/js/angular-touch.min.js',
            'test/lib/*.js',
            'coconuts/js/coconuts.js',
            'test/unit/*.js'
        ],
        frameworks: ['jasmine'],
        plugins: [
            'karma-chrome-launcher',
            'karma-coverage',
            'karma-jasmine',
            'karma-junit-reporter',
            'karma-phantomjs-launcher'
        ],
        preprocessors: {
            'coconuts/js/coconuts.js': 'coverage',
        },

        // FIXME: why the extra ".." ?
        coverageReporter: { type: 'cobertura', file: '../../../coverage-unit.xml' },
        junitReporter: { outputFile: '../../test-unit.xml', suite: 'unit' },

        // common settings
        browsers: ['PhantomJS'],
        captureTimeout: 10000,
        colors: false,
        //logLevel: LOG_INFO,
        reporters: ['coverage', 'dots', 'junit'],
        singleRun: true
    });
};
