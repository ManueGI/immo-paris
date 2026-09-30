import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import type { CommuneStats, PropertyType } from '@immo-paris/api-client';
import type { Observable } from 'rxjs';

import { API_BASE_URL } from './api-base-url';

/** Statistics endpoints of the API. */
@Injectable({ providedIn: 'root' })
export class StatsApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(API_BASE_URL);

  /** Price per m² statistics by commune; the API defaults to its latest year. */
  communeStats(propertyType?: PropertyType): Observable<CommuneStats[]> {
    const params = propertyType ? new HttpParams().set('property_type', propertyType) : undefined;
    return this.http.get<CommuneStats[]>(`${this.baseUrl}/api/v1/stats/communes`, { params });
  }
}
