import { Component } from '@angular/core';

@Component({
  selector: 'app-home-page',
  standalone: true,
  template: `
    <section class="panel">
      <h2>Phase 1 foundation</h2>
      <p>
        This shell matches the documented frontend structure and gives the repository a minimal
        Angular startup path without prematurely implementing ingestion, retrieval, or model features.
      </p>
    </section>

    <section class="card-grid" aria-label="MVP sections">
      <article class="card">
        <h3>Ingest</h3>
        <p>Manual document capture with explicit scope metadata is the first planned vertical slice.</p>
      </article>
      <article class="card">
        <h3>Store</h3>
        <p>Postgres is prepared as the metadata store while backend persistence stays intentionally thin.</p>
      </article>
      <article class="card">
        <h3>Retrieve Later</h3>
        <p>Chunking, embeddings, vector storage, and answers are reserved for later phases.</p>
      </article>
    </section>
  `,
  styles: [
    `
      .panel,
      .card {
        border: 1px solid #e4e4e7;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 18px 40px rgba(24, 24, 27, 0.06);
      }

      .panel {
        padding: 24px;
        margin-bottom: 20px;
      }

      .panel h2,
      .card h3 {
        margin-top: 0;
      }

      .panel p,
      .card p {
        margin-bottom: 0;
        color: #3f3f46;
        line-height: 1.6;
      }

      .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
      }

      .card {
        padding: 20px;
      }
    `
  ]
})
export class HomePageComponent {}
