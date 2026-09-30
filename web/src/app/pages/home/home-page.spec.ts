import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { provideFrenchLocale } from '../../core/locale';
import { communeStats } from '../../testing/fixtures';
import { HomePage } from './home-page';

describe('HomePage', () => {
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        // Replaces the network: the test decides what each request returns
        provideHttpClientTesting(),
        provideFrenchLocale(),
      ],
    });
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  async function render(stats: ReturnType<typeof communeStats>[]): Promise<HTMLElement> {
    const fixture = TestBed.createComponent(HomePage);
    // Start the component and its HTTP request. Not whenStable(): a pending request keeps
    // the app unstable until the test answers it, so waiting here would never end
    TestBed.tick();
    http.expectOne((req) => req.url.endsWith('/api/v1/stats/communes')).flush(stats);
    await fixture.whenStable();
    return fixture.nativeElement as HTMLElement;
  }

  it('lists each arrondissement with its median price and a link to its page', async () => {
    const page = await render([communeStats()]);

    const row = page.querySelector('tbody tr');
    expect(row?.textContent).toContain('Paris 11e');
    // French thousands separator is a narrow no-break space (U+202F), matched by \s
    expect(row?.textContent).toMatch(/9\s972/);
    expect(row?.querySelector('a')?.getAttribute('href')).toBe('/arrondissements/paris-11');
  });

  it('does not show a median computed on too few sales', async () => {
    const page = await render([
      communeStats({ median_price_per_m2: null, p25_price_per_m2: null, p75_price_per_m2: null }),
    ]);

    expect(page.querySelector('tbody tr')?.textContent).toContain('Pas assez de ventes');
  });

  it('shows a message when the API fails', async () => {
    const fixture = TestBed.createComponent(HomePage);
    TestBed.tick();
    http
      .expectOne((req) => req.url.endsWith('/api/v1/stats/communes'))
      .flush('boom', { status: 503, statusText: 'Service Unavailable' });
    await fixture.whenStable();

    const alert = (fixture.nativeElement as HTMLElement).querySelector('[role="alert"]');
    expect(alert?.textContent).toContain('momentanément indisponibles');
  });
});
