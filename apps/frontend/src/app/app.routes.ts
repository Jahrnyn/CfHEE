import { Routes } from '@angular/router';

import { HomePageComponent } from './pages/home-page.component';
import { StaticPageComponent } from './pages/static-page.component';

export const routes: Routes = [
  {
    path: '',
    component: HomePageComponent,
    title: 'Overview'
  },
  {
    path: 'inbox',
    component: StaticPageComponent,
    data: {
      title: 'Inbox / Capture',
      description: 'Manual ingest will start here with explicit workspace and domain selection.'
    }
  },
  {
    path: 'documents',
    component: StaticPageComponent,
    data: {
      title: 'Documents',
      description: 'This page will list stored documents from Postgres in the next vertical slice.'
    }
  },
  {
    path: 'ask',
    component: StaticPageComponent,
    data: {
      title: 'Ask Copilot',
      description: 'Scoped Q&A stays intentionally unimplemented until retrieval and answers land.'
    }
  },
  {
    path: 'scope-manager',
    component: StaticPageComponent,
    data: {
      title: 'Scope Manager',
      description: 'Workspaces, domains, projects, clients, and modules will be managed here.'
    }
  },
  {
    path: 'settings',
    component: StaticPageComponent,
    data: {
      title: 'Settings',
      description: 'Local runtime and project configuration will live here as the app grows.'
    }
  },
  {
    path: '**',
    redirectTo: ''
  }
];
