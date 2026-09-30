import { provideHttpClient, withFetch } from '@angular/common/http';
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { provideRouter, withComponentInputBinding } from '@angular/router';

import { routes } from './app.routes';
import { provideFrenchLocale } from './core/locale';

/** Application-wide providers: what the dependency injection can hand out everywhere. */
export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // Route parameters (:slug) are passed to page components as inputs
    provideRouter(routes, withComponentInputBinding()),
    // The browser reuses the HTML rendered by the server instead of rebuilding it, and the
    // HTTP responses fetched during server rendering are not requested a second time
    provideClientHydration(withEventReplay()),
    // fetch() works both in the browser and in the Node.js server that renders the pages
    provideHttpClient(withFetch()),
    provideFrenchLocale(),
  ],
};
