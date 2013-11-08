'use strict';

describe('Controllers', function() {
    var $httpBackend;

    beforeEach(module('coconuts'));
    beforeEach(module(function($provide) {
        var FakeData = function() {
        };
        FakeData.prototype.append = function(k, v) {
            this[k] = v;
        };

        $provide.value('FormData', FakeData);
    }));
    beforeEach(inject(function($injector) {
        $httpBackend = $injector.get('$httpBackend');
    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    describe('FolderCtrl', function() {
        var scope, ctrl;

        beforeEach(inject(function($controller, $rootScope) {
            scope = $rootScope.$new();
            ctrl = $controller('FolderCtrl', {
                $scope: scope
            });

            $httpBackend.expect('GET', '/images/contents/context.html').respond({
                can_manage: true,
                can_write: true,
                files: [],
                name: '',
                folders: [],
                photos: [],
                path: '',
                url: '/'
            });
            $httpBackend.flush();
        }));

        it('should get contents', function() {
            expect(scope.contents).toEqual({
                can_manage: true,
                can_write: true,
                files: [],
                folders: [],
                name: '',
                photos: [],
                path: '',
                url: '/'
            }); 
        });

        it('should add file', function() {
            $httpBackend.expect('POST', '/images/add_file/context.html', function(data) {
                return angular.equals(data, {
                    upload: {name: 'folder.png'}
                }, true);
            }).respond({
                can_manage: true,
                can_write: true,
                files: [
                    {
                        filesize: 548,
                        name: 'folder.png',
                        path: 'folder.png'
                    }
                ],
                folders: [],
                name: '',
                photos: [],
                path: '',
                url: '/'
            });
 
            scope.addPrompt = true;
            scope.addFile = {name: "folder.png"};
            scope.doAdd();
            $httpBackend.flush();
            expect(scope.addPrompt).toBe(false);
        });

        it('should create folder', function() {
            $httpBackend.expect('POST', '/images/add_folder/context.html', function(data) {
                return angular.equals(data, {
                    name: 'New folder'
                }, true);
            }).respond({
                files: [],
                folders: [
                    {
                        filesize: 4096,
                        name: 'New folder',
                        path: 'New folder',
                        url: '/New%20folder/',
                    }
                ],
                photos: []
            });
 
            scope.createPrompt = true;
            scope.createName = "New folder";
            scope.doCreate();
            $httpBackend.flush();
            expect(scope.createPrompt).toBe(false);
        });
    });
});
