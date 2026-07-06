
  

import { Routes } from '@angular/router';
import { HomeComponent } from './conversazioni/home/home.component';
import { LoginComponent } from './conversazioni/session/login.component';
import { SignupComponent } from './conversazioni/session/signup.component';

import { ListaBeniComponent } from './conversazioni/bene/lista-beni.component';
import { CreateBeneComponent } from './conversazioni/bene/create-bene.component';
import { RicercaBeniComponent } from './conversazioni/bene/ricerca-beni.component';
import { DettaglioBeneComponent } from './conversazioni/bene/dettaglio-bene.component';
import { CreaPrestitoComponent } from './conversazioni/prestito/crea-prestito.component';
import { ProfiloComponent } from './conversazioni/utente/profilo.component';
import { ListaUtentiComponent } from './conversazioni/utente/lista-utenti.component';
import { PreferitiComponent } from './conversazioni/utente/preferiti.component';
import { ListaPrestitiComponent } from './conversazioni/prestito/lista-prestiti.component';
import { DettaglioPrestitoComponent } from './conversazioni/prestito/dettaglio-prestito.component';
import { RecensioneBeneComponent } from './conversazioni/bene/recensione-bene.component';
import { ListaSegnalazioniComponent } from './conversazioni/segnalazione/lista-segnalazioni.component';
import { SegnalazioneComponent } from './conversazioni/segnalazione/segnalazione.component';
import { FeedbackComponent } from './conversazioni/feedback/feedback.component';
import { MessaggioComponent } from './conversazioni/messaggio/messaggio.component';
import { SuggerimentoComponent } from './conversazioni/suggerimento/suggerimento.component';
import { ListaSuggerimentiComponent } from './conversazioni/suggerimento/lista-suggerimenti.component';
import { ListaCategorieComponent } from './conversazioni/admin/lista-categorie.component';
import { CreaCategoriaComponent } from './conversazioni/admin/crea-categoria.component';


export const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'beni', component: ListaBeniComponent },
  { path: 'beni/:id', component: DettaglioBeneComponent },
  { path: 'beni/:id/richiedi-prestito', component: CreaPrestitoComponent },
  { path: 'bene/nuovo', component: CreateBeneComponent },
  { path: 'ricerca-beni', component: RicercaBeniComponent },
  { path: 'utenti', component: ListaUtentiComponent },
  { path: 'conversazioni/utente/:id', component: ProfiloComponent },
  { path: 'conversazioni/utente/:id/segnala', component: SegnalazioneComponent },
  { path: 'profilo', component: ProfiloComponent },
  { path: 'preferiti', component: PreferitiComponent },
  { path: 'prestiti', component: ListaPrestitiComponent },
  { path: 'recensione/:id', component: RecensioneBeneComponent },
  { path: 'prestiti/:id', component: DettaglioPrestitoComponent },
  { path: 'feedback/:idPrestito/:idDestinatario', component: FeedbackComponent },
  { path: 'segnalazioni', component: ListaSegnalazioniComponent },
  { path: 'suggerimento', component: SuggerimentoComponent },
  { path: 'admin/suggerimenti', component: ListaSuggerimentiComponent },
  { path: 'admin/categorie', component: ListaCategorieComponent },
  { path: 'admin/crea-categoria', component: CreaCategoriaComponent },
  { path: '**', redirectTo: 'home' }
];
