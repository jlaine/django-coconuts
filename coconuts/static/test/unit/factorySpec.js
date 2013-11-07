'use strict';

describe('Providers', function() {
    beforeEach(module('coconuts'));

    describe('FormData', function() {
        var myFormData;
        beforeEach(inject(['$injector', function($injector) {
            myFormData = $injector.get('FormData');
        }]));

        it('should return native FormData', function() {
            expect(myFormData).toBe(FormData);
        });
    });
});
