var app = angular.module('coconuts', ['ngAnimate', 'ngResource', 'ngRoute', 'ngTouch']).
config(['$httpProvider', '$routeProvider', function($httpProvider, $routeProvider) {
    // handle django's CSRF
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]).
controller('FolderCtrl', ['$http', '$scope', function($http, $scope) {
    var url = window.location.pathname;
    $scope.current = {
        url: window.location.pathname
    };
    $http.get('/images/contents' + url).success(function(contents) {
        $scope.contents = contents;
    });
}]).
filter('fileIcon', [function() {
    var mimeroot = '/static/coconuts/img/mimetypes/';
    return function(name) {
        var idx = name.lastIndexOf('.');
        if (idx !== -1) {
            var extension = name.slice(idx + 1, name.length).toLowerCase();
            if (extension == 'gif' || extension == 'jpg' || extension == 'jpeg' || extension == 'png') {
                return mimeroot + 'image-jpeg.png';
            } else if (extension == 'py') {
                return mimeroot + 'text-x-python.png';
            }
        }
        return mimeroot + 'unknown.png';
    }
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
