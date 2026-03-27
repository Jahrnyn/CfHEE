import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import { OpsPathVisibilitySummary, OpsSummaryApiService, OpsSummaryResponse } from '../ops-summary-api.service';

@Component({
  selector: 'app-operations-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="panel surface-panel">
      <div class="header">
        <div>
          <p class="label">Read-only ops summary</p>
          <h2>Operations / Admin</h2>
          <p class="intro">
            Inspect the current CfHEE runtime conservatively from the running app. Runtime lifecycle
            control still remains external to the workbench.
          </p>
        </div>

        <div class="actions">
          <button type="button" (click)="loadSummary()" [disabled]="isLoading">
            {{ isLoading ? 'Refreshing...' : 'Refresh summary' }}
          </button>
        </div>
      </div>

      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>

      <div *ngIf="isLoading && !summary" class="status">Loading operations summary...</div>

      <div class="section-grid" *ngIf="summary">
        <section class="card surface-card">
          <p class="card-label">Runtime</p>
          <h3>Runtime info</h3>
          <p class="meta"><strong>Service:</strong> {{ summary.runtime_info.service }}</p>
          <p class="meta"><strong>Public API:</strong> {{ summary.runtime_info.public_api_version }}</p>
          <p class="meta"><strong>Runtime mode:</strong> {{ formatRuntimeMode(summary.runtime_info.runtime_mode) }}</p>
          <p class="meta"><strong>Answer provider mode:</strong> {{ summary.runtime_info.answer_provider_mode }}</p>
          <p class="meta">
            <strong>Ollama:</strong>
            {{ summary.runtime_info.ollama.optional ? 'optional' : 'required' }}
          </p>
          <p class="meta"><strong>Ollama base URL:</strong> {{ summary.runtime_info.ollama.base_url }}</p>
          <p class="meta"><strong>Ollama model:</strong> {{ summary.runtime_info.ollama.model }}</p>
        </section>

        <section class="card surface-card">
          <p class="card-label">Config</p>
          <h3>Backend/runtime config</h3>
          <p class="meta">
            <strong>Frontend-facing backend URL:</strong>
            {{ summary.config_summary.frontend_api_base_url || 'Not reported by the current backend runtime' }}
          </p>
          <p class="meta">
            <strong>Runtime lifecycle control:</strong> {{ summary.config_summary.runtime_lifecycle_control }}
          </p>
          <div class="meta-block">
            <strong>Backend CORS origins:</strong>
            <ul class="list">
              <li *ngFor="let origin of summary.config_summary.backend_cors_origins">{{ origin }}</li>
            </ul>
          </div>
        </section>

        <section class="card surface-card">
          <p class="card-label">Storage</p>
          <h3>Persistence targets</h3>
          <p class="meta">
            <strong>Postgres target:</strong>
            {{ formatPostgresTarget() }}
          </p>
          <p class="meta">
            <strong>Chroma path:</strong> {{ summary.config_summary.chroma_persist_directory }}
          </p>
        </section>
      </div>

      <section class="panel panel-secondary surface-panel" *ngIf="summary">
        <p class="card-label">Visibility</p>
        <h3>Storage/path visibility</h3>

        <div class="paths">
          <article class="path-card surface-card">
            <h4>Chroma persistence</h4>
            <p class="path">{{ summary.storage_visibility.chroma_persist_directory.path }}</p>
            <p class="meta">{{ formatPathSummary(summary.storage_visibility.chroma_persist_directory) }}</p>
          </article>

          <article class="path-card surface-card">
            <h4>runtime-data/postgres</h4>
            <p class="path">{{ summary.storage_visibility.runtime_data_postgres.path }}</p>
            <p class="meta">{{ formatPathSummary(summary.storage_visibility.runtime_data_postgres) }}</p>
          </article>

          <article class="path-card surface-card">
            <h4>runtime-data/chroma</h4>
            <p class="path">{{ summary.storage_visibility.runtime_data_chroma.path }}</p>
            <p class="meta">{{ formatPathSummary(summary.storage_visibility.runtime_data_chroma) }}</p>
          </article>
        </div>
      </section>

      <section class="panel panel-secondary surface-panel" *ngIf="summary">
        <p class="card-label">Notes</p>
        <h3>Operational boundaries</h3>
        <ul class="list">
          <li *ngFor="let note of summary.notes">{{ note }}</li>
        </ul>
      </section>
    </section>
  `,
  styles: [
    `
      .panel {
        padding: 24px;
      }

      .panel + .panel {
        margin-top: 20px;
      }

      .panel-secondary {
        margin-top: 20px;
      }

      .header {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 24px;
      }

      .label,
      .card-label {
        margin: 0 0 8px;
        color: #7a5c2e;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      h2,
      h3,
      h4 {
        margin-top: 0;
      }

      .intro,
      .meta,
      .path,
      .status {
        color: #3f3f46;
        line-height: 1.6;
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
      }

      button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        padding: 0 16px;
        border: 0;
        border-radius: 999px;
        color: #fff;
        font: inherit;
        background: #0f766e;
        cursor: pointer;
      }

      button:disabled {
        cursor: default;
        opacity: 0.7;
      }

      .error {
        margin: 0 0 16px;
        padding: 12px 14px;
        border-radius: 14px;
        color: #991b1b;
        background: #fee2e2;
      }

      .status {
        margin: 0;
        padding: 12px 14px;
        border-radius: 14px;
        color: #1d4ed8;
        background: #dbeafe;
      }

      .section-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
      }

      .card,
      .path-card {
        padding: 18px;
      }

      .meta {
        margin: 8px 0 0;
      }

      .meta-block {
        margin-top: 12px;
      }

      .list {
        margin: 10px 0 0;
        padding-left: 18px;
        color: #3f3f46;
        line-height: 1.6;
      }

      .paths {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      }

      .path {
        margin: 10px 0 0;
        word-break: break-word;
      }
    `
  ]
})
export class OperationsPageComponent implements OnInit {
  private readonly opsSummaryApi = inject(OpsSummaryApiService);

  protected summary: OpsSummaryResponse | null = null;
  protected isLoading = false;
  protected errorMessage = '';

  ngOnInit(): void {
    this.loadSummary();
  }

  protected loadSummary(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.opsSummaryApi.getSummary().subscribe({
      next: (summary) => {
        this.summary = summary;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Unable to load the current operations summary from the backend.';
        this.isLoading = false;
      }
    });
  }

  protected formatRuntimeMode(mode: OpsSummaryResponse['runtime_info']['runtime_mode']): string {
    switch (mode) {
      case 'portable-runtime-container':
        return 'Portable runtime container';
      case 'source-local':
        return 'Source-based local run';
      default:
        return 'Unknown / mixed runtime shape';
    }
  }

  protected formatPostgresTarget(): string {
    if (!this.summary) {
      return '';
    }

    const target = this.summary.config_summary.postgres_target;
    const host = target.host || 'unknown-host';
    const port = target.port ?? 'unknown-port';
    const database = target.database || 'unknown-db';
    return `${host}:${port}/${database}`;
  }

  protected formatPathSummary(pathSummary: OpsPathVisibilitySummary): string {
    const parts = [
      pathSummary.visible_to_runtime ? 'Visible to runtime' : 'Not visible to runtime',
      pathSummary.exists ? 'Exists' : 'Missing'
    ];

    if (pathSummary.writable !== undefined) {
      parts.push(pathSummary.writable ? 'Writable' : 'Not writable');
    }

    return parts.join(' | ');
  }
}
