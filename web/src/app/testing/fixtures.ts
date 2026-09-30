import type { CommuneStats, Sale, SalePage } from '@immo-paris/api-client';

/** Builders of API responses for tests, typed with the generated API client. */

export function communeStats(overrides: Partial<CommuneStats> = {}): CommuneStats {
  return {
    commune_code: '75111',
    commune_label: 'Paris 11e',
    year: 2025,
    property_type: 'apartment',
    sales_count: 1500,
    p25_price_per_m2: 8900,
    median_price_per_m2: 9972,
    p75_price_per_m2: 11000,
    avg_surface_m2: 45,
    ...overrides,
  };
}

export function sale(overrides: Partial<Sale> = {}): Sale {
  return {
    id: 1,
    mutation_id: '2025-1',
    date: '2025-12-31',
    commune_code: '75111',
    commune_label: 'Paris 11e',
    address: '26 RUE GODEFROY CAVAIGNAC 75011',
    postal_code: '75011',
    property_type: 'apartment',
    surface_m2: 31,
    rooms: 2,
    price: 393750,
    price_per_m2: 12702,
    longitude: 2.38,
    latitude: 48.85,
    ...overrides,
  };
}

export function salePage(items: Sale[], nextCursor: string | null = null): SalePage {
  return { items, next_cursor: nextCursor };
}
