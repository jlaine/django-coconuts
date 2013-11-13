'use strict';

describe('Filters', function() {
    beforeEach(module('coconuts'));

    describe('fileIcon', function() {
        var fileIcon;

        beforeEach(inject(function($filter) {
            fileIcon = $filter('fileIcon');
        }));

        it('should return directory icon', function() {
            expect(fileIcon('inode/directory')).toBe('/static/coconuts/img/inode-directory.png');
        });

        it('should return image icon', function() {
            expect(fileIcon('image/gif')).toBe('/static/coconuts/img/image-x-generic.png');
            expect(fileIcon('image/jpeg')).toBe('/static/coconuts/img/image-x-generic.png');
            expect(fileIcon('image/pjpeg')).toBe('/static/coconuts/img/image-x-generic.png');
            expect(fileIcon('image/png')).toBe('/static/coconuts/img/image-x-generic.png');
        });

        it('should return pdf icon', function() {
            expect(fileIcon('application/pdf')).toBe('/static/coconuts/img/application-pdf.png');
        });

        it('should return text icon', function() {
            expect(fileIcon('text/plain')).toBe('/static/coconuts/img/text-x-generic.png');
            expect(fileIcon('text/html')).toBe('/static/coconuts/img/text-x-generic.png');
        });

        it('should return unknown icon', function() {
            expect(fileIcon('application/octet-stream')).toBe('/static/coconuts/img/unknown.png');
        });

        it('should return zip icon', function() {
            expect(fileIcon('application/zip')).toBe('/static/coconuts/img/application-zip.png');
        });
    });
});
