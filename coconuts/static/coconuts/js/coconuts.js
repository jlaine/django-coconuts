var app = angular.module('coconuts', ['ngAnimate', 'ngResource', 'ngRoute', 'ngTouch']).
config(['$httpProvider', '$routeProvider', function($httpProvider, $routeProvider) {
    // handle django's CSRF
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    $routeProvider.
        when(':path*', {
            templateUrl: '/folder.html',
            controller: 'FolderCtrl'
        }).
        otherwise({redirectTo: '/'});
}]).
controller('CrumbCtrl', ['$location', '$rootScope', '$scope', function($location, $rootScope, $scope) {
    $scope.show = function(crumb) {
        $rootScope.transitionClass = 'slide-backward';
        $location.path(crumb.path);
    };

    $scope.location = $location;
    $scope.$watch('location.path()', function(path) {
        if (path === '') path = '/';
        var crumbs = [];
        var crumbPath = '/';
        var bits = path.split('/');
        for (var i = 1; i < bits.length - 1; i++) {
            crumbPath += bits[i] + '/';
            crumbs.push({name: bits[i], path: crumbPath});
        }
        if (bits[bits.length-1]) {
            crumbPath += bits[bits.length-1];
            crumbs.push({name: bits[bits.length-1], path: crumbPath});
        }
        $scope.crumbs = crumbs;
    });
}]).
controller('FolderCtrl', ['$http', '$location', '$rootScope', '$routeParams', '$scope', 'Folder', 'FormData', 'settings', function($http, $location, $rootScope, $routeParams, $scope, Folder, FormData, settings) {
    $scope.settings = settings;

    // fetch folder contents
    var idx = $routeParams.path.lastIndexOf('/');
    var dirPath = $routeParams.path.slice(0, idx + 1);
    $scope.currentFolder = Folder.get(dirPath);
    $scope.$watch('currentFolder', function() {
        var photos = $scope.currentFolder.files.filter(function(x) {
            return x.image !== undefined;
        });
        $scope.showThumbnails = (photos.length == $scope.currentFolder.files.length);
        for (var i = 0; i < photos.length; i++) {
            if (photos[i].path === $routeParams.path) {
                $scope.previousPhoto = photos[i-1];
                $scope.currentPhoto = photos[i];
                $scope.nextPhoto = photos[i+1];
                return;
            }
        }
        $scope.previousPhoto = undefined;
        $scope.currentPhoto = undefined;
        $scope.nextPhoto = undefined;
    }, true);

    $scope.show = function(photo) {
        $rootScope.transitionClass = 'slide-forward';
        $location.path(photo.path);
    };

    $scope.showNext = function() {
        if ($scope.nextPhoto) {
            $rootScope.transitionClass = 'slide-forward';
            $location.path($scope.nextPhoto.path);
            $location.replace();
        }
    };

    $scope.showPrevious = function() {
        if ($scope.previousPhoto) {
            $rootScope.transitionClass = 'slide-backward';
            $location.path($scope.previousPhoto.path);
            $location.replace();
        }
    };

    $scope.doAdd = function() {
        var formData = new FormData();
        formData.append('upload', $scope.addFile);
        $http.post(settings.coconuts_root + 'add_file' + $scope.currentFolder.path, formData, {
            headers: { 'Content-Type': undefined },
            transformRequest: function(data) { return data; }
        }).success(function(currentFolder) {
            $scope.addPrompt = false;
            angular.copy(currentFolder, $scope.currentFolder);
        });
    };

    $scope.doCreate = function() {
        var formData = new FormData();
        formData.append('name', $scope.createName);
        $http.post(settings.coconuts_root + 'add_folder' + $scope.currentFolder.path, formData, {
            headers: { 'Content-Type': undefined },
            transformRequest: function(data) { return data; }
        }).success(function(currentFolder) {
            $scope.createPrompt = false;
            angular.copy(currentFolder, $scope.currentFolder);
        });
    };

    $scope.promptDelete = function(obj) {
        $scope.deleteTarget = obj;
        $scope.deleteFolder = false;
    };
    $scope.doDelete = function() {
        $http.post(settings.coconuts_root + 'delete' + $scope.deleteTarget.path).success(function(currentFolder) {
            $scope.deleteTarget = undefined;
            angular.copy(currentFolder, $scope.currentFolder);
            $location.path(currentFolder.path);
        });
    };
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
directive('coPhoto', ['settings', function(settings) {
    return {
        restrict: 'A',
        scope: {
            photo: '=coPhoto'
        },
        link: function(scope, elm, attrs) {
            scope.$watch('photo', function(photo) {
                if (photo !== undefined) {
                    elm.attr('alt', photo.name);
                    elm.attr('src', settings.coconuts_root + 'render' + photo.path + '?size=' + attrs.coSize);
                } else {
                    elm.attr('alt', '');
                    elm.attr('src', '');
                }
            });
        }
    };
}]).
factory('Folder', ['$cacheFactory', '$http', 'settings', function($cacheFactory, $http, settings) {
    var cache = $cacheFactory('Folder');
    var Folder = function() {
        this.files = [];
        this.folders = [];
    };
    Folder.get = function(dirPath) {
        var folder = cache.get(dirPath);
        if (folder === undefined) {
            folder = new Folder();
            $http.get(settings.coconuts_root + 'contents' + dirPath).success(function(data) {
                angular.copy(data, folder);
                cache.put(dirPath, folder);
            });
        }
        return folder;
    };
    return Folder;
}]).
factory('FormData', [function() {
    return FormData;
}]).
factory('settings', ['$http', function($http) {
    return {
        coconuts_root: 'images/',
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
