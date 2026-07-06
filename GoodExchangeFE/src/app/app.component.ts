import { Component, OnInit, OnDestroy } from '@angular/core';
// Router = servizio per navigare tra le pagine dell'app
// RouterOutlet = direttiva che indica dove visualizzare i componenti
// RouterModule = modulo che abilita il routing nell'app
import { Router, RouterOutlet, RouterModule } from '@angular/router';
// Per ngIf nfFor
import { CommonModule } from '@angular/common';
// Modulo per la gestione delle form
import { FormsModule } from '@angular/forms';
// Modulo per la "sottoscrizione" agli Observable
// OSS Iscriversi agli observable (oggetti restituiti dalle chiamate http) permette
// di ricevere aggiornamenti in tempo reale sui dati
import { Subscription } from 'rxjs';

import { Utente } from './modelli/utente.model';
import { Bene } from './modelli/bene.model';
import { SessionService } from './servizi/session.service';
import { BeneService } from './servizi/bene.service';
import { UtenteService } from './servizi/utente.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterModule, CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'GoodExchangeFE';

  // variabili gestione utente
  loggedUser: Utente | null = null;
  isAdmin: boolean = false;
  isClient: boolean = false;

  // variabili per la barra di ricerca utenti
  searchUtenti: string = '';

  // risultati ricerca utenti
  utentiTrovati: Utente[] = [];

  private userSubscription?: Subscription;
  private beniSubscription?: Subscription;
  private utentiSubscription?: Subscription;

  constructor(
    private sessionService: SessionService,
    private beneService: BeneService,
    private utenteService: UtenteService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.userSubscription = this.sessionService.utenteLoggato$.subscribe(user => {
      this.loggedUser = user;
      this.isAdmin = user?.ruolo === 'admin';
      this.isClient = user?.ruolo === 'utente';
    });
  }

  ngOnDestroy(): void {
    this.userSubscription?.unsubscribe();
  }


  cercaUtenti(): void {
    if (this.searchUtenti.trim()) {
      // Usa il servizio UtenteService per cercare utenti
      this.utentiSubscription?.unsubscribe();
      this.utentiSubscription = this.utenteService.getUtenti({ search: this.searchUtenti.trim() })
        .subscribe(utenti => {
          this.utentiTrovati = utenti;
        });
      this.searchUtenti = '';
    }
  }

  logout(): void {
    this.sessionService.clearLoggedUser();
    this.router.navigate(['/home']);
  }

  get isUtenteLogged(): boolean {
    return this.loggedUser !== null;
  }
}
