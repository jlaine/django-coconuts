import { TestBed } from '@angular/core/testing';

import { RouterService, stripBasePath, stripTrailingSlash } from './router.service';

describe('RouterService', () => {
    let service: RouterService;

    beforeEach(() => {
        TestBed.configureTestingModule({});
        service = TestBed.inject(RouterService);
    });

    it('should navigate', () => {
        const paths: string[] = [];
        const spy = spyOn(window.history, 'pushState');
        const sub = service.path$.subscribe((path) => {
            paths.push(path);
        });

        service.pathPrefix = '/app/';
        expect(paths).toEqual(['']);

        service.go('some/path/');
        expect(spy).toHaveBeenCalledWith(null, '', '/app/some/path/');
        expect(paths).toEqual(['', 'some/path/']);

        sub.unsubscribe();
    });

    it('should strip base path', () => {
        expect(stripBasePath('/', '/some/path')).toBe('some/path');

        expect(stripBasePath('/app/', '/app/some/path')).toBe('some/path');
        expect(stripBasePath('/app/', '/some/path')).toBe('/some/path');
    });

    it('should strip trailing slash', () => {
        expect(stripTrailingSlash('foo/bar')).toBe('foo/bar');
        expect(stripTrailingSlash('foo/bar/')).toBe('foo/bar');
    });
});
