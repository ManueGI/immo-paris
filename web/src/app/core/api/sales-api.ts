import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import type { PropertyType, SalePage } from '@immo-paris/api-client';
import type { Observable } from 'rxjs';

import { API_BASE_URL } from './api-base-url';

export interface SaleListQuery {
  communeCode?: string;
  propertyType?: PropertyType;
  limit?: number;
  cursor?: string | null;
}

/** Sales endpoints of the API. Types come from @immo-paris/api-client (generated). */
@Injectable({ providedIn: 'root' })
export class SalesApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);

  list(query: SaleListQuery = {}): Observable<SalePage> {
    let params = new HttpParams();
    if (query.communeCode) params = params.set('commune_code', query.communeCode);
    if (query.propertyType) params = params.set('property_type', query.propertyType);
    if (query.limit) params = params.set('limit', query.limit);
    if (query.cursor) params = params.set('cursor', query.cursor);
    return this.http.get<SalePage>(`${this.baseUrl}/api/v1/sales`, { params });
  }
}
