import { RESPONSE_INIT } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { NotFoundPage } from './not-found-page';

describe('NotFoundPage', () => {
  it('answers with a 404 status when rendered on the server', () => {
    const response: ResponseInit = {};
    TestBed.configureTestingModule({
      providers: [provideRouter([]), { provide: RESPONSE_INIT, useValue: response }],
    });

    TestBed.createComponent(NotFoundPage);

    expect(response.status).toBe(404);
  });

  it('renders in the browser, where there is no response to set', () => {
    TestBed.configureTestingModule({ providers: [provideRouter([])] });

    const fixture = TestBed.createComponent(NotFoundPage);

    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Page introuvable');
  });
});
