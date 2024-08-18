import { FileIconPipe } from './file-icon.pipe';

describe('FileIconPipe', () => {
    let pipe: FileIconPipe;

    beforeEach(() => {
        pipe = new FileIconPipe();
    });

    it('should return directory icon', () => {
        expect(pipe.transform('inode/directory')).toBe('folder');
    });

    it('should return image icon', () => {
        expect(pipe.transform('image/jpeg')).toBe('image');
        expect(pipe.transform('image/png')).toBe('image');
    });

    it('should return text icon', () => {
        expect(pipe.transform('text/plain')).toBe('description');
        expect(pipe.transform('text/html')).toBe('description');
    });

    it('should return unknown icon', () => {
        expect(pipe.transform('application/octet-stream')).toBe('draft');
    });

    it('should return video icon', () => {
        expect(pipe.transform('video/mp4')).toBe('video');
    });

});
