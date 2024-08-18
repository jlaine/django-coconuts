import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';

const stripBasePath = (basePath: string, url: string): string => {
    if (url.startsWith(basePath)) {
        return url.substring(basePath.length);
    } else {
        return url;
    }
}

const stripTrailingSlash = (url: string): string => {
    if (url.endsWith('/')) {
        return url.substring(0, url.length - 1);
    } else {
        return url;
    }
}

@Injectable({
    providedIn: 'root'
})
export class RouterService {
    path$: Observable<string>;
    pathPrefix: string;

    private pathSubject$ = new ReplaySubject<string>();

    constructor() {
        this.pathPrefix = stripTrailingSlash(document.baseURI.split(/\/\/[^\/]+/)[1]);
        this.pathSubject$.next(stripBasePath(this.pathPrefix, location.pathname));
        this.path$ = this.pathSubject$.asObservable();
    }

    go(path: string) {
        history.pushState(null, '', this.pathPrefix + path);
        this.pathSubject$.next(path);
    }
}
