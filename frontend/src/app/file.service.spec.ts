import { TestBed } from '@angular/core/testing';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { FileService } from './file.service';

describe('FileService', () => {
    let service: FileService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                provideHttpClient(),
                provideHttpClientTesting(),
            ]
        });
        service = TestBed.inject(FileService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
