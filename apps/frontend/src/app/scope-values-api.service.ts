import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { getApiBaseUrl } from './runtime-config';

export interface ScopeValuesResponse {
  workspaces: string[];
  domains: string[];
  projects: string[];
  clients: string[];
  modules: string[];
}

export interface ScopeValuesQuery {
  workspace?: string | null;
  domain?: string | null;
  project?: string | null;
  client?: string | null;
}

@Injectable({ providedIn: 'root' })
export class ScopeValuesApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = getApiBaseUrl();

  listScopeValues(query: ScopeValuesQuery): Observable<ScopeValuesResponse> {
    let params = new HttpParams();

    for (const [key, value] of Object.entries(query)) {
      const normalized = value?.trim();
      if (!normalized) {
        continue;
      }

      params = params.set(key, normalized);
    }

    return this.http.get<ScopeValuesResponse>(`${this.apiBaseUrl}/scope-values`, { params });
  }
}
