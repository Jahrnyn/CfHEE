import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { getApiBaseUrl } from './runtime-config';

export interface DocumentPayload {
  workspace: string;
  domain: string;
  project: string | null;
  client: string | null;
  module: string | null;
  source_type: string;
  title: string;
  raw_text: string;
  language: string | null;
  source_ref: string | null;
}

export interface DocumentSummary {
  id: number;
  workspace: string;
  domain: string;
  project: string | null;
  client: string | null;
  module: string | null;
  title: string;
  source_type: string;
  language: string | null;
  source_ref: string | null;
  raw_text_preview: string;
  created_at: string;
}

export interface ChunkSummary {
  id: number;
  document_id: number;
  chunk_index: number;
  text: string;
  char_count: number;
  workspace: string;
  domain: string;
  project: string | null;
  client: string | null;
  module: string | null;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class DocumentsApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = getApiBaseUrl();

  createDocument(payload: DocumentPayload): Observable<DocumentSummary> {
    return this.http.post<DocumentSummary>(`${this.apiBaseUrl}/documents`, payload);
  }

  listDocuments(): Observable<DocumentSummary[]> {
    return this.http.get<DocumentSummary[]>(`${this.apiBaseUrl}/documents`);
  }

  listDocumentChunks(documentId: number): Observable<ChunkSummary[]> {
    return this.http.get<ChunkSummary[]>(`${this.apiBaseUrl}/documents/${documentId}/chunks`);
  }
}
