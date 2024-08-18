import { FileSizePipe } from './file-size.pipe';

describe('FileSizePipe', () => {
    let pipe: FileSizePipe;

    beforeEach(() => {
        pipe = new FileSizePipe();
    });

    it('should format size in bytes', () => {
        expect(pipe.transform(0)).toBe('0 B');
        expect(pipe.transform(1023)).toBe('1023 B');
    });

    it('should format size in kibibytes', () => {
        expect(pipe.transform(1024)).toBe('1.0 kiB');
        expect(pipe.transform(1048575)).toBe('1024.0 kiB');
    });

    it('should format size in mebibytes', () => {
        expect(pipe.transform(1048576)).toBe('1.0 MiB');
        expect(pipe.transform(1073741823)).toBe('1024.0 MiB');
    });

    it('should format size in gibibytes', () => {
        expect(pipe.transform(1073741824)).toBe('1.0 GiB');
    });
});
