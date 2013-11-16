describe('Directives', function() {
    beforeEach(module('coconuts'));

    describe('coFile', function() {
        var elem, scope;
        beforeEach(inject(function($compile, $rootScope) {
            var compiled = $compile('<input type="file" co-file="csv_file"/>');
            scope = $rootScope.$new();
            elem = compiled(scope);
        }));

        it('should select no file', function() {
            elem.trigger('change');
            expect(scope.csv_file).toBe(undefined);
        });
    });

    describe('coPhoto', function() {
        var elem, scope;
        beforeEach(inject(function($compile, $rootScope) {
            var compiled = $compile('<img co-photo="some_photo" co-size="128"/>');
            scope = $rootScope.$new();
            elem = compiled(scope);
        }));

        it('should handle undefined photo', function() {
            scope.$digest();
            expect(elem.attr('alt')).toBe(undefined);
            expect(elem.attr('src')).toBe(undefined);
        });

        it('should handle defined photo', function() {
            scope.some_photo = {name: 'bar.jpg', path: '/foo/bar.jpg'};
            scope.$digest();
            expect(elem.attr('alt')).toBe('bar.jpg');
            expect(elem.attr('src')).toBe('images/render/foo/bar.jpg?size=128');
        });
    });
});
