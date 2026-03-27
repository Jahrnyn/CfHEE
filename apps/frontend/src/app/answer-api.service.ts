import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { RetrievalQueryPayload, RetrievalScope, RetrievedChunkMatch } from './retrieval-api.service';
import { getApiBaseUrl } from './runtime-config';

export interface AnswerQueryResponse {
  query_text: string;
  active_scope: RetrievalScope;
  grounded: boolean;
  answer_text: string | null;
  message: string | null;
  requested_provider: string;
  provider: string;
  fallback_used: boolean;
  provider_error: string | null;
  retrieval_empty: boolean;
  citations: RetrievedChunkMatch[];
}

@Injectable({ providedIn: 'root' })
export class AnswerApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = getApiBaseUrl();

  query(payload: RetrievalQueryPayload): Observable<AnswerQueryResponse> {
    return this.http.post<AnswerQueryResponse>(`${this.apiBaseUrl}/answer/query`, payload);
  }
}
