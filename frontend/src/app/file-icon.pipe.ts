import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'fileIcon',
    standalone: true
})
export class FileIconPipe implements PipeTransform {
    transform(mimetype: string): unknown {
        if (mimetype === 'inode/directory') {
            return 'folder';
        } else if (mimetype.indexOf('image/') === 0) {
            return 'image';
        } else if (mimetype.indexOf('text/') === 0) {
            return 'description';
        } else if (mimetype.indexOf('video/') === 0) {
            return 'video';
        } else {
            return 'draft';
        }
    }
}
