'use strict';

describe('Providers', function() {
    beforeEach(module('coconuts'));

    describe('Folder', function() {
        var Folder, $httpBackend;

        beforeEach(inject(['$injector', function($injector) {
            Folder = $injector.get('Folder');
            $httpBackend = $injector.get('$httpBackend');
        }]));

        afterEach(function() {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });

        it('should get folder', function() {
            // cache miss
            $httpBackend.expect('GET', 'images/contents/').respond({
                files: [],
                folders: [],
                name: '',
                path: '/'
            });
            var folder = Folder.get('/');
            expect(folder.name).toBe(undefined);
            expect(folder.path).toBe(undefined);
            $httpBackend.flush();
            expect(folder.name).toBe('');
            expect(folder.path).toBe('/');

            // cache hit
            var folder2 = Folder.get('/');
            expect(folder2.name).toBe('');
            expect(folder2.path).toBe('/');
        });
    });
});
