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

    describe('CrumbCtrl', function() {
        var scope, ctrl, $location;

        beforeEach(inject(function($controller, $injector, $rootScope) {
            $location = $injector.get('$location');
            scope = $rootScope.$new();
            ctrl = $controller('CrumbCtrl', {
                $scope: scope
            });
        }));

        it('should return crumbs for /', function() {
            scope.$digest();
            expect(scope.crumbs).toEqual([]);
        });

        it('should return crumbs for /foo.jpg', function() {
            $location.path = function() { return '/foo.jpg'; };
            scope.$digest();
            expect(scope.crumbs).toEqual([
                { name : 'foo.jpg', path : '/foo.jpg' }
            ]);
        });

        it('should return crumbs for /foo/', function() {
            $location.path = function() { return '/foo/'; };
            scope.$digest();
            expect(scope.crumbs).toEqual([
                { name : 'foo', path : '/foo/' }
            ]);
        });

        it('should return crumbs for /foo/bar.jpg', function() {
            $location.path = function() { return '/foo/bar.jpg'; };
            scope.$digest();
            expect(scope.crumbs).toEqual([
                { name : 'foo', path : '/foo/' },
                { name : 'bar.jpg', path : '/foo/bar.jpg' }
            ]);
        });

        it('should return crumbs for /foo/bar/baz.jpg', function() {
            $location.path = function() { return '/foo/bar/baz.jpg'; };
            scope.$digest();
            expect(scope.crumbs).toEqual([
                { name : 'foo', path : '/foo/' },
                { name : 'bar', path : '/foo/bar/' },
                { name : 'baz.jpg', path : '/foo/bar/baz.jpg' }
            ]);
        });
    });

    describe('FolderCtrl', function() {
        var scope, ctrl;

        beforeEach(inject(function($controller, $rootScope) {
            scope = $rootScope.$new();
            ctrl = $controller('FolderCtrl', {
                $scope: scope
            });

            $httpBackend.expect('GET', 'images/contents/').respond({
                can_manage: true,
                can_write: true,
                files: [],
                name: '',
                folders: [],
                photos: [],
                path: '/'
            });
            $httpBackend.flush();
        }));

        it('should get contents', function() {
            expect(scope.currentFolder).toEqual({
                can_manage: true,
                can_write: true,
                files: [],
                folders: [],
                name: '',
                photos: [],
                path: '/'
            }); 
        });

        it('should add file', function() {
            $httpBackend.expect('POST', 'images/add_file/', function(data) {
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
                path: '/'
            });
 
            scope.addPrompt = true;
            scope.addFile = {name: "folder.png"};
            scope.doAdd();
            $httpBackend.flush();
            expect(scope.addPrompt).toBe(false);
        });

        it('should create folder', function() {
            $httpBackend.expect('POST', 'images/add_folder/', function(data) {
                return angular.equals(data, {
                    name: 'New folder'
                }, true);
            }).respond({
                can_manage: true,
                can_write: true,
                files: [],
                folders: [
                    {
                        filesize: 4096,
                        name: 'New folder',
                        path: 'New folder',
                        url: '/New%20folder/',
                    }
                ],
                name: '',
                photos: [],
                path: '/'
            });
 
            scope.createPrompt = true;
            scope.createName = "New folder";
            scope.doCreate();
            $httpBackend.flush();
            expect(scope.createPrompt).toBe(false);
        });

        it('should delete file', function() {
            $httpBackend.expect('POST', 'images/delete/Foo/').respond({
                can_manage: true,
                can_write: true,
                files: [],
                folders: [],
                name: '',
                photos: [],
                path: '/'
            });

            scope.promptDelete({path: '/Foo/'});
            scope.doDelete();
            $httpBackend.flush();
            expect(scope.deleteTarget).toBe(undefined);
        });
    });
});
