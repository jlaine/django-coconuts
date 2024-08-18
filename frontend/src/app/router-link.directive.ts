import { Directive, ElementRef, HostListener, Input, Renderer2 } from '@angular/core';

import { RouterService } from './router.service';

@Directive({
    selector: '[routerLink]',
    standalone: true,
})
export class RouterLinkDirective {
    private path = '';

    constructor(
        private element: ElementRef,
        private renderer: Renderer2,
        private router: RouterService,
    ) { }

    @Input()
    set routerLink(path: string) {
        this.path = path;
        this.renderer.setAttribute(this.element.nativeElement, 'href', this.router.pathPrefix + path);
    }

    @HostListener(
        'click',
        ['$event.button', '$event.ctrlKey', '$event.shiftKey', '$event.altKey', '$event.metaKey'])
    onClick(button: number, ctrlKey: boolean, shiftKey: boolean, altKey: boolean, metaKey: boolean): boolean {
        this.router.go(this.path);
        return false;
    }
}
