import { Routes } from '@angular/router';

import { AskPageComponent } from './pages/ask-page.component';
import { DocumentsPageComponent } from './pages/documents-page.component';
import { HomePageComponent } from './pages/home-page.component';
import { InboxPageComponent } from './pages/inbox-page.component';
import { StaticPageComponent } from './pages/static-page.component';

export const routes: Routes = [
  {
    path: '',
    component: HomePageComponent,
    title: 'Overview'
  },
  {
    path: 'inbox',
    component: InboxPageComponent,
    title: 'Inbox / Capture'
  },
  {
    path: 'documents',
    component: DocumentsPageComponent,
    title: 'Documents'
  },
  {
    path: 'ask',
    component: AskPageComponent,
    title: 'Ask Copilot'
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
