import { CurrencyPipe } from '@angular/common';
import { Component, input } from '@angular/core';
import type { CommuneStats } from '@immo-paris/api-client';

/** Median price per m² and its interquartile range for one property type. */
@Component({
  selector: 'app-price-stats-card',
  imports: [CurrencyPipe],
  template: `
    <article class="card">
      <h2>{{ heading() }}</h2>
      @let s = stats();
      @if (s && s.median_price_per_m2 !== null) {
        <p class="median">{{ s.median_price_per_m2 | currency: 'EUR' : 'symbol' : '1.0-0' }}/m²</p>
        <p class="detail">
          La moitié des ventes entre
          {{ s.p25_price_per_m2 | currency: 'EUR' : 'symbol' : '1.0-0' }} et
          {{ s.p75_price_per_m2 | currency: 'EUR' : 'symbol' : '1.0-0' }}/m², sur
          {{ s.sales_count }} ventes en {{ s.year }}.
        </p>
      } @else {
        <p class="median">—</p>
        <p class="detail">Pas assez de ventes pour un prix fiable.</p>
      }
    </article>
  `,
  styles: `
    .card {
      padding: 1rem;
      border: 1px solid var(--border);
      border-radius: 0.5rem;
      background: var(--surface);
    }
    h2 {
      margin: 0;
      font-size: 1rem;
      color: var(--muted);
    }
    .median {
      margin: 0.25rem 0;
      font-size: 1.75rem;
      font-weight: 700;
    }
    .detail {
      margin: 0;
      color: var(--muted);
    }
  `,
})
export class PriceStatsCard {
  /** Card title, e.g. "Appartements" */
  readonly heading = input.required<string>();
  /** Statistics to show; undefined when the API has no data for this property type */
  readonly stats = input<CommuneStats | undefined>();
}
