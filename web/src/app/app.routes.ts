import type { CanMatchFn, Routes } from '@angular/router';

import { arrondissementBySlug } from './core/arrondissements';

/** Only known arrondissement slugs match; anything else falls through to the 404 page. */
const isArrondissementSlug: CanMatchFn = (_route, segments) =>
  arrondissementBySlug(segments[1]?.path ?? '') !== undefined;

export const routes: Routes = [
  {
    path: '',
    title: "Prix de l'immobilier à Paris par arrondissement",
    // Lazy loading: the page code is downloaded only when the page is visited
    loadComponent: () => import('./pages/home/home-page').then((m) => m.HomePage),
  },
  {
    path: 'arrondissements/:slug',
    canMatch: [isArrondissementSlug],
    loadComponent: () =>
      import('./pages/arrondissement/arrondissement-page').then((m) => m.ArrondissementPage),
  },
  {
    path: '**',
    title: 'Page introuvable',
    loadComponent: () => import('./pages/not-found/not-found-page').then((m) => m.NotFoundPage),
  },
];
