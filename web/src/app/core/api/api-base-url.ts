import { InjectionToken } from '@angular/core';

/**
 * Base URL of the Immo Paris API. Defaults to the API run locally with uv
 * (`uv run python -m immo_paris` in api/); each deployment will provide its own value.
 */
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  factory: () => 'http://127.0.0.1:8000',
});
