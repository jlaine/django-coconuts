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

    describe('fileRender', function() {
        var fileRender;

        beforeEach(inject(function($filter) {
            fileRender = $filter('fileRender');
        }));

        it('should get thumbnail', function() {
            expect(fileRender({'path': '/foo/bar.jpg'}, 128)).toBe('images/render/foo/bar.jpg?size=128');
        });

        it('should get image', function() {
            expect(fileRender({'path': '/foo/bar.jpg'})).toBe('images/render/foo/bar.jpg?size=800');
        });
    });

    describe('fileSize', function() {
        var fileSize;

        beforeEach(inject(function($filter) {
            fileSize = $filter('fileSize');
        }));

        it('should format size in bytes', function() {
            expect(fileSize(0)).toBe('0 B');
            expect(fileSize(1023)).toBe('1023 B');
        });

        it('should format size in kibibytes', function() {
            expect(fileSize(1024)).toBe('1.0 kiB');
            expect(fileSize(1048575)).toBe('1024.0 kiB');
        });

        it('should format size in mebibytes', function() {
            expect(fileSize(1048576)).toBe('1.0 MiB');
            expect(fileSize(1073741823)).toBe('1024.0 MiB');
        });

        it('should format size in gibibytes', function() {
            expect(fileSize(1073741824)).toBe('1.0 GiB');
        });
    });
});
