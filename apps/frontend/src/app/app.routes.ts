import { Routes } from '@angular/router';

import { AskPageComponent } from './pages/ask-page.component';
import { DocumentsPageComponent } from './pages/documents-page.component';
import { HomePageComponent } from './pages/home-page.component';
import { InboxPageComponent } from './pages/inbox-page.component';
import { OperationsPageComponent } from './pages/operations-page.component';
import { ScopeExplorerPageComponent } from './pages/scope-explorer-page.component';

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
    path: 'scopes',
    component: ScopeExplorerPageComponent,
    title: 'Scope Explorer'
  },
  {
    path: 'ask',
    component: AskPageComponent,
    title: 'Ask'
  },
  {
    path: 'operations',
    component: OperationsPageComponent,
    title: 'Operations / Admin'
  },
  {
    path: '**',
    redirectTo: ''
  }
];
