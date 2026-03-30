import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';

import {
  ScopeTreeApiService,
  ScopeTreeResponse,
} from '../scope-tree-api.service';

@Component({
  selector: 'app-scope-explorer-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="panel surface-panel">
      <div class="header">
        <div>
          <p class="label">Read-only scope visibility</p>
          <h2>Scope Explorer</h2>
          <p class="intro">
            Inspect the stored hard-scope hierarchy as it currently exists in CfHEE. This page is
            read-only and does not infer, plan, or edit scope.
          </p>
        </div>

        <div class="actions">
          <button type="button" (click)="loadScopeTree()" [disabled]="isLoading">
            {{ isLoading ? 'Refreshing...' : 'Refresh tree' }}
          </button>
          <button
            type="button"
            class="secondary-button"
            (click)="downloadJson()"
            [disabled]="!scopeTree"
          >
            Download JSON
          </button>
        </div>
      </div>

      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>

      <div *ngIf="isLoading && !scopeTree" class="status">Loading scope tree...</div>

      <section *ngIf="scopeTree && scopeTree.workspaces.length === 0" class="empty-state surface-card">
        <h3 class="empty-title">No stored scopes yet</h3>
        <p class="empty-copy">
          The current backend returned an empty scope tree. Ingest a document first to create stored
          scope combinations.
        </p>
      </section>

      <section *ngIf="scopeTree && scopeTree.workspaces.length > 0" class="tree-shell">
        <div class="tree-summary surface-card">
          <p class="summary-label">Current shape</p>
          <p class="summary-copy">
            {{ scopeTree.workspaces.length }} workspace{{ scopeTree.workspaces.length === 1 ? '' : 's' }}
            currently visible through the stored scope tree.
          </p>
        </div>

        <div class="workspace-list">
          <article *ngFor="let workspace of scopeTree.workspaces" class="workspace-card surface-card">
            <details class="tree-group tree-group-workspace">
              <summary class="tree-node tree-node-summary">
                <span class="node-type">Workspace</span>
                <span class="node-name">{{ workspace.name }}</span>
                <span class="node-meta">{{ workspace.domains.length }} domain{{ workspace.domains.length === 1 ? '' : 's' }}</span>
              </summary>

              <div *ngIf="workspace.domains.length === 0" class="empty-branch">
                No stored domains under this workspace.
              </div>

              <ul *ngIf="workspace.domains.length > 0" class="tree-list tree-list-root">
                <li *ngFor="let domain of workspace.domains" class="tree-item">
                  <details class="tree-group">
                    <summary class="tree-node tree-node-summary">
                      <span class="node-type">Domain</span>
                      <span class="node-name">{{ domain.name }}</span>
                      <span class="node-meta">{{ domain.projects.length }} project{{ domain.projects.length === 1 ? '' : 's' }}</span>
                    </summary>

                    <div *ngIf="domain.projects.length === 0" class="empty-branch empty-branch-nested">
                      No stored projects under this domain.
                    </div>

                    <ul *ngIf="domain.projects.length > 0" class="tree-list">
                      <li *ngFor="let project of domain.projects" class="tree-item">
                        <details class="tree-group">
                          <summary class="tree-node tree-node-summary">
                            <span class="node-type">Project</span>
                            <span class="node-name">{{ project.name }}</span>
                            <span class="node-meta">{{ project.clients.length }} client{{ project.clients.length === 1 ? '' : 's' }}</span>
                          </summary>

                          <div *ngIf="project.clients.length === 0" class="empty-branch empty-branch-nested">
                            No stored clients under this project.
                          </div>

                          <ul *ngIf="project.clients.length > 0" class="tree-list">
                            <li *ngFor="let client of project.clients" class="tree-item">
                              <details class="tree-group">
                                <summary class="tree-node tree-node-summary">
                                  <span class="node-type">Client</span>
                                  <span class="node-name">{{ client.name }}</span>
                                  <span class="node-meta">{{ client.modules.length }} module{{ client.modules.length === 1 ? '' : 's' }}</span>
                                </summary>

                                <div *ngIf="client.modules.length === 0" class="empty-branch empty-branch-nested">
                                  No stored modules under this client.
                                </div>

                                <ul *ngIf="client.modules.length > 0" class="tree-list">
                                  <li *ngFor="let module of client.modules" class="tree-item">
                                    <div class="tree-node tree-node-leaf">
                                      <span class="node-type">Module</span>
                                      <span class="node-name">{{ module.name }}</span>
                                    </div>
                                  </li>
                                </ul>
                              </details>
                            </li>
                          </ul>
                        </details>
                      </li>
                    </ul>
                  </details>
                </li>
              </ul>
            </details>
          </article>
        </div>
      </section>
    </section>
  `,
  styles: [
    `
      .header {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 24px;
      }

      .label,
      .summary-label,
      .node-label {
        margin: 0 0 8px;
        color: var(--warning);
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
      .summary-copy,
      .empty-copy,
      .empty-branch {
        color: var(--text-muted);
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
        font: inherit;
        cursor: pointer;
      }

      button:disabled {
        cursor: default;
        opacity: 0.7;
      }

      .error,
      .status {
        margin-bottom: 16px;
        padding: 12px 14px;
        border-radius: 14px;
      }

      .empty-state {
        margin-bottom: 20px;
      }

      .empty-title {
        margin-bottom: 8px;
      }

      .empty-copy {
        margin: 0;
      }

      .tree-shell {
        display: grid;
        gap: 20px;
      }

      .tree-summary,
      .workspace-card {
        padding: 18px;
      }

      .summary-copy,
      .node-label {
        margin-bottom: 0;
      }

      .workspace-list {
        display: grid;
        gap: 16px;
      }

      .tree-list {
        list-style: none;
        margin: 14px 0 0;
        padding-left: 18px;
        border-left: 1px solid var(--border);
      }

      .tree-list-root {
        padding-left: 0;
        border-left: 0;
      }

      .tree-item + .tree-item {
        margin-top: 14px;
      }

      .tree-node {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        padding: 10px 12px;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: var(--bg-soft);
      }

      .tree-node-summary {
        width: 100%;
        cursor: pointer;
        list-style: none;
      }

      .tree-node-summary::-webkit-details-marker {
        display: none;
      }

      .tree-group > summary::before {
        content: '▸';
        color: var(--text-muted);
        font-size: 0.85rem;
        line-height: 1;
        transition: transform 150ms ease;
      }

      .tree-group[open] > summary::before {
        transform: rotate(90deg);
      }

      .tree-node-leaf {
        background: var(--accent-soft);
        border-color: rgba(77, 182, 172, 0.35);
      }

      .node-type {
        color: var(--warning);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      .node-name {
        color: var(--text);
        font-weight: 600;
      }

      .node-meta {
        margin-left: auto;
        color: var(--text-soft);
        font-size: 0.85rem;
      }

      .empty-branch {
        margin-top: 10px;
        padding-left: 12px;
      }

      .empty-branch-nested {
        margin-left: 4px;
      }
    `
  ]
})
export class ScopeExplorerPageComponent implements OnInit {
  private readonly scopeTreeApi = inject(ScopeTreeApiService);

  protected scopeTree: ScopeTreeResponse | null = null;
  protected isLoading = false;
  protected errorMessage = '';

  ngOnInit(): void {
    this.loadScopeTree();
  }

  protected loadScopeTree(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.scopeTreeApi.getScopeTree().subscribe({
      next: (scopeTree) => {
        this.scopeTree = scopeTree;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Unable to load the current stored scope hierarchy from the backend.';
        this.isLoading = false;
      }
    });
  }

  protected downloadJson(): void {
    if (!this.scopeTree) {
      return;
    }

    const payload = JSON.stringify(this.scopeTree, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const objectUrl = URL.createObjectURL(blob);
    const timestamp = this.formatTimestampForFilename(new Date());
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = `scope-tree-${timestamp}.json`;
    anchor.click();
    URL.revokeObjectURL(objectUrl);
  }

  private formatTimestampForFilename(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}${month}${day}-${hours}${minutes}${seconds}`;
  }
}
