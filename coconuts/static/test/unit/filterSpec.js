'use strict';

describe('Filters', function() {
    beforeEach(module('coconuts'));

    describe('fileIcon', function() {
        var fileIcon;

        beforeEach(inject(function($filter) {
            fileIcon = $filter('fileIcon');
        }));

        it('should return image icon', function() {
            expect(fileIcon('some_file.gif')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');
            expect(fileIcon('some_file.jpg')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');
            expect(fileIcon('some_file.jpeg')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');
            expect(fileIcon('some_file.png')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');

            expect(fileIcon('some_file.GIF')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');
            expect(fileIcon('some_file.JPG')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');
            expect(fileIcon('some_file.JPEG')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');
            expect(fileIcon('some_file.PNG')).toBe('/static/coconuts/img/mimetypes/image-jpeg.png');
        });

        it('should return unknown icon', function() {
            expect(fileIcon('some_file.xyz')).toBe('/static/coconuts/img/mimetypes/unknown.png');
        });
    });
});
