import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { DocumentPayload, DocumentsApiService } from '../documents-api.service';
import { ScopeValuesApiService, ScopeValuesResponse } from '../scope-values-api.service';

@Component({
  selector: 'app-inbox-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <section class="panel">
      <p class="label">Manual ingest</p>
      <h2>Inbox / Capture</h2>
      <p class="intro">
        Submit pasted text with explicit scope metadata. Workspace and domain are required, and
        lower scope levels stay optional.
      </p>

      <form class="document-form" (ngSubmit)="submit()" #documentForm="ngForm">
        <div class="field-grid">
          <label>
            <span>Workspace</span>
            <input
              [(ngModel)]="form.workspace"
              (ngModelChange)="onWorkspaceChange()"
              list="workspace-options"
              name="workspace"
              required
            />
            <datalist id="workspace-options">
              <option *ngFor="let option of scopeOptions.workspaces" [value]="option"></option>
            </datalist>
            <small *ngIf="closeMatch('workspaces') as match" class="hint">
              Existing close match: {{ match }}
            </small>
          </label>

          <label>
            <span>Domain</span>
            <input
              [(ngModel)]="form.domain"
              (ngModelChange)="onDomainChange()"
              list="domain-options"
              name="domain"
              required
            />
            <datalist id="domain-options">
              <option *ngFor="let option of scopeOptions.domains" [value]="option"></option>
            </datalist>
            <small *ngIf="closeMatch('domains') as match" class="hint">
              Existing close match: {{ match }}
            </small>
          </label>

          <label>
            <span>Project</span>
            <input
              [(ngModel)]="form.project"
              (ngModelChange)="onProjectChange()"
              list="project-options"
              name="project"
            />
            <datalist id="project-options">
              <option *ngFor="let option of scopeOptions.projects" [value]="option"></option>
            </datalist>
            <small *ngIf="closeMatch('projects') as match" class="hint">
              Existing close match: {{ match }}
            </small>
          </label>

          <label>
            <span>Client</span>
            <input
              [(ngModel)]="form.client"
              (ngModelChange)="onClientChange()"
              list="client-options"
              name="client"
            />
            <datalist id="client-options">
              <option *ngFor="let option of scopeOptions.clients" [value]="option"></option>
            </datalist>
            <small *ngIf="closeMatch('clients') as match" class="hint">
              Existing close match: {{ match }}
            </small>
          </label>

          <label>
            <span>Module</span>
            <input [(ngModel)]="form.module" list="module-options" name="module" />
            <datalist id="module-options">
              <option *ngFor="let option of scopeOptions.modules" [value]="option"></option>
            </datalist>
            <small *ngIf="closeMatch('modules') as match" class="hint">
              Existing close match: {{ match }}
            </small>
          </label>

          <label>
            <span>Source type</span>
            <input [(ngModel)]="form.sourceType" name="sourceType" required />
          </label>

          <label>
            <span>Language</span>
            <input [(ngModel)]="form.language" name="language" />
          </label>

          <label>
            <span>Source ref</span>
            <input [(ngModel)]="form.sourceRef" name="sourceRef" />
          </label>
        </div>

        <label>
          <span>Title</span>
          <input [(ngModel)]="form.title" name="title" required />
        </label>

        <label>
          <span>Raw text</span>
          <textarea [(ngModel)]="form.rawText" name="rawText" rows="12" required></textarea>
        </label>

        <div class="actions">
          <button type="submit" [disabled]="isSubmitting || documentForm.invalid">Save document</button>
          <a routerLink="/documents">View stored documents</a>
        </div>
      </form>

      <p *ngIf="successMessage" class="success">{{ successMessage }}</p>
      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>
      <p *ngIf="isLoadingScopeValues" class="status">Refreshing saved scope values...</p>
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

      h2 {
        margin: 0 0 12px;
      }

      .intro {
        margin: 0 0 24px;
        color: #3f3f46;
        line-height: 1.6;
      }

      .document-form {
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

      .hint {
        color: #a1a1aa;
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
        align-items: center;
      }

      button,
      a {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        padding: 0 16px;
        border-radius: 999px;
        font: inherit;
      }

      button {
        border: 0;
        color: #fff;
        background: #0f766e;
        cursor: pointer;
      }

      button:disabled {
        cursor: default;
        opacity: 0.7;
      }

      a {
        color: #18181b;
        text-decoration: none;
        border: 1px solid #d4d4d8;
        background: #fff;
      }

      .success,
      .error {
        margin: 0;
        padding: 12px 14px;
        border-radius: 14px;
      }

      .success {
        color: #166534;
        background: #dcfce7;
      }

      .error {
        color: #991b1b;
        background: #fee2e2;
      }
    `
  ]
})
export class InboxPageComponent implements OnInit {
  private readonly documentsApi = inject(DocumentsApiService);
  private readonly scopeValuesApi = inject(ScopeValuesApiService);

  protected isSubmitting = false;
  protected isLoadingScopeValues = false;
  protected successMessage = '';
  protected errorMessage = '';
  protected scopeOptions: ScopeValuesResponse = {
    workspaces: [],
    domains: [],
    projects: [],
    clients: [],
    modules: []
  };
  protected form = {
    workspace: '',
    domain: '',
    project: '',
    client: '',
    module: '',
    sourceType: 'pasted_text',
    title: '',
    rawText: '',
    language: '',
    sourceRef: ''
  };

  ngOnInit(): void {
    this.refreshScopeValues();
  }

  protected submit(): void {
    this.isSubmitting = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.documentsApi.createDocument(this.buildPayload()).subscribe({
      next: (document) => {
        this.isSubmitting = false;
        this.successMessage = `Saved document #${document.id}: ${document.title}`;
        this.form.workspace = document.workspace;
        this.form.domain = document.domain;
        this.form.project = document.project ?? '';
        this.form.client = document.client ?? '';
        this.form.module = document.module ?? '';
        this.form.title = '';
        this.form.rawText = '';
        this.form.sourceRef = '';
        this.refreshScopeValues();
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage = error.error?.detail ?? 'Unable to save the document.';
      }
    });
  }

  protected onWorkspaceChange(): void {
    this.refreshScopeValues();
  }

  protected onDomainChange(): void {
    this.refreshScopeValues();
  }

  protected onProjectChange(): void {
    this.refreshScopeValues();
  }

  protected onClientChange(): void {
    this.refreshScopeValues();
  }

  protected closeMatch(field: keyof ScopeValuesResponse): string | null {
    const currentValue = this.currentScopeValue(field);
    const normalizedValue = this.normalizeValue(currentValue);
    if (!normalizedValue) {
      return null;
    }

    const exactMatch = this.scopeOptions[field].find(
      (option) => this.normalizeValue(option) === normalizedValue
    );
    if (exactMatch) {
      return null;
    }

    let bestMatch: string | null = null;
    let bestDistance = Number.POSITIVE_INFINITY;

    for (const option of this.scopeOptions[field]) {
      const distance = this.levenshteinDistance(normalizedValue, this.normalizeValue(option));
      if (distance < bestDistance) {
        bestDistance = distance;
        bestMatch = option;
      }
    }

    if (!bestMatch || bestDistance > 2) {
      return null;
    }

    return bestMatch;
  }

  private buildPayload(): DocumentPayload {
    return {
      workspace: this.normalizeValue(this.form.workspace),
      domain: this.normalizeValue(this.form.domain),
      project: this.optionalValue(this.form.project),
      client: this.optionalValue(this.form.client),
      module: this.optionalValue(this.form.module),
      source_type: this.form.sourceType.trim(),
      title: this.form.title.trim(),
      raw_text: this.form.rawText.trim(),
      language: this.optionalValue(this.form.language),
      source_ref: this.optionalValue(this.form.sourceRef)
    };
  }

  private optionalValue(value: string): string | null {
    const normalized = this.normalizeValue(value);
    return normalized ? normalized : null;
  }

  private refreshScopeValues(): void {
    this.isLoadingScopeValues = true;

    this.scopeValuesApi
      .listScopeValues({
        workspace: this.form.workspace,
        domain: this.form.domain,
        project: this.form.project,
        client: this.form.client
      })
      .subscribe({
        next: (response) => {
          this.isLoadingScopeValues = false;
          this.scopeOptions = response;
        },
        error: () => {
          this.isLoadingScopeValues = false;
        }
      });
  }

  private currentScopeValue(field: keyof ScopeValuesResponse): string {
    switch (field) {
      case 'workspaces':
        return this.form.workspace;
      case 'domains':
        return this.form.domain;
      case 'projects':
        return this.form.project;
      case 'clients':
        return this.form.client;
      case 'modules':
        return this.form.module;
    }
  }

  private normalizeValue(value: string): string {
    return value.trim().replace(/\s+/g, ' ');
  }

  private levenshteinDistance(left: string, right: string): number {
    if (left === right) {
      return 0;
    }

    if (!left.length) {
      return right.length;
    }

    if (!right.length) {
      return left.length;
    }

    const previous = Array.from({ length: right.length + 1 }, (_, index) => index);
    const current = new Array<number>(right.length + 1).fill(0);

    for (let leftIndex = 0; leftIndex < left.length; leftIndex += 1) {
      current[0] = leftIndex + 1;

      for (let rightIndex = 0; rightIndex < right.length; rightIndex += 1) {
        const substitutionCost = left[leftIndex] === right[rightIndex] ? 0 : 1;
        current[rightIndex + 1] = Math.min(
          current[rightIndex] + 1,
          previous[rightIndex + 1] + 1,
          previous[rightIndex] + substitutionCost
        );
      }

      for (let index = 0; index < previous.length; index += 1) {
        previous[index] = current[index];
      }
    }

    return previous[right.length];
  }
}
