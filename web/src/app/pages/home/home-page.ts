import { CurrencyPipe } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { Meta } from '@angular/platform-browser';
import { RouterLink } from '@angular/router';

import { StatsApi } from '../../core/api/stats-api';
import { arrondissementByCode } from '../../core/arrondissements';

/** Home page: price per m² of apartments in the 20 arrondissements. */
@Component({
  selector: 'app-home-page',
  imports: [RouterLink, CurrencyPipe],
  templateUrl: './home-page.html',
  styleUrl: './home-page.scss',
})
export class HomePage {
  private readonly statsApi = inject(StatsApi);

  /** Loads the statistics once; exposes value(), isLoading() and error() as signals */
  protected readonly stats = rxResource({
    stream: () => this.statsApi.communeStats('apartment'),
  });

  /** Statistics, or [] while loading or after an error (value() throws in an error state) */
  private readonly loadedStats = computed(() => (this.stats.hasValue() ? this.stats.value() : []));

  /** Rows of the table: each statistic joined with its arrondissement (slug, label) */
  protected readonly rows = computed(() =>
    this.loadedStats().flatMap((stats) => {
      const arrondissement = arrondissementByCode(stats.commune_code);
      return arrondissement ? [{ arrondissement, stats }] : [];
    }),
  );

  protected readonly year = computed(() => this.loadedStats()[0]?.year);

  constructor() {
    inject(Meta).updateTag({
      name: 'description',
      content:
        'Prix médian au m² des appartements dans chaque arrondissement de Paris, ' +
        'calculé sur les ventes réelles publiées par la DGFiP.',
    });
  }
}
