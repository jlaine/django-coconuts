import { CommonModule } from '@angular/common';
import { Component, DOCUMENT, HostListener, Inject, OnInit } from '@angular/core';
import { map, Observable, switchMap, tap } from 'rxjs';

import { FileService, FolderContents, FolderFile } from './file.service';
import { FileIconPipe } from './file-icon.pipe';
import { FileSizePipe } from './file-size.pipe';
import { RouterLinkDirective } from './router-link.directive';
import { RouterService } from './router.service';

interface Crumb {
    name: string;
    path: string;
}

export const getImageSize = (documentElement: HTMLElement, window: Window) => {
    const sizes = [800, 1024, 1280, 1600, 2048, 2560];
    const screenSize = Math.max(
        documentElement.clientWidth,
        documentElement.clientHeight
    ) * window.devicePixelRatio;
    for (var i = 0; i < sizes.length; i++) {
        if (screenSize <= sizes[i]) {
            return sizes[i];
        }
    }
    return sizes[sizes.length - 1];
}

@Component({
    selector: 'app-root',
    imports: [
        CommonModule,
        FileSizePipe,
        FileIconPipe,
        RouterLinkDirective,
    ],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
    crumbs$: Observable<Crumb[]>;
    currentFolder: FolderContents | null = null;
    showInformation = false;
    showThumbnails = false;

    mediaCurrent: FolderFile | null = null;
    mediaNext: FolderFile | null = null;
    mediaPrevious: FolderFile | null = null;

    private currentFolder$: Observable<FolderContents>;
    private mediaFiles: FolderFile[] = [];
    private mediaSize = 800;

    @HostListener('document:keydown', ['$event'])
    handleKeypress(event: KeyboardEvent) {
        switch (event.key) {
            case 'ArrowLeft':
                this.showPrevious();
                break;
            case 'ArrowRight':
                this.showNext();
                break;
        }
    }

    @HostListener('window:resize')
    handleResize() {
        this.mediaSize = getImageSize(document.documentElement, window);
    }

    constructor(
        @Inject(DOCUMENT) private document: Document,
        private fileService: FileService,
        router: RouterService,
    ) {
        this.crumbs$ = router.path$.pipe(
            map((path) => {
                let crumbPath = '';
                return path.split('/').slice(0, -1).map((bit) => {
                    crumbPath += bit + '/';
                    return { name: crumbPath === '/' ? 'Home' : bit, path: crumbPath };
                });
            })
        );

        this.currentFolder$ = router.path$.pipe(
            switchMap((path) => this.fileService.folderContents(path))
        );
    }

    fileDownload(file: FolderFile) {
        return this.fileService.fileDownload(file);
    }

    fileRender(file: FolderFile) {
        return this.fileService.fileRender(file, this.mediaSize);
    }

    fileThumbnail(file: FolderFile) {
        return this.fileService.fileRender(file, 256);
    }

    ngOnInit() {
        this.handleResize();

        this.currentFolder$.subscribe((contents) => {
            this.mediaFiles = contents.files.filter((x) => x.image !== undefined || x.video !== undefined);
            this.currentFolder = contents;
            this.mediaCurrent = null;
            this.mediaNext = null;
            this.mediaPrevious = null;

            // Show thumbnails if the current directory contains only media.
            this.showThumbnails = this.mediaFiles.length === contents.files.length;
        });
    }

    mediaClose() {
        this.mediaCurrent = null;
        this.mediaNext = null;
        this.mediaPrevious = null;
    }

    mediaOpen(file: FolderFile) {
        const idx = this.mediaFiles.indexOf(file);
        this.mediaCurrent = file;
        this.mediaPrevious = this.mediaFiles[idx - 1] || null;
        this.mediaNext = this.mediaFiles[idx + 1] || null;
    }

    showNext() {
        if (this.mediaNext) {
            this.mediaOpen(this.mediaNext);
        }
    }

    showPrevious() {
        if (this.mediaPrevious) {
            this.mediaOpen(this.mediaPrevious);
        }
    }

    toggleInformation() {
        this.showInformation = !this.showInformation;
    }

    toggleFullscreen() {
        if (!this.document.fullscreenElement) {
            this.document.documentElement.requestFullscreen();
        } else {
            this.document.exitFullscreen();
        }
    }
}
