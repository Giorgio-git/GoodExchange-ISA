import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SegnalazioneService } from '../../servizi/segnalazione.service';
import { Segnalazione } from '../../modelli/segnalazione.model';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Messaggio } from '../../modelli/messaggio.model';
import { UtenteService } from '../../servizi/utente.service';
import { Utente } from '../../modelli/utente.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-lista-segnalazioni',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-segnalazioni.component.html',
  styleUrls: ['./lista-segnalazioni.component.css']
})
export class ListaSegnalazioniComponent implements OnInit {
  segnalazioni: Segnalazione[] = [];
  messaggi: { [idSegnalazione: number]: Messaggio | null } = {};
  utentiMap: { [id: number]: Utente | undefined } = {};
  loading = true;
  errore = '';

  constructor(
    private segnalazioneService: SegnalazioneService,
    private messaggioService: MessaggioService,
    private utenteService: UtenteService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Carica subito la mappa degli utenti
    this.utenteService.getUtenti().subscribe({
      next: (utenti) => {
        utenti.forEach(u => {
          if (u.id !== undefined) {
            this.utentiMap[u.id] = u;
          }
        });
      },
      error: () => {}
    });

    this.segnalazioneService.getSegnalazioni().subscribe({
      next: segnalazioni => {
        this.segnalazioni = segnalazioni.sort((a, b) => (a.id || 0) - (b.id || 0));
        // Carica i messaggi e verifica gli utenti associati
        segnalazioni.forEach(s => {
          if (s.id !== undefined) {
            this.messaggioService.getMessaggiByTipo('segnalazione', s.id).subscribe({
              next: messaggi => {
                this.messaggi[s.id!] = messaggi.length > 0 ? messaggi[0] : null;
              },
              error: () => {
                this.messaggi[s.id!] = null;
              }
            });
          }
          if (s.id_segnalante && !this.utentiMap[s.id_segnalante]) {
            this.utenteService.getUtenteById(s.id_segnalante).subscribe({
              next: u => { this.utentiMap[s.id_segnalante] = u; },
              error: () => {}
            });
          }
          if (s.id_segnalato && !this.utentiMap[s.id_segnalato]) {
            this.utenteService.getUtenteById(s.id_segnalato).subscribe({
              next: u => { if (s.id_segnalato) this.utentiMap[s.id_segnalato] = u; },
              error: () => {}
            });
          }
        });
        this.loading = false;
      },
      error: (err) => {
        this.errore = err.error?.detail || err.error?.errore || 'Errore nel caricamento delle segnalazioni.';
        this.loading = false;
      }
    });
  }

  vaiAProfilo(idUtente: number) {
    if (idUtente) {
      this.router.navigate(['/conversazioni/utente', idUtente]);
    }
  }

  // Azione amministratore: cambia stato segnalazione
  aggiornaStato(id: number, nuovoStato: string) {
    this.segnalazioneService.aggiornaStatoSegnalazione(id, nuovoStato).subscribe({
      next: () => {
        // Aggiorna localmente lo stato
        const segnalazione = this.segnalazioni.find(s => s.id === id);
        if (segnalazione) 
          segnalazione.stato = nuovoStato as 'aperta' | 'in_gestione' | 'risolta' | 'respinta';
      },
      error: (err) => {
        this.errore = err.error?.detail || err.error?.errore || 'Errore nell’aggiornamento dello stato.';
      }
    });
  }
}
