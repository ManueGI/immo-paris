import { InjectionToken, REQUEST_CONTEXT, TransferState, inject, makeStateKey } from '@angular/core';

/** Default: the API run locally with uv (`uv run python -m immo_paris` in api/). */
export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

/** What the Node.js server (server.ts) passes to Angular for each request. */
export interface ServerRequestContext {
  apiBaseUrl: string;
}

const API_BASE_URL_KEY = makeStateKey<string>('apiBaseUrl');

/**
 * Base URL of the Immo Paris API, read at runtime rather than at build time, so the same
 * Docker image runs on any host: the server gets it from its API_BASE_URL environment
 * variable and hands it to the browser in the transfer state of the rendered page.
 */
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  factory: () => {
    const transferState = inject(TransferState);
    // Only set during server rendering
    const context = inject(REQUEST_CONTEXT, { optional: true }) as ServerRequestContext | null;
    if (context?.apiBaseUrl) {
      transferState.set(API_BASE_URL_KEY, context.apiBaseUrl);
      return context.apiBaseUrl;
    }
    return transferState.get(API_BASE_URL_KEY, DEFAULT_API_BASE_URL);
  },
});
