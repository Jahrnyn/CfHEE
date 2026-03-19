import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { DocumentPayload, DocumentsApiService } from '../documents-api.service';

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
export class InboxPageComponent {
  private readonly documentsApi = inject(DocumentsApiService);

  protected isSubmitting = false;
  protected successMessage = '';
  protected errorMessage = '';
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

  protected submit(): void {
    this.isSubmitting = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.documentsApi.createDocument(this.buildPayload()).subscribe({
      next: (document) => {
        this.isSubmitting = false;
        this.successMessage = `Saved document #${document.id}: ${document.title}`;
        this.form.title = '';
        this.form.rawText = '';
        this.form.sourceRef = '';
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage = error.error?.detail ?? 'Unable to save the document.';
      }
    });
  }

  private buildPayload(): DocumentPayload {
    return {
      workspace: this.form.workspace.trim(),
      domain: this.form.domain.trim(),
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
    const normalized = value.trim();
    return normalized ? normalized : null;
  }
}
