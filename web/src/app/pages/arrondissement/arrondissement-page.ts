import { CurrencyPipe, DatePipe, formatNumber } from '@angular/common';
import {
  Component,
  LOCALE_ID,
  computed,
  effect,
  inject,
  input,
  linkedSignal,
  signal,
} from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { Meta, Title } from '@angular/platform-browser';
import { RouterLink } from '@angular/router';
import type { Sale } from '@immo-paris/api-client';
import { finalize } from 'rxjs';

import { SalesApi } from '../../core/api/sales-api';
import { StatsApi } from '../../core/api/stats-api';
import { type Arrondissement, arrondissementBySlug } from '../../core/arrondissements';
import { PriceStatsCard } from '../../shared/price-stats-card';
import { PropertyTypeLabelPipe } from '../../shared/property-type-label-pipe';

const PAGE_SIZE = 20;

/** One arrondissement: price statistics and the most recent sales, 20 at a time. */
@Component({
  selector: 'app-arrondissement-page',
  imports: [RouterLink, CurrencyPipe, DatePipe, PriceStatsCard, PropertyTypeLabelPipe],
  templateUrl: './arrondissement-page.html',
  styleUrl: './arrondissement-page.scss',
})
export class ArrondissementPage {
  private readonly salesApi = inject(SalesApi);
  private readonly statsApi = inject(StatsApi);
  private readonly title = inject(Title);
  private readonly meta = inject(Meta);
  private readonly locale = inject(LOCALE_ID);

  /** `:slug` route parameter, bound by withComponentInputBinding() */
  readonly slug = input.required<string>();

  protected readonly arrondissement = computed<Arrondissement>(() => {
    const arrondissement = arrondissementBySlug(this.slug());
    // The route's canMatch guard only lets known slugs reach this page
    if (!arrondissement) throw new Error(`Unknown arrondissement: ${this.slug()}`);
    return arrondissement;
  });

  // ---- Statistics ----
  private readonly stats = rxResource({ stream: () => this.statsApi.communeStats() });

  protected readonly apartmentStats = computed(() => this.statsFor('apartment'));
  protected readonly houseStats = computed(() => this.statsFor('house'));

  // ---- Sales, paginated ----
  /** First page; reloaded automatically when the arrondissement changes */
  protected readonly firstPage = rxResource({
    params: () => ({ communeCode: this.arrondissement().code }),
    stream: ({ params }) =>
      this.salesApi.list({ communeCode: params.communeCode, limit: PAGE_SIZE }),
  });

  /** Pages added with "Voir plus"; reset to [] when the arrondissement changes */
  private readonly nextPages = linkedSignal<string, Sale[]>({
    source: () => this.arrondissement().code,
    computation: () => [],
  });

  /** Cursor of the next page, from the first page then from each loaded page */
  protected readonly nextCursor = linkedSignal(() =>
    this.firstPage.hasValue() ? this.firstPage.value().next_cursor : null,
  );

  protected readonly sales = computed(() => [
    // value() throws when the resource is in an error state: read it only when it has one
    ...(this.firstPage.hasValue() ? this.firstPage.value().items : []),
    ...this.nextPages(),
  ]);

  protected readonly loadingMore = signal(false);

  constructor() {
    // Title and description for search engines, recomputed when their inputs change
    effect(() => {
      const { label } = this.arrondissement();
      const median = this.apartmentStats()?.median_price_per_m2;
      this.title.setTitle(`Prix immobilier ${label} : prix au m² et ventes récentes`);
      this.meta.updateTag({
        name: 'description',
        content:
          median != null
            ? `Prix médian des appartements à ${label} : ${formatNumber(median, this.locale, '1.0-0')} €/m². ` +
              'Statistiques et dernières ventes réelles publiées par la DGFiP.'
            : `Prix au m² et dernières ventes immobilières réelles à ${label}.`,
      });
    });
  }

  protected loadMore(): void {
    const cursor = this.nextCursor();
    if (!cursor || this.loadingMore()) return;

    this.loadingMore.set(true);
    this.salesApi
      .list({ communeCode: this.arrondissement().code, limit: PAGE_SIZE, cursor })
      .pipe(finalize(() => this.loadingMore.set(false)))
      .subscribe((page) => {
        this.nextPages.update((sales) => [...sales, ...page.items]);
        this.nextCursor.set(page.next_cursor);
      });
  }

  private statsFor(propertyType: Sale['property_type']) {
    if (!this.stats.hasValue()) return undefined;
    const code = this.arrondissement().code;
    return this.stats
      .value()
      .find((stats) => stats.commune_code === code && stats.property_type === propertyType);
  }
}
