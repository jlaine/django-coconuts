import { Pipe, PipeTransform } from '@angular/core';

const GiB = 1024 * 1024 * 1024;
const MiB = 1024 * 1024;
const KiB = 1024;

@Pipe({
    name: 'fileSize',
    standalone: true
})
export class FileSizePipe implements PipeTransform {
    transform(value: number): unknown {
        if (value >= GiB) {
            return (value / GiB).toFixed(1) + ' GiB';
        } else if (value >= MiB) {
            return (value / MiB).toFixed(1) + ' MiB';
        } else if (value >= KiB) {
            return (value / KiB).toFixed(1) + ' kiB';
        } else {
            return value + ' B';
        }
    }
}
