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
    $scope.crumbs = [];

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
        if (!document.fullscreenElement &&    // alternative standard method
            !document.mozFullScreenElement && !document.webkitFullscreenElement) {  // current working methods
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            } else if (document.documentElement.mozRequestFullScreen) {
                document.documentElement.mozRequestFullScreen();
            } else if (document.documentElement.webkitRequestFullscreen) {
                document.documentElement.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
            }
        } else {
            if (document.cancelFullScreen) {
                document.cancelFullScreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitCancelFullScreen) {
                document.webkitCancelFullScreen();
            }
        }
    };
}]).
controller('FolderCtrl', ['$http', '$location', '$rootScope', '$routeParams', '$scope', '$timeout', 'Folder', 'FormData', 'settings', function($http, $location, $rootScope, $routeParams, $scope, $timeout, Folder, FormData, settings) {
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

    $scope.promptManage = function() {
        $scope.managePrompt = true;
        $http.get(settings.coconuts_root + 'permissions' + $scope.currentFolder.path).success(function(data) {
            $scope.description = data.description;
            $scope.permissions = data.permissions;
            $scope.owners = data.owners;
        });
    };
    $scope.doManage = function() {
        $http.post(settings.coconuts_root + 'permissions' + $scope.currentFolder.path, {
            description: $scope.description,
            permissions: $scope.permissions
        }).success(function(data) {
            $scope.managePrompt = false;
        });
    };

    // keyboard navigation
    function handleKeypress(evt) {
        switch (evt.keyCode) {
        case 0:
        case 39:
            $scope.$apply(function() {
                $scope.showNext();
            });
            break;
        case 8:
        case 37:
            $scope.$apply(function() {
                $scope.showPrevious();
            });
            break;
        }
    }
    angular.element(document).bind('keypress', handleKeypress);
    $scope.$on('$destroy', function() {
        angular.element(document).unbind('keypress', handleKeypress);
    });

    // clear the transition once it is finished, so that we do not re-play
    // it if the user navigates with the browser's back or forward buttons
    $timeout(function() {
        $rootScope.transitionClass = undefined;
    }, 600);
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
            photo: '=coPhoto',
            size: '=coSize'
        },
        link: function(scope, elm, attrs) {
            scope.$watch('[photo, size]', function() {
                if (scope.photo !== undefined) {
                    elm.attr('alt', scope.photo.name);
                    elm.attr('src', settings.coconuts_root + 'render' + scope.photo.path + '?size=' + scope.size);
                } else {
                    elm.attr('alt', undefined);
                    elm.attr('src', undefined);
                }
            }, true);
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
factory('settings', ['$http', '$rootScope', function($http, $rootScope) {
    function getDisplayHeight() {
        return $(window).height() - 32;
    }
    function getImageSize() {
        var screenSize = Math.max($(window).width(), $(window).height());
        var sizes = [800, 1024, 1280, 1600];
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
        image_size: getImageSize()
    };
    $(window).resize(function() {
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
        } else if (mimetype.indexOf('text/') === 0) {
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
}]);
