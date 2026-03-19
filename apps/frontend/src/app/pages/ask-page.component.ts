import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

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
        This first slice is retrieval-only. Workspace and domain are required so results stay
        scoped by default and do not mix unrelated content.
      </p>

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
            <span>Result limit</span>
            <input [(ngModel)]="form.limit" name="limit" type="number" min="1" max="20" />
          </label>
        </div>

        <div class="actions">
          <button type="submit" [disabled]="isSubmitting || queryForm.invalid">Retrieve chunks</button>
        </div>
      </form>

      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>

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
          <p class="meta">{{ lastResponse.results.length }} result(s)</p>
        </div>

        <p *ngIf="lastResponse.results.length === 0" class="empty">
          No chunks matched this scoped query.
        </p>

        <article class="result-card" *ngFor="let result of lastResponse.results">
          <div class="card-header">
            <h4>#{{ result.rank }} - {{ result.document.title }}</h4>
            <p *ngIf="result.distance !== null">Distance: {{ result.distance | number: '1.3-3' }}</p>
          </div>

          <p class="meta">
            <strong>Scope:</strong>
            {{ result.scope.workspace }} / {{ result.scope.domain }}
            <ng-container *ngIf="result.scope.project"> / {{ result.scope.project }}</ng-container>
            <ng-container *ngIf="result.scope.client"> / {{ result.scope.client }}</ng-container>
            <ng-container *ngIf="result.scope.module"> / {{ result.scope.module }}</ng-container>
          </p>
          <p class="meta"><strong>Document ID:</strong> {{ result.document_id }}</p>
          <p class="meta"><strong>Chunk:</strong> {{ result.chunk_index + 1 }} ({{ result.char_count }} chars)</p>
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

      .error {
        margin: 16px 0 0;
        padding: 12px 14px;
        border-radius: 14px;
        color: #991b1b;
        background: #fee2e2;
      }

      .results {
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
  private readonly retrievalApi = inject(RetrievalApiService);

  protected isSubmitting = false;
  protected errorMessage = '';
  protected lastResponse: RetrievalQueryResponse | null = null;
  protected form = {
    queryText: '',
    workspace: '',
    domain: '',
    project: '',
    client: '',
    module: '',
    limit: 5
  };

  protected submit(): void {
    this.isSubmitting = true;
    this.errorMessage = '';

    this.retrievalApi.query(this.buildPayload()).subscribe({
      next: (response) => {
        this.lastResponse = response;
        this.isSubmitting = false;
      },
      error: (error) => {
        this.errorMessage = error.error?.detail ?? 'Unable to retrieve chunks for this scoped query.';
        this.isSubmitting = false;
      }
    });
  }

  private buildPayload(): RetrievalQueryPayload {
    return {
      query_text: this.form.queryText.trim(),
      workspace: this.form.workspace.trim(),
      domain: this.form.domain.trim(),
      project: this.optionalValue(this.form.project),
      client: this.optionalValue(this.form.client),
      module: this.optionalValue(this.form.module),
      limit: Number(this.form.limit) || 5
    };
  }

  private optionalValue(value: string): string | null {
    const normalized = value.trim();
    return normalized ? normalized : null;
  }
}
