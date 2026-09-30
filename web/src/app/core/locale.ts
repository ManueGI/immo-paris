import { registerLocaleData } from '@angular/common';
import localeFr from '@angular/common/locales/fr';
import { LOCALE_ID, type Provider } from '@angular/core';

// French formats for the number, currency and date pipes (1 234 €, 1 oct. 2026)
registerLocaleData(localeFr);

/** French locale for the whole app; also used by tests that render formatted values. */
export function provideFrenchLocale(): Provider {
  return { provide: LOCALE_ID, useValue: 'fr-FR' };
}
