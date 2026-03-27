import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { getApiBaseUrl } from './runtime-config';

export interface OpsPathVisibilitySummary {
  path: string;
  visible_to_runtime: boolean;
  exists: boolean;
  writable?: boolean;
}

export interface OpsSummaryResponse {
  status: string;
  runtime_info: {
    service: string;
    public_api_version: string;
    runtime_mode: 'portable-runtime-container' | 'source-local' | 'unknown';
    answer_provider_mode: string;
    ollama: {
      optional: boolean;
      base_url: string;
      model: string;
    };
  };
  config_summary: {
    frontend_api_base_url?: string;
    backend_cors_origins: string[];
    postgres_target: {
      scheme?: string;
      host?: string;
      port?: number;
      database?: string;
    };
    chroma_persist_directory: string;
    runtime_lifecycle_control: 'external';
  };
  storage_visibility: {
    chroma_persist_directory: OpsPathVisibilitySummary;
    runtime_data_postgres: OpsPathVisibilitySummary;
    runtime_data_chroma: OpsPathVisibilitySummary;
  };
  backup_summary: {
    expected_backup_root: string;
    backup_root_visible_to_runtime: boolean;
    backup_root_exists: boolean;
    discovered_backup_count: number;
    latest_backup_name?: string;
    latest_backup_created_at_utc?: string;
    latest_backup_has_manifest?: boolean;
  };
  notes: string[];
}

@Injectable({ providedIn: 'root' })
export class OpsSummaryApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = getApiBaseUrl();

  getSummary(): Observable<OpsSummaryResponse> {
    return this.http.get<OpsSummaryResponse>(`${this.apiBaseUrl}/ops/summary`);
  }
}
