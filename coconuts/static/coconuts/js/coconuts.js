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
controller('CrumbCtrl', ['$location', '$rootScope', '$scope', 'settings', function($location, $rootScope, $scope, settings) {
    $scope.crumbs = [];
    $scope.settings = settings;

    $scope.show = function(crumb) {
        $rootScope.transitionClass = 'slide-backward';
        $location.path(crumb.path);
    };

    $scope.location = $location;
    $scope.$watch('location.path()', function(path) {
        if (path === '') path = '/';

        // build crumbs
        var crumbs = [];
        var crumbPath = '/';
        var bits = path.split('/');
        crumbs.push({name: 'Home', path: crumbPath});
        for (var i = 1; i < bits.length - 1; i++) {
            crumbPath += bits[i] + '/';
            crumbs.push({name: bits[i], path: crumbPath});
        }
        if (bits[bits.length-1]) {
            crumbPath += bits[bits.length-1];
            crumbs.push({name: bits[bits.length-1], path: crumbPath});
        }

        // replace crumbs
        for (i = 0; i < crumbs.length; i++) {
            if (i >= $scope.crumbs.length || $scope.crumbs[i].path != crumbs[i].path) {
                $scope.crumbs[i] = crumbs[i];
            }
        }
        $scope.crumbs.splice(crumbs.length, $scope.crumbs.length - crumbs.length);
    });

    $scope.toggleFullScreen = function() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    };
}]).
controller('FolderCtrl', ['$http', '$location', '$rootScope', '$routeParams', '$scope', '$timeout', 'Folder', 'settings', function($http, $location, $rootScope, $routeParams, $scope, $timeout, Folder, settings) {
    $scope.settings = settings;

    // fetch folder contents
    var idx = $routeParams.path.lastIndexOf('/');
    var dirPath = $routeParams.path.slice(0, idx + 1);
    $scope.currentFolder = Folder.get(dirPath);
    $scope.$watch('currentFolder', function() {
        var photos = $scope.currentFolder.files.filter(function(x) {
            return x.image !== undefined || x.video !== undefined;
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
        if (photo && !$rootScope.transitionClass) {
            $rootScope.transitionClass = 'slide-forward';
            $location.path(photo.path);
        }
    };

    $scope.showNext = function() {
        if ($scope.nextPhoto && !$rootScope.transitionClass) {
            $rootScope.transitionClass = 'slide-forward';
            $location.path($scope.nextPhoto.path);
            $location.replace();
        }
    };

    $scope.showPrevious = function() {
        if ($scope.previousPhoto && !$rootScope.transitionClass) {
            $rootScope.transitionClass = 'slide-backward';
            $location.path($scope.previousPhoto.path);
            $location.replace();
        }
    };

    // keyboard navigation
    function handleKeypress(evt) {
        switch (evt.keyCode) {
        case 32:
        case 39:
            $scope.$apply(function() {
                $scope.showNext();
            });
            break;
        case 37:
            $scope.$apply(function() {
                $scope.showPrevious();
            });
            break;
        }
    }
    angular.element(document).bind('keydown', handleKeypress);
    $scope.$on('$destroy', function() {
        angular.element(document).unbind('keydown', handleKeypress);
    });

    // clear the transition once it is finished, so that we do not re-play
    // it if the user navigates with the browser's back or forward buttons
    $timeout(function() {
        $rootScope.transitionClass = undefined;
    }, 600);
}]).
directive('coDisplay', ['settings', function(settings) {
    return {
        restrict: 'A',
        template: '<img ng-src="{{ file | fileRender }}" ng-if="file.image">' +
                  '<video controls ng-if="file.video">' +
                  '<source ng-src="{{ file | fileDownload }}" type="video/mp4"></source>' +
                  '</video>',
        scope: {
            file: '=coDisplay'
        }
    };
}]).
directive('coThumbnail', ['$window', function($window) {
    return {
        restrict: 'A',
        template: '<img class="thumb" ng-src="{{ file | fileRender:resolution }}" ng-if="file.image !== undefined || file.video !== undefined"/>' +
                  '<img class="icon" ng-src="{{ file.mimetype | fileIcon }}" ng-if="file.image === undefined">',
        scope: {
            file: '=coThumbnail'
        },
        link: function(scope, elm, attrs) {
            if ($window.devicePixelRatio > 1) {
                scope.resolution = 256;
            } else {
                scope.resolution = 128;
            }
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
factory('settings', ['$http', '$rootScope', '$window', function($http, $rootScope, $window) {
    function getDisplayHeight() {
        var foot = document.body.classList.contains('photo-info-visible') ? 96 : 0;
        return document.documentElement.clientHeight - 32 - foot;
    }
    function getImageSize() {
        var screenSize = Math.max(
            document.documentElement.clientWidth,
            document.documentElement.clientHeight
        ) * $window.devicePixelRatio;
        var sizes = [800, 1024, 1280, 1600, 2048, 2560];
        for (var i = 0; i < sizes.length; i++) {
            if (screenSize <= sizes[i]) {
                return sizes[i];
            }
        }
        return sizes[sizes.length - 1];
    }

    var settings = {
        coconuts_root: 'images/',
        display_height: getDisplayHeight(),
        image_size: getImageSize(),
        toggleInformation: function() {
            document.body.classList.toggle('photo-info-visible');
            settings.display_height = getDisplayHeight();
            settings.image_size = getImageSize();
        }
    };
    window.addEventListener('resize', function() {
        var newHeight = getDisplayHeight();
        var newSize = getImageSize();
        if (newHeight != settings.display_height || newSize !== settings.image_size) {
            $rootScope.$apply(function() {
                settings.display_height = newHeight;
                settings.image_size = newSize;
            });
        }
    });
    return settings;
}]).
filter('fileIcon', ['settings', function(settings) {
    var mime_root = '/static/coconuts/img/';
    return function(mimetype) {
        if (mimetype.indexOf('image/') === 0) {
            return mime_root + 'image-x-generic.png';
        } else if (mimetype === 'inode/directory') {
            return mime_root + 'inode-directory.png';
        } else if (mimetype === 'application/pdf') {
            return mime_root + 'application-pdf.png';
        } else if (mimetype === 'application/zip') {
            return mime_root + 'application-zip.png';
        }   else if (mimetype.indexOf('text/') === 0) {
            return mime_root + 'text-x-generic.png';
        } else if (mimetype.indexOf('video/') === 0) {
            return mime_root + 'video-x-generic.png';
        } else {
            return mime_root + 'unknown.png';
        }
    };
}]).
filter('fileSize', [function() {
    var GiB = 1024 * 1024 * 1024,
        MiB = 1024 * 1024,
        KiB = 1024;
    return function(val) {
        if (val >= GiB) {
            return (val / GiB).toFixed(1) + ' GiB';
        } else if (val >= MiB) {
            return (val / MiB).toFixed(1) + ' MiB';
        } else if (val >= KiB) {
            return (val / KiB).toFixed(1) + ' kiB';
        } else {
            return val + ' B';
        }
    };
}]).
filter('fileDownload', ['settings', function(settings) {
    return function(file) {
        return settings.coconuts_root + 'download' + file.path;
    };
}]).
filter('fileRender', ['settings', function(settings) {
    return function(file, size) {
        if (size === undefined) {
            size = settings.image_size;
        }
        return settings.coconuts_root + 'render' + file.path + '?size=' + size;
    };
}]);
