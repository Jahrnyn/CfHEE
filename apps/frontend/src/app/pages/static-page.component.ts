import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-static-page',
  standalone: true,
  template: `
    <section class="panel">
      <p class="label">Planned view</p>
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
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
        margin-top: 0;
      }

      p:last-child {
        margin-bottom: 0;
        color: #3f3f46;
        line-height: 1.6;
      }
    `
  ]
})
export class StaticPageComponent {
  private readonly route = inject(ActivatedRoute);

  get title(): string {
    return this.route.snapshot.data['title'] as string;
  }

  get description(): string {
    return this.route.snapshot.data['description'] as string;
  }
}
