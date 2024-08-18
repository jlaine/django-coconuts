import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { RouterService } from './router.service';


export interface FolderFile {
    mimetype: string;
    name: string;
    path: string;
    size: number;

    image?: {
        camera: string;
        height: number;
        settings: string;
        width: number;
    }

    video?: {
        duration: number;
        height: number;
        width: number;
    }
}

export interface FolderContents {
    files: FolderFile[];
    folders: {
        mimetype: string;
        name: string;
        path: string;
    }[];
    name: string;
    path: string;
}

@Injectable({
    providedIn: 'root',
})
export class FileService {
    private apiRoot: string;

    constructor(
        private http: HttpClient,
        router: RouterService,
    ) {
        this.apiRoot = router.pathPrefix + '/images'
    }

    fileDownload(file: FolderFile) {
        return this.apiRoot + '/download' + file.path;
    }

    fileRender(file: FolderFile, size: number) {
        return this.apiRoot + '/render' + file.path + '?size=' + size;
    }

    folderContents(path: string) {
        return this.http.get<FolderContents>(this.apiRoot + '/contents/' + path);
    }
}
