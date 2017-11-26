module.exports = function(config) {
    config.set({
        browsers: ['ChromeHeadless'],
        captureTimeout: 10000,
        colors: false,
        coverageReporter: {
            type: 'lcovonly',
            dir: 'coverage',
            subdir: '.'
        },
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
        preprocessors: {
            'coconuts/js/coconuts.js': 'coverage',
        },
        reporters: ['coverage', 'spec']
    });
};
