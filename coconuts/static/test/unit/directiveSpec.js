function path(url) {
    return '/' + url.split('/').slice(3).join('/');
}

describe('Directives', function() {
    beforeEach(module('coconuts'));

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

            var img = elem.find('img');
            expect(img.length).toBe(1);

            expect(img[0].className).toBe('thumb ng-scope');
            expect(path(img[0].src)).toBe('/images/render/foo/bar.jpg?size=128');
        });

        it('should handle video file', function() {
            scope.some_file = {
                video: { width: 1024, height: 768 },
                mimetype: 'video/mp4',
                name: 'bar.jpg',
                path: '/foo/bar.mp4'
            };
            scope.$digest();

            var img = elem.find('img');
            expect(img.length).toBe(2);

            expect(img[0].className).toBe('thumb ng-scope');
            expect(path(img[0].src)).toBe('/images/render/foo/bar.mp4?size=128');

            expect(img[1].className).toBe('icon ng-scope');
            expect(path(img[1].src)).toBe('/static/coconuts/img/video-x-generic.png');
        });

        it('should handle text file', function() {
            scope.some_file = {
                mimetype: 'text/plain',
                name: 'bar.txt',
                path: '/foo/bar.txt'
            };
            scope.$digest();

            var img = elem.find('img');
            expect(img.length).toBe(1);

            expect(img[0].className).toBe('icon ng-scope');
            expect(path(img[0].src)).toBe('/static/coconuts/img/text-x-generic.png');
        });

        it('should handle other file', function() {
            scope.some_file = {
                mimetype: 'application/octet-stream',
                name: 'bar.dat',
                path: '/foo/bar.dat'
            };
            scope.$digest();

            var img = elem.find('img');
            expect(img.length).toBe(1);

            expect(img[0].className).toBe('icon ng-scope');
            expect(path(img[0].src)).toBe('/static/coconuts/img/unknown.png');
        });
    });
});
