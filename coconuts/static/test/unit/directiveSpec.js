describe('Directives', function() {
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
});
