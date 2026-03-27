import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { getApiBaseUrl } from './runtime-config';

export interface QueryLogEntry {
  id: number;
  created_at: string;
  query_text: string;
  workspace: string;
  domain: string;
  project: string | null;
  client: string | null;
  module: string | null;
  top_k: number | null;
  result_count: number;
  empty_result: boolean;
  retrieved_chunk_ids: number[];
  retrieved_document_ids: number[];
  selected_context_chunk_ids: number[] | null;
  dropped_context_chunk_ids: number[] | null;
  answer_text: string | null;
  has_evidence: boolean | null;
  context_used_count: number | null;
  answer_length: number | null;
  grounded_flag: string | null;
  provider_used: string;
  fallback_used: boolean;
}

@Injectable({ providedIn: 'root' })
export class QueryLogApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = getApiBaseUrl();

  list(limit = 20): Observable<QueryLogEntry[]> {
    return this.http.get<QueryLogEntry[]>(`${this.apiBaseUrl}/query-logs?limit=${limit}`);
  }
}
