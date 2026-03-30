import { CommonModule, DatePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ChunkSummary, DocumentSummary, DocumentsApiService } from '../documents-api.service';

@Component({
  selector: 'app-documents-page',
  standalone: true,
  imports: [CommonModule, DatePipe, RouterLink],
  template: `
    <section class="panel">
      <div class="header">
        <div>
          <p class="label">Stored documents</p>
          <h2>Documents</h2>
          <p class="intro">Documents are listed directly from Postgres through the FastAPI backend.</p>
        </div>

        <div class="actions">
          <a routerLink="/inbox">Add document</a>
          <button type="button" (click)="loadDocuments()" [disabled]="isLoading">Refresh</button>
        </div>
      </div>

      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>
      <p *ngIf="successMessage" class="success">{{ successMessage }}</p>

      <p *ngIf="!isLoading && documents.length === 0" class="empty">
        No documents stored yet. Add the first one from Inbox / Capture.
      </p>

      <div class="documents" *ngIf="documents.length > 0">
        <article class="card" *ngFor="let document of documents">
          <div class="card-header">
            <h3>{{ document.title }}</h3>
            <p>{{ document.created_at | date: 'medium' }}</p>
          </div>

          <p class="meta">
            <strong>Scope:</strong>
            {{ document.workspace }} / {{ document.domain }}
            <ng-container *ngIf="document.project"> / {{ document.project }}</ng-container>
            <ng-container *ngIf="document.client"> / {{ document.client }}</ng-container>
            <ng-container *ngIf="document.module"> / {{ document.module }}</ng-container>
          </p>

          <p class="meta"><strong>Source type:</strong> {{ document.source_type }}</p>
          <p class="meta" *ngIf="document.language"><strong>Language:</strong> {{ document.language }}</p>
          <p class="meta" *ngIf="document.source_ref"><strong>Source ref:</strong> {{ document.source_ref }}</p>
          <p class="preview">{{ document.raw_text_preview }}</p>

          <div class="chunk-actions">
            <button type="button" (click)="toggleChunks(document.id)">
              {{ expandedDocumentId === document.id ? 'Hide chunks' : 'Inspect chunks' }}
            </button>
            <button
              type="button"
              class="danger-button"
              (click)="confirmDelete(document)"
              [disabled]="deletingDocumentId === document.id"
            >
              {{ deletingDocumentId === document.id ? 'Deleting...' : 'Delete' }}
            </button>
          </div>

          <div class="chunks" *ngIf="expandedDocumentId === document.id">
            <p class="meta" *ngIf="chunkErrorMessage">{{ chunkErrorMessage }}</p>
            <p class="meta" *ngIf="!chunkErrorMessage && isLoadingChunks">Loading chunks...</p>

            <div *ngIf="!isLoadingChunks && documentChunks.length > 0">
              <article class="chunk-card" *ngFor="let chunk of documentChunks">
                <p class="chunk-meta">
                  <strong>Chunk {{ chunk.chunk_index + 1 }}</strong>
                  - {{ chunk.char_count }} chars
                </p>
                <p class="chunk-text">{{ chunk.text }}</p>
              </article>
            </div>

            <p class="meta" *ngIf="!isLoadingChunks && !chunkErrorMessage && documentChunks.length === 0">
              No chunks were generated for this document.
            </p>
          </div>
        </article>
      </div>
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

      .header {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 24px;
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
      h3 {
        margin-top: 0;
      }

      .intro,
      .meta,
      .preview,
      .empty {
        color: #3f3f46;
        line-height: 1.6;
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
      }

      a,
      button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        padding: 0 16px;
        border-radius: 999px;
        font: inherit;
      }

      a {
        color: #18181b;
        text-decoration: none;
        border: 1px solid #d4d4d8;
        background: #fff;
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

      .documents {
        display: grid;
        gap: 16px;
      }

      .card {
        padding: 20px;
        border: 1px solid #e4e4e7;
        border-radius: 18px;
        background: #fff;
      }

      .card-header {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: space-between;
        align-items: baseline;
      }

      .card-header p {
        margin: 0;
        color: #71717a;
      }

      .meta {
        margin: 8px 0 0;
      }

      .preview {
        margin: 16px 0 0;
        padding-top: 16px;
        border-top: 1px solid #e4e4e7;
        white-space: pre-wrap;
      }

      .chunk-actions {
        margin-top: 16px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
      }

      .chunks {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px dashed #d4d4d8;
      }

      .chunk-card {
        padding: 14px 16px;
        border: 1px solid #e4e4e7;
        border-radius: 14px;
        background: #fafafa;
      }

      .chunk-card + .chunk-card {
        margin-top: 12px;
      }

      .chunk-meta {
        margin: 0 0 10px;
        color: #52525b;
      }

      .chunk-text {
        margin: 0;
        color: #18181b;
        line-height: 1.6;
        white-space: pre-wrap;
      }

      .error {
        margin: 0 0 16px;
        padding: 12px 14px;
        border-radius: 14px;
        color: #991b1b;
        background: #fee2e2;
      }

      .success {
        margin: 0 0 16px;
        padding: 12px 14px;
        border-radius: 14px;
        color: #065f46;
        background: #d1fae5;
      }

      .danger-button {
        color: var(--error-text) !important;
        background: linear-gradient(180deg, #8f1d2c 0%, #6f1622 100%) !important;
        border: 1px solid rgba(255, 180, 191, 0.3) !important;
        box-shadow: 0 10px 22px rgba(111, 22, 34, 0.28);
      }

      .danger-button:not(:disabled):hover,
      .danger-button:not(:disabled):focus-visible {
        background: linear-gradient(180deg, #a32133 0%, #7b1926 100%) !important;
        border-color: rgba(255, 180, 191, 0.42) !important;
        box-shadow: 0 12px 26px rgba(111, 22, 34, 0.34) !important;
      }

      .danger-button:not(:disabled):focus-visible {
        outline: 2px solid rgba(255, 180, 191, 0.36);
        outline-offset: 2px;
      }
    `
  ]
})
export class DocumentsPageComponent implements OnInit {
  private readonly documentsApi = inject(DocumentsApiService);

