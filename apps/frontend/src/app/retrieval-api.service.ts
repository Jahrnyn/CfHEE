import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { getApiBaseUrl } from './runtime-config';

export interface RetrievalQueryPayload {
  query_text: string;
  workspace: string;
  domain: string;
  project: string | null;
  client: string | null;
  module: string | null;
  top_k: number;
}

export interface RetrievalScope {
  workspace: string;
  domain: string;
  project: string | null;
  client: string | null;
  module: string | null;
}

export interface RetrievedDocumentSummary {
  id: number;
  title: string;
  source_type: string;
  language: string | null;
  source_ref: string | null;
  created_at: string;
}

export interface RetrievedChunkMatch {
  rank: number;
  chunk_id: number;
  document_id: number;
  chunk_index: number;
  text: string;
  char_count: number;
  similarity_score: number | null;
  distance: number | null;
  created_at: string;
  document: RetrievedDocumentSummary;
  scope: RetrievalScope;
}

export interface RetrievalQueryResponse {
  query_text: string;
  active_scope: RetrievalScope;
  top_k: number;
  returned_results: number;
  empty: boolean;
  results: RetrievedChunkMatch[];
}

@Injectable({ providedIn: 'root' })
export class RetrievalApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = getApiBaseUrl();

  query(payload: RetrievalQueryPayload): Observable<RetrievalQueryResponse> {
    return this.http.post<RetrievalQueryResponse>(`${this.apiBaseUrl}/retrieval/query`, payload);
  }
}
