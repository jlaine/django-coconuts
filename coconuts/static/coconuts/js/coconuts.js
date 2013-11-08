var app = angular.module('coconuts', ['ngAnimate', 'ngResource', 'ngRoute', 'ngTouch']).
config(['$httpProvider', '$routeProvider', function($httpProvider, $routeProvider) {
    // handle django's CSRF
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]).
controller('FolderCtrl', ['$http', '$location', '$scope', 'FormData', 'settings', function($http, $location, $scope, FormData, settings) {
    $scope.settings = settings;
    $scope.contents = {photos: []};

    function updateList() {
        $http.get(settings.coconuts_root + 'contents' + window.location.pathname).success(function(contents) {
            $scope.contents = contents;
            updatePhoto();
        });
    }

    function updatePhoto() {
        var path = $location.path();
        var photo, i;
        for (i = 0; i < $scope.contents.photos.length; i++) {
            photo = $scope.contents.photos[i];
            if ('/' + photo.path == path) {
                $scope.previousPhoto = $scope.contents.photos[i-1];
                $scope.currentPhoto = photo;
                $scope.nextPhoto = $scope.contents.photos[i+1];
                return;
            }
            $scope.previousPhoto = undefined;
            $scope.currentPhoto = undefined;
            $scope.nextPhoto = undefined;
        }
    }

    $scope.doAdd = function() {
        var formData = new FormData();
        formData.append('upload', $scope.addFile);
        $http.post(settings.coconuts_root + 'add_file' + window.location.pathname, formData, {
            headers: { 'Content-Type': undefined },
            transformRequest: function(data) { return data; }
        }).success(function(contents) {
            $scope.addPrompt = false;
            $scope.contents = contents;
            updatePhoto();
        });
    };

    $scope.doCreate = function() {
        var formData = new FormData();
        formData.append('name', $scope.createName);
        $http.post(settings.coconuts_root + 'add_folder' + window.location.pathname, formData, {
            headers: { 'Content-Type': undefined },
            transformRequest: function(data) { return data; }
        }).success(function(contents) {
            $scope.createPrompt = false;
            $scope.contents = contents;
            updatePhoto();
        });
    };

    $scope.promptDelete = function(obj) {
        $scope.deleteTarget = obj;
        $scope.deleteFolder = false;
    };
    $scope.doDelete = function() {
        $http.post(settings.coconuts_root + 'delete/' + $scope.deleteTarget.path).success(function(contents) {
            $scope.deleteTarget = undefined;
            $scope.contents = contents;
            $location.path('');
        });
    };

    $scope.location = $location;
    $scope.$watch('location.path()', function(path) {
        if (path == '') path = '/';
        $http.get(settings.coconuts_root + 'contents' + path).success(function(contents) {
            $scope.contents = contents;
            updatePhoto();
        });
    });
    updateList();
}]).
directive('coFile', ['$parse', function($parse) {
    return {
        restrict: 'A',
        link: function(scope, elm, attrs) {
            var model = $parse(attrs.coFile);
            elm.bind('change', function(evt) {
                scope.$apply(function() {
                    model.assign(scope, evt.target.files[0]);
                });
            });
        }
    };
}]).
factory('FormData', [function() {
    return FormData;
}]).
factory('settings', ['$http', function($http) {
    return {
        coconuts_root: '/images/',
        static_root: '/static/coconuts/'
    };
}]).
filter('fileIcon', ['settings', function(settings) {
    var mime_root = settings.static_root + 'img/mimetypes/';
    return function(name) {
        var idx = name.lastIndexOf('.');
        if (idx !== -1) {
            var extension = name.slice(idx + 1, name.length).toLowerCase();
            if (extension == 'gif' || extension == 'jpg' || extension == 'jpeg' || extension == 'png') {
                return mime_root + 'image-jpeg.png';
            } else if (extension == 'py') {
                return mime_root + 'text-x-python.png';
            }
        }
        return mime_root + 'unknown.png';
    };
}]).
filter('fileSize', [function() {
    var MB = 1024 * 1024;
    var KB = 1024;
    return function(val) {
        if (val > MB) {
            return (val / MB).toFixed(1) + ' MB';
        } else if (val > KB) {
            return (val / KB).toFixed(1) + ' kB';
        } else {
            return val + ' B';
        }
    };
}]).
filter('urlencode', [function() {
    return function(val) {
        return val;
    };
}]);
