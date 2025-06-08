import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DOCUMENT } from '@angular/core';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { AppComponent, getImageSize } from './app.component';
import { FolderContents } from './file.service';
import { ReplaySubject } from 'rxjs';
import { RouterService } from './router.service';


const HOME_CONTENTS: FolderContents = {
    files: [],
    folders: [{
        mimetype: 'inode/directory',
        name: '2024',
        path: '/2024/',
    }],
    name: ''
};

const FOLDER_CONTENTS: FolderContents = {
    files: [
        {
            "mimetype": "image/jpeg",
            "name": "IMG_5032.JPG",
            "path": "/2024/IMG_5032.JPG",
            "size": 4275032,
            "image": {
                "width": 5123,
                "height": 3415,
                "camera": "Canon EOS 5D Mark II",
                "settings": "f/9, 1/400 sec, 84 mm"
            }
        },
        {

            "mimetype": "video/mp4",
            "name": "IMG_5209.MP4",
            "path": "/2024/IMG_5209.MP4",
            "size": 16695465,
            "video": {
                "duration": 29.72,
                "height": 1080,
                "width": 1920

            }
        }
    ],
    folders: [],
    name: '2024'
};

export class RouterMock {
    path$ = new ReplaySubject();
    pathPrefix = '';

    constructor() {
        this.path$.next('/');
    }

    go(path: string) {
        this.path$.next(path);
    }
}

describe('AppComponent', () => {
    let component: AppComponent;
    let document: Document;
    let fixture: ComponentFixture<AppComponent>;
    let httpMock: HttpTestingController;
    let router: RouterService;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [AppComponent],
            providers: [
                provideHttpClient(),
                provideHttpClientTesting(),
                {
                    provide: RouterService,
                    useClass: RouterMock,
                }
            ]
        }).compileComponents();

        document = TestBed.inject(DOCUMENT);
        fixture = TestBed.createComponent(AppComponent);
        httpMock = TestBed.inject(HttpTestingController);
        router = TestBed.inject(RouterService);

        component = fixture.componentInstance;
    });

    afterEach(() => {
        httpMock.verify();
    })


    describe('start from home', () => {
        beforeEach(() => {
            fixture.detectChanges();

            httpMock.expectOne({
                method: 'GET',
                url: '/images/contents/',
            }).flush(HOME_CONTENTS)
            fixture.detectChanges();
        });

        it('should display home', () => {
            expect(component.showInformation).toBeFalse();
            expect(component.showThumbnails).toBeTrue();

            // Keypress does nothing.
            component.handleKeypress(new KeyboardEvent('keydown', { key: 'ArrowLeft' }));
            component.handleKeypress(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
        });

        it('should display folder', () => {
            // Navigate to folder.
            router.go('/2024/');
            httpMock.expectOne({
                method: 'GET',
                url: '/images/contents/2024/',
            }).flush(FOLDER_CONTENTS)
            fixture.detectChanges();

            // Open media.
            component.mediaOpen(FOLDER_CONTENTS.files[0]);
            fixture.detectChanges();
            expect(component.mediaCurrent).toBe(FOLDER_CONTENTS.files[0]);
            expect(component.mediaNext).toBe(FOLDER_CONTENTS.files[1]);
            expect(component.mediaPrevious).toBeNull();

            // Show previous -> noop.
            component.showPrevious();
            fixture.detectChanges();
            expect(component.mediaCurrent).toBe(FOLDER_CONTENTS.files[0]);
            expect(component.mediaNext).toBe(FOLDER_CONTENTS.files[1]);
            expect(component.mediaPrevious).toBeNull();

            // Show next.
            component.showNext();
            fixture.detectChanges();
            expect(component.mediaCurrent).toBe(FOLDER_CONTENTS.files[1]);
            expect(component.mediaNext).toBe(null);
            expect(component.mediaPrevious).toBe(FOLDER_CONTENTS.files[0]);

            // Show next -> noop.
            component.showNext();
            fixture.detectChanges();
            expect(component.mediaCurrent).toBe(FOLDER_CONTENTS.files[1]);
            expect(component.mediaNext).toBe(null);
            expect(component.mediaPrevious).toBe(FOLDER_CONTENTS.files[0]);

            // Toggle information.
            component.toggleInformation();
            fixture.detectChanges();
            expect(component.showInformation).toBeTrue();
            component.toggleInformation();
            fixture.detectChanges();
            expect(component.showInformation).toBeFalse();

            // Show previous.
            component.showPrevious();
            fixture.detectChanges();
            expect(component.mediaCurrent).toBe(FOLDER_CONTENTS.files[0]);
            expect(component.mediaNext).toBe(FOLDER_CONTENTS.files[1]);
            expect(component.mediaPrevious).toBeNull();

            // Close media.
            component.mediaClose();
        });

        it('should toggle fullscreen', () => {
            let fullscreenElement: HTMLElement | null = null;

            spyOnProperty(document, 'fullscreenElement', 'get').and.callFake(() => fullscreenElement);
            spyOn(document, 'exitFullscreen').and.callFake(() => {
                fullscreenElement = null;
                return Promise.resolve(void 0);
            });
            spyOn(document.documentElement, 'requestFullscreen').and.callFake(() => {
                fullscreenElement = document.documentElement;
                return Promise.resolve(void 0);
            });

            // Enter fullscreen.
            component.toggleFullscreen();
            expect(fullscreenElement).not.toBeNull();

            // Exit fullscreen.
            component.toggleFullscreen();
            expect(fullscreenElement).toBeNull();
        });
    });

    it('should return image size', () => {
        const testImageSize = (clientHeight: number, clientWidth: number, devicePixelRatio: number) => getImageSize(
            { clientHeight: clientHeight, clientWidth: clientWidth } as HTMLElement,
            { devicePixelRatio: devicePixelRatio } as Window,
        );
        expect(testImageSize(640, 480, 1)).toBe(800);
        expect(testImageSize(480, 640, 1)).toBe(800);

        expect(testImageSize(640, 480, 2)).toBe(1280);
        expect(testImageSize(480, 640, 2)).toBe(1280);

        expect(testImageSize(1600, 1200, 2)).toBe(2560);
        expect(testImageSize(1200, 1600, 2)).toBe(2560);
    });
});
