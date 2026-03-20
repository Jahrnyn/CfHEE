import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { RetrievalQueryPayload, RetrievalScope, RetrievedChunkMatch } from './retrieval-api.service';

export interface AnswerQueryResponse {
  query_text: string;
  active_scope: RetrievalScope;
  grounded: boolean;
  answer_text: string | null;
  message: string | null;
  provider: string;
  provider_error: string | null;
  retrieval_empty: boolean;
  citations: RetrievedChunkMatch[];
}

@Injectable({ providedIn: 'root' })
export class AnswerApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = 'http://127.0.0.1:8000';

  query(payload: RetrievalQueryPayload): Observable<AnswerQueryResponse> {
    return this.http.post<AnswerQueryResponse>(`${this.apiBaseUrl}/answer/query`, payload);
  }
}
