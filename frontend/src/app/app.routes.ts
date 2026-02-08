import { Routes } from '@angular/router';
import { PrinterListComponent } from './components/printer-list/printer-list.component';
import { Settings } from './components/settings/settings';

export const routes: Routes = [
    { path: '', component: PrinterListComponent },
    { path: 'settings', component: Settings },
    { path: '**', redirectTo: '' }
];
