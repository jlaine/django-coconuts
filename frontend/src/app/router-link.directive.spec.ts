import { By } from '@angular/platform-browser';
import { Component } from '@angular/core';
import { RouterLinkDirective } from './router-link.directive';
import { TestBed } from '@angular/core/testing';

import { RouterMock } from './app.component.spec';
import { RouterService } from './router.service';

@Component({
    imports: [RouterLinkDirective],
    standalone: true,
    template: `<a routerLink="/2024/">2024<a>`,
})
class RouterLinkTestComponent { }

describe('RouterLinkDirective', () => {
    let router: RouterService;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [RouterLinkTestComponent],
            providers: [
                {
                    provide: RouterService,
                    useClass: RouterMock,
                }
            ]
        }).compileComponents();

        router = TestBed.inject(RouterService);
        spyOn(router, 'go');
    });

    it('should work without path prefix', () => {
        const fixture = TestBed.createComponent(RouterLinkTestComponent);
        const link: HTMLAnchorElement = fixture.debugElement.query(By.css('a')).nativeElement;
        expect(link.pathname).toBe('/2024/');

        link.click();
        expect(router.go).toHaveBeenCalledOnceWith('/2024/');
    });

    it('should work with path prefix', () => {
        router.pathPrefix = '/someprefix';
    
        const fixture = TestBed.createComponent(RouterLinkTestComponent);
        const link: HTMLAnchorElement = fixture.debugElement.query(By.css('a')).nativeElement;
        expect(link.pathname).toBe('/someprefix/2024/');

        link.click();
        expect(router.go).toHaveBeenCalledOnceWith('/2024/');
    });

});
