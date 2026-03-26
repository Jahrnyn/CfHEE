import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AnswerApiService, AnswerQueryResponse } from '../answer-api.service';
import { QueryLogApiService, QueryLogEntry } from '../query-log-api.service';
import {
  RetrievalApiService,
  RetrievalQueryPayload,
  RetrievalQueryResponse
} from '../retrieval-api.service';

@Component({
  selector: 'app-ask-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="panel">
      <p class="label">Scoped retrieval</p>
      <h2>Ask Copilot</h2>
      <p class="intro">
        Grounded answers reuse scoped retrieval only. Workspace and domain are required so results
        stay scoped by default, and no answer is produced without retrieved evidence.
      </p>

      <div class="scope-summary">
        <strong>Current scope:</strong> {{ currentScopeSummary }}
      </div>

      <form class="query-form" (ngSubmit)="submit()" #queryForm="ngForm">
        <label>
          <span>Query text</span>
          <textarea [(ngModel)]="form.queryText" name="queryText" rows="5" required></textarea>
        </label>

        <div class="field-grid">
          <label>
            <span>Workspace</span>
            <input [(ngModel)]="form.workspace" name="workspace" required />
          </label>

          <label>
            <span>Domain</span>
            <input [(ngModel)]="form.domain" name="domain" required />
          </label>

          <label>
            <span>Project</span>
            <input [(ngModel)]="form.project" name="project" />
          </label>

          <label>
            <span>Client</span>
            <input [(ngModel)]="form.client" name="client" />
          </label>

          <label>
            <span>Module</span>
            <input [(ngModel)]="form.module" name="module" />
          </label>

          <label>
            <span>Top K</span>
            <input [(ngModel)]="form.topK" name="topK" type="number" min="1" max="20" />
          </label>
        </div>

        <div class="actions">
          <button type="submit" [disabled]="isSubmitting || queryForm.invalid">
            {{ isSubmitting && activeAction === 'answer' ? 'Generating answer...' : 'Generate grounded answer' }}
          </button>
          <button type="button" class="secondary-button" (click)="retrieveOnly()" [disabled]="isSubmitting || queryForm.invalid">
            {{ isSubmitting && activeAction === 'retrieval' ? 'Retrieving...' : 'Retrieve chunks only' }}
          </button>
        </div>
      </form>

      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>
      <p *ngIf="isSubmitting" class="status">
        {{ activeAction === 'answer' ? 'Generating grounded answer from retrieved chunks...' : 'Searching scoped chunks...' }}
      </p>

      <section class="answer-section" *ngIf="lastAnswerResponse">
        <div class="results-header">
          <div>
            <h3>Grounded answer</h3>
            <p class="meta">
              Active scope:
              {{ lastAnswerResponse.active_scope.workspace }} / {{ lastAnswerResponse.active_scope.domain }}
              <ng-container *ngIf="lastAnswerResponse.active_scope.project">
                / {{ lastAnswerResponse.active_scope.project }}
              </ng-container>
              <ng-container *ngIf="lastAnswerResponse.active_scope.client">
                / {{ lastAnswerResponse.active_scope.client }}
              </ng-container>
              <ng-container *ngIf="lastAnswerResponse.active_scope.module">
                / {{ lastAnswerResponse.active_scope.module }}
              </ng-container>
            </p>
          </div>
          <p class="meta">
            Provider: {{ lastAnswerResponse.provider }}
            <ng-container *ngIf="lastAnswerResponse.fallback_used">
              (fallback from {{ lastAnswerResponse.requested_provider }})
            </ng-container>
          </p>
        </div>

        <div *ngIf="lastAnswerResponse.grounded" class="answer-card">
          <p class="answer-label">Short answer</p>
          <p class="answer-text">{{ lastAnswerResponse.answer_text }}</p>
          <p class="meta" *ngIf="lastAnswerResponse.message">{{ lastAnswerResponse.message }}</p>
        </div>

        <div *ngIf="!lastAnswerResponse.grounded" class="empty-state">
          <p class="empty-title">
            {{
              lastAnswerResponse.retrieval_empty
                ? 'No evidence in the selected scope'
                : 'No grounded answer'
            }}
          </p>
          <p class="empty">{{ lastAnswerNoEvidenceMessage }}</p>
          <p class="meta" *ngIf="lastAnswerResponse.provider_error">
            <strong>Provider error:</strong> {{ lastAnswerResponse.provider_error }}
          </p>
        </div>

        <div class="citations" *ngIf="lastAnswerResponse.citations.length > 0">
          <h4>Cited support</h4>

          <article class="result-card" *ngFor="let citation of lastAnswerResponse.citations">
            <div class="card-header">
              <h4>#{{ citation.rank }} - {{ citation.document.title }}</h4>
              <p *ngIf="citation.similarity_score !== null">
                Similarity: {{ citation.similarity_score | number: '1.3-3' }}
              </p>
            </div>

            <p class="meta">
              <strong>Scope:</strong>
              {{ citation.scope.workspace }} / {{ citation.scope.domain }}
              <ng-container *ngIf="citation.scope.project"> / {{ citation.scope.project }}</ng-container>
              <ng-container *ngIf="citation.scope.client"> / {{ citation.scope.client }}</ng-container>
              <ng-container *ngIf="citation.scope.module"> / {{ citation.scope.module }}</ng-container>
            </p>
            <p class="meta"><strong>Document ID:</strong> {{ citation.document_id }}</p>
            <p class="meta"><strong>Chunk ID:</strong> {{ citation.chunk_id }}</p>
            <p class="meta"><strong>Chunk:</strong> {{ citation.chunk_index + 1 }} ({{ citation.char_count }} chars)</p>
            <p class="meta" *ngIf="citation.distance !== null"><strong>Distance:</strong> {{ citation.distance | number: '1.3-3' }}</p>
            <p class="meta"><strong>Source type:</strong> {{ citation.document.source_type }}</p>
            <p class="meta" *ngIf="citation.document.source_ref"><strong>Source ref:</strong> {{ citation.document.source_ref }}</p>
            <p class="chunk-text">{{ citation.text }}</p>
          </article>
        </div>
      </section>

      <section class="results" *ngIf="lastResponse">
        <div class="results-header">
          <div>
            <h3>Retrieved chunks</h3>
            <p class="meta">
              Active scope:
              {{ lastResponse.active_scope.workspace }} / {{ lastResponse.active_scope.domain }}
              <ng-container *ngIf="lastResponse.active_scope.project">
                / {{ lastResponse.active_scope.project }}
              </ng-container>
              <ng-container *ngIf="lastResponse.active_scope.client">
                / {{ lastResponse.active_scope.client }}
              </ng-container>
              <ng-container *ngIf="lastResponse.active_scope.module">
                / {{ lastResponse.active_scope.module }}
              </ng-container>
            </p>
          </div>
          <p class="meta">{{ lastResponse.returned_results }} result(s) from top_k={{ lastResponse.top_k }}</p>
        </div>

        <div *ngIf="lastResponse.empty" class="empty-state">
          <p class="empty-title">No results found</p>
          <p class="empty">
            No chunks matched this query inside the selected scope.
          </p>
        </div>

        <article class="result-card" *ngFor="let result of lastResponse.results">
          <div class="card-header">
            <h4>#{{ result.rank }} - {{ result.document.title }}</h4>
            <p *ngIf="result.similarity_score !== null">
              Similarity: {{ result.similarity_score | number: '1.3-3' }}
            </p>
          </div>

          <p class="meta">
            <strong>Scope:</strong>
            {{ result.scope.workspace }} / {{ result.scope.domain }}
            <ng-container *ngIf="result.scope.project"> / {{ result.scope.project }}</ng-container>
            <ng-container *ngIf="result.scope.client"> / {{ result.scope.client }}</ng-container>
            <ng-container *ngIf="result.scope.module"> / {{ result.scope.module }}</ng-container>
          </p>
          <p class="meta"><strong>Document ID:</strong> {{ result.document_id }}</p>
          <p class="meta"><strong>Chunk ID:</strong> {{ result.chunk_id }}</p>
          <p class="meta"><strong>Chunk:</strong> {{ result.chunk_index + 1 }} ({{ result.char_count }} chars)</p>
          <p class="meta" *ngIf="result.distance !== null"><strong>Distance:</strong> {{ result.distance | number: '1.3-3' }}</p>
          <p class="meta"><strong>Source type:</strong> {{ result.document.source_type }}</p>
          <p class="meta" *ngIf="result.document.language"><strong>Language:</strong> {{ result.document.language }}</p>
          <p class="meta" *ngIf="result.document.source_ref"><strong>Source ref:</strong> {{ result.document.source_ref }}</p>
          <p class="chunk-text">{{ result.text }}</p>
        </article>
      </section>
    </section>
  `,
  styles: [
    `
      .panel {
        padding: 24px;
        border: 1px solid #e4e4e7;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 18px 40px rgba(24, 24, 27, 0.06);
      }

      .label {
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
      .empty,
      .chunk-text {
        color: #3f3f46;
        line-height: 1.6;
      }

      .query-form {
        display: grid;
        gap: 16px;
      }

      .scope-summary,
      .status,
      .empty-state {
        margin-top: 16px;
        padding: 12px 14px;
        border-radius: 14px;
      }

      .scope-summary {
        color: #1f2937;
        background: #f4f4f5;
      }

      .field-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
      }

      label {
        display: grid;
        gap: 8px;
      }

      span {
        font-weight: 600;
      }

      input,
      textarea {
        width: 100%;
        padding: 12px 14px;
        border: 1px solid #d4d4d8;
        border-radius: 14px;
        font: inherit;
        background: #fff;
      }

      textarea {
        resize: vertical;
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

      .secondary-button {
        color: #18181b;
        border: 1px solid #d4d4d8;
        background: #fff;
      }

      .error {
        margin: 16px 0 0;
        padding: 12px 14px;
        border-radius: 14px;
        color: #991b1b;
        background: #fee2e2;
      }

      .status {
        color: #1d4ed8;
        background: #dbeafe;
      }

      .results {
        margin-top: 24px;
        display: grid;
        gap: 16px;
      }

      .answer-section {
        margin-top: 24px;
        display: grid;
        gap: 16px;
      }

      .results-header,
      .card-header {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: space-between;
        align-items: baseline;
      }

      .result-card {
        padding: 18px;
        border: 1px solid #e4e4e7;
        border-radius: 18px;
        background: #fff;
      }

      .card-header p,
      .results-header p {
        margin: 0;
        color: #71717a;
      }

      .meta {
        margin: 8px 0 0;
      }

      .answer-card {
        padding: 18px;
        border: 1px solid #d1fae5;
        border-radius: 18px;
        background: #ecfdf5;
      }

      .answer-label {
        margin: 0 0 8px;
        color: #065f46;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      .answer-text {
        margin: 0;
        color: #064e3b;
        line-height: 1.7;
      }

      .empty-state {
        border: 1px dashed #d4d4d8;
        background: #fafafa;
      }

      .empty-title {
        margin: 0 0 8px;
        color: #18181b;
        font-weight: 700;
      }

      .citations {
        display: grid;
        gap: 16px;
      }

      .citations h4 {
        margin: 0;
      }

      .chunk-text {
        margin: 16px 0 0;
        padding-top: 16px;
        border-top: 1px solid #e4e4e7;
        white-space: pre-wrap;
        color: #18181b;
      }
    `
  ]
})
export class AskPageComponent {
  private readonly answerApi = inject(AnswerApiService);
  private readonly queryLogApi = inject(QueryLogApiService);
  private readonly retrievalApi = inject(RetrievalApiService);

  protected isSubmitting = false;
  protected activeAction: 'answer' | 'retrieval' | null = null;
  protected errorMessage = '';
  protected lastAnswerResponse: AnswerQueryResponse | null = null;
  protected lastQueryLog: QueryLogEntry | null = null;
  protected lastResponse: RetrievalQueryResponse | null = null;
  protected form = {
    queryText: '',
    workspace: '',
    domain: '',
    project: '',
    client: '',
    module: '',
    topK: 5
  };

  protected submit(): void {
    this.generateAnswer();
  }

  protected retrieveOnly(): void {
    const payload = this.buildPayload();
    this.isSubmitting = true;
    this.activeAction = 'retrieval';
    this.errorMessage = '';
    this.lastAnswerResponse = null;
    this.lastQueryLog = null;
    this.lastResponse = null;

    this.retrievalApi.query(payload).subscribe({
      next: (response) => {
        this.lastResponse = response;
        this.isSubmitting = false;
        this.activeAction = null;
        this.refreshLatestQueryLog(payload);
      },
      error: (error) => {
        this.errorMessage = this.formatError(error);
        this.isSubmitting = false;
        this.activeAction = null;
      }
    });
  }

  private generateAnswer(): void {
    const payload = this.buildPayload();
    this.isSubmitting = true;
    this.activeAction = 'answer';
    this.errorMessage = '';
    this.lastAnswerResponse = null;
    this.lastQueryLog = null;
    this.lastResponse = null;

    this.answerApi.query(payload).subscribe({
      next: (response) => {
        this.lastAnswerResponse = response;
        this.isSubmitting = false;
        this.activeAction = null;
        this.refreshLatestQueryLog(payload);
      },
      error: (error) => {
        this.errorMessage = this.formatError(error);
        this.isSubmitting = false;
        this.activeAction = null;
      }
    });
  }

  protected get currentScopeSummary(): string {
    return this.buildScopeSummary(
      this.form.workspace,
      this.form.domain,
      this.form.project,
      this.form.client,
      this.form.module
    );
  }

  protected get lastAnswerNoEvidenceMessage(): string {
    if (!this.lastAnswerResponse) {
      return 'Not enough evidence in retrieved context.';
    }

    if (this.lastAnswerResponse.retrieval_empty) {
      return 'No chunks matched this query inside the selected scope, so no grounded answer was generated.';
    }

    return this.lastAnswerResponse.message ?? 'Not enough evidence in retrieved context.';
  }

  private buildScopeSummary(
    workspace: string,
    domain: string,
    project: string,
    client: string,
    module: string
  ): string {
    if (!workspace.trim() || !domain.trim()) {
      return 'Global retrieval is disabled. Workspace and domain are required.';
    }

    const scopeParts = [workspace.trim(), domain.trim(), project.trim(), client.trim(), module.trim()].filter(
      (value) => value.length > 0
    );

    return scopeParts.join(' / ');
  }

  private buildPayload(): RetrievalQueryPayload {
    return {
      query_text: this.form.queryText.trim(),
      workspace: this.form.workspace.trim(),
      domain: this.form.domain.trim(),
      project: this.optionalValue(this.form.project),
      client: this.optionalValue(this.form.client),
      module: this.optionalValue(this.form.module),
      top_k: Number(this.form.topK) || 5
    };
  }

  private optionalValue(value: string): string | null {
    const normalized = value.trim();
    return normalized ? normalized : null;
  }

  private refreshLatestQueryLog(payload: RetrievalQueryPayload): void {
    this.queryLogApi.list(20).subscribe({
      next: (rows) => {
        this.lastQueryLog = rows.find((row) => this.matchesQueryLog(row, payload)) ?? null;
      },
      error: () => {
        this.lastQueryLog = null;
      }
    });
  }

  private matchesQueryLog(row: QueryLogEntry, payload: RetrievalQueryPayload): boolean {
    return (
      row.query_text === payload.query_text &&
      row.workspace === payload.workspace &&
      row.domain === payload.domain &&
      row.project === payload.project &&
      row.client === payload.client &&
      row.module === payload.module &&
      row.top_k === payload.top_k
    );
  }

  private formatError(error: { error?: { detail?: unknown } }): string {
    const detail = error.error?.detail;

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      return detail
        .map((item) => {
          if (typeof item === 'string') {
            return item;
          }

          if (item && typeof item === 'object' && 'msg' in item) {
            return String(item.msg);
          }

          return 'Request validation failed.';
        })
        .join(' ');
    }

    return 'Unable to complete this Ask Copilot request.';
  }
}
