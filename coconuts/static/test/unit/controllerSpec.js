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
                files: [],
                folders: [],
                photos: []
            });
            $httpBackend.flush();
        }));

        it('should get contents', function() {
            expect(scope.contents).toEqual({
                files: [],
                folders: [],
                photos: []
            }); 
        });

        it('should add file', function() {
            $httpBackend.expect('POST', '/images/add_file/context.html', function(data) {
                return angular.equals(data, {
                    upload: {name: 'New file.jpg'}
                }, true);
            }).respond({
            });
 
            scope.addPrompt = true;
            scope.addFile = {name: "New file.jpg"};
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
            });
 
            scope.createPrompt = true;
            scope.createName = "New folder";
            scope.doCreate();
            $httpBackend.flush();
            expect(scope.createPrompt).toBe(false);
        });
    });
});
