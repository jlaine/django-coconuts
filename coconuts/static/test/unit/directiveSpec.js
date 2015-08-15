describe('Directives', function() {
    beforeEach(module('coconuts'));

    describe('coFile', function() {
        var elem, scope;
        beforeEach(inject(function($compile, $rootScope) {
            var compiled = $compile('<input type="file" co-file="csv_file"/>');
            scope = $rootScope.$new();
            elem = compiled(scope);
        }));

        it('should select no file', function() {
            elem.trigger('change');
            expect(scope.csv_file).toBe(undefined);
        });
    });

    describe('coThumbnail', function() {
        var elem, scope;
        beforeEach(inject(function($compile, $rootScope) {
            var compiled = $compile('<div co-thumbnail="some_file"></div>');
            scope = $rootScope.$new();
            elem = compiled(scope);
        }));

        it('should handle image file', function() {
            scope.some_file = {
                image: { width: 1024, height: 768 },
                mimetype: 'image/jpeg',
                name: 'bar.jpg',
                path: '/foo/bar.jpg'
            };
            scope.$digest();

            var img = elem.find('img.thumb');
            expect(img.attr('src')).toBe('images/render/foo/bar.jpg?size=128');

            img = elem.find('img.icon');
            expect(img.length).toBe(0);
        });

        it('should handle video file', function() {
            scope.some_file = {
                video: { width: 1024, height: 768 },
                mimetype: 'video/mp4',
                name: 'bar.jpg',
                path: '/foo/bar.mp4'
            };
            scope.$digest();

            var img = elem.find('img.thumb');
            expect(img.attr('src')).toBe('images/render/foo/bar.mp4?size=128');

            img = elem.find('img.icon');
            expect(img.attr('src')).toBe('/static/coconuts/img/video-x-generic.png');
        });

        it('should handle text file', function() {
            scope.some_file = {
                mimetype: 'text/plain',
                name: 'bar.txt',
                path: '/foo/bar.txt'
            };
            scope.$digest();

            var img = elem.find('img.thumb');
            expect(img.length).toBe(0);

            img = elem.find('img.icon');
            expect(img.attr('src')).toBe('/static/coconuts/img/text-x-generic.png');
        });

        it('should handle other file', function() {
            scope.some_file = {
                mimetype: 'application/octet-stream',
                name: 'bar.dat',
                path: '/foo/bar.dat'
            };
            scope.$digest();

            var img = elem.find('img.thumb');
            expect(img.length).toBe(0);

            img = elem.find('img.icon');
            expect(img.attr('src')).toBe('/static/coconuts/img/unknown.png');
        });
    });
});