  protected documents: DocumentSummary[] = [];
  protected documentChunks: ChunkSummary[] = [];
  protected expandedDocumentId: number | null = null;
  protected errorMessage = '';
  protected successMessage = '';
  protected chunkErrorMessage = '';
  protected deletingDocumentId: number | null = null;
  protected isLoading = false;
  protected isLoadingChunks = false;

  ngOnInit(): void {
    this.loadDocuments();
  }

  protected loadDocuments(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.documentsApi.listDocuments().subscribe({
      next: (documents) => {
        this.documents = documents;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Unable to load documents from the backend.';
        this.isLoading = false;
      }
    });
  }

  protected confirmDelete(document: DocumentSummary): void {
    const confirmed = window.confirm(`Delete "${document.title}" and its stored chunks and vectors?`);
    if (!confirmed) {
      return;
    }

    this.deletingDocumentId = document.id;
    this.errorMessage = '';
    this.successMessage = '';

    this.documentsApi.deleteDocument(document.id).subscribe({
      next: (result) => {
        if (this.expandedDocumentId === document.id) {
          this.expandedDocumentId = null;
          this.documentChunks = [];
          this.chunkErrorMessage = '';
        }

        this.successMessage = `Deleted document ${result.document_id} and ${result.deleted_chunk_count} chunk(s).`;
        this.deletingDocumentId = null;
        this.loadDocuments();
      },
      error: (error) => {
        this.errorMessage =
          error?.status === 404
            ? `Document ${document.id} was already removed.`
            : 'Unable to delete the selected document.';
        this.deletingDocumentId = null;
      }
    });
  }

  protected toggleChunks(documentId: number): void {
    if (this.expandedDocumentId === documentId) {
      this.expandedDocumentId = null;
      this.documentChunks = [];
      this.chunkErrorMessage = '';
      return;
    }

    this.expandedDocumentId = documentId;
    this.isLoadingChunks = true;
    this.chunkErrorMessage = '';
    this.documentChunks = [];

    this.documentsApi.listDocumentChunks(documentId).subscribe({
      next: (chunks) => {
        this.documentChunks = chunks;
        this.isLoadingChunks = false;
      },
      error: () => {
        this.chunkErrorMessage = 'Unable to load chunks for this document.';
        this.isLoadingChunks = false;
      }
    });
  }
}
