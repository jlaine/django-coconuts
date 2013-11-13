'use strict';

describe('Filters', function() {
    beforeEach(module('coconuts'));

    describe('fileIcon', function() {
        var fileIcon;

        beforeEach(inject(function($filter) {
            fileIcon = $filter('fileIcon');
        }));

        it('should return folder icon', function() {
            expect(fileIcon('inode/directory')).toBe('/static/coconuts/img/folder.png');
        });

        it('should return image icon', function() {
            expect(fileIcon('image/gif')).toBe('/static/coconuts/img/image.png');
            expect(fileIcon('image/jpeg')).toBe('/static/coconuts/img/image.png');
            expect(fileIcon('image/pjpeg')).toBe('/static/coconuts/img/image.png');
            expect(fileIcon('image/png')).toBe('/static/coconuts/img/image.png');
        });

        it('should return unknown icon', function() {
            expect(fileIcon('application/octet-stream')).toBe('/static/coconuts/img/unknown.png');
        });
    });
});
