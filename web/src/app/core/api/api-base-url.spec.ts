import { REQUEST_CONTEXT, TransferState, makeStateKey } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { API_BASE_URL, DEFAULT_API_BASE_URL } from './api-base-url';

describe('API_BASE_URL', () => {
  it('uses the URL given by the server and hands it to the browser', () => {
    TestBed.configureTestingModule({
      providers: [
        { provide: REQUEST_CONTEXT, useValue: { apiBaseUrl: 'https://api.example.com' } },
      ],
    });

    expect(TestBed.inject(API_BASE_URL)).toBe('https://api.example.com');
    expect(TestBed.inject(TransferState).get(makeStateKey<string>('apiBaseUrl'), '')).toBe(
      'https://api.example.com',
    );
  });

  it('in the browser, reads the URL transferred by the server', () => {
    TestBed.inject(TransferState).set(makeStateKey<string>('apiBaseUrl'), 'https://api.example.com');

    expect(TestBed.inject(API_BASE_URL)).toBe('https://api.example.com');
  });

  it('falls back to the local API when nothing is configured', () => {
    expect(TestBed.inject(API_BASE_URL)).toBe(DEFAULT_API_BASE_URL);
  });
});
