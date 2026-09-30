import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { type ComponentFixture, TestBed } from '@angular/core/testing';
import { Title } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';

import { provideFrenchLocale } from '../../core/locale';
import { communeStats, sale, salePage } from '../../testing/fixtures';
import { ArrondissementPage } from './arrondissement-page';

describe('ArrondissementPage', () => {
  let http: HttpTestingController;
  let fixture: ComponentFixture<ArrondissementPage>;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
        provideFrenchLocale(),
      ],
    });
    http = TestBed.inject(HttpTestingController);

    fixture = TestBed.createComponent(ArrondissementPage);
    // What the router does with withComponentInputBinding() for /arrondissements/paris-11
    fixture.componentRef.setInput('slug', 'paris-11');
    // Start the requests, answer them, then wait until the page is rendered
    TestBed.tick();

    http.expectOne((req) => req.url.endsWith('/api/v1/stats/communes')).flush([communeStats()]);
    http
      .expectOne((req) => req.url.endsWith('/api/v1/sales') && !req.params.has('cursor'))
      .flush(salePage([sale({ id: 1 }), sale({ id: 2 })], 'cursor-page-2'));
    await fixture.whenStable();
  });

  afterEach(() => http.verify());

  const page = () => fixture.nativeElement as HTMLElement;
  const saleRows = () => page().querySelectorAll('tbody tr');
  const loadMoreButton = () => page().querySelector<HTMLButtonElement>('button.load-more');

  it('requests the sales of the arrondissement and shows them', () => {
    expect(page().querySelector('h1')?.textContent).toContain('Paris 11e');
    expect(saleRows()).toHaveLength(2);
    expect(saleRows()[0]?.textContent).toContain('26 RUE GODEFROY CAVAIGNAC');
  });

  it('sets a page title for search engines', () => {
    expect(TestBed.inject(Title).getTitle()).toBe(
      'Prix immobilier Paris 11e : prix au m² et ventes récentes',
    );
  });

  it('appends the next page and hides the button on the last page', async () => {
    loadMoreButton()?.click();
    const request = http.expectOne((req) => req.params.get('cursor') === 'cursor-page-2');
    expect(request.request.params.get('commune_code')).toBe('75111');
    request.flush(salePage([sale({ id: 3 })], null));
    await fixture.whenStable();

    expect(saleRows()).toHaveLength(3);
    expect(loadMoreButton()).toBeNull();
  });
});
