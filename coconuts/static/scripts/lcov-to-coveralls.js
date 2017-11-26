var coveralls = require('coveralls'),
    fs = require('fs');

var data = fs.readFileSync('coverage/lcov.info');
coveralls.getOptions(function(err, options) {
    coveralls.convertLcovToCoveralls(data.toString(), options, function(err, postData) {
        postData.source_files.forEach(function(x) {
            x.name = 'coconuts/static/' + x.name;
        });
        fs.writeFileSync('coverage/coveralls.json', JSON.stringify(postData));
    });
});
