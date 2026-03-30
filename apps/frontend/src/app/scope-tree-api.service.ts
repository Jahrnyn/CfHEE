import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { getApiBaseUrl } from './runtime-config';

export interface ScopeTreeModuleNode {
  name: string;
}

export interface ScopeTreeClientNode {
  name: string;
  modules: ScopeTreeModuleNode[];
}

export interface ScopeTreeProjectNode {
  name: string;
  clients: ScopeTreeClientNode[];
}

export interface ScopeTreeDomainNode {
  name: string;
  projects: ScopeTreeProjectNode[];
}

export interface ScopeTreeWorkspaceNode {
  name: string;
  domains: ScopeTreeDomainNode[];
}

export interface ScopeTreeResponse {
  workspaces: ScopeTreeWorkspaceNode[];
}

@Injectable({ providedIn: 'root' })
export class ScopeTreeApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = getApiBaseUrl();

  getScopeTree(): Observable<ScopeTreeResponse> {
    return this.http.get<ScopeTreeResponse>(`${this.apiBaseUrl}/api/v1/scopes/tree`);
  }
}
