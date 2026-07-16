import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SuggerimentoService } from '../../servizi/suggerimento.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { UtenteService } from '../../servizi/utente.service';
import { Suggerimento } from '../../modelli/suggerimento.model';
import { Messaggio } from '../../modelli/messaggio.model';
import { Utente } from '../../modelli/utente.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-lista-suggerimenti',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lista-suggerimenti.component.html',
  styleUrls: ['./lista-suggerimenti.component.css']
})
export class ListaSuggerimentiComponent implements OnInit {
  suggerimentiRichiesti: Suggerimento[] = [];
  suggerimentiCompletati: Suggerimento[] = [];
  messaggi: { [id: number]: Messaggio[] } = {};
  utentiMap: { [id: number]: Utente | undefined } = {};
  loading = true;
  errore = '';

  constructor(
    private suggerimentoService: SuggerimentoService,
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

    this.suggerimentoService.getAll().subscribe({
      next: suggerimenti => {
        this.suggerimentiRichiesti = suggerimenti.filter(s => s.stato === 'richiesto').sort((a, b) => a.id! - b.id!);
        this.suggerimentiCompletati = suggerimenti.filter(s => s.stato === 'completato').sort((a, b) => a.id! - b.id!);
        this.loading = false;
        // Carica i messaggi per ogni suggerimento
        [...this.suggerimentiRichiesti, ...this.suggerimentiCompletati].forEach(s => {
          this.messaggioService.getMessaggiByTipo('suggerimento', s.id!).subscribe((msgs: Messaggio[]) => {
            if (s.id !== undefined) {
              this.messaggi[s.id!] = msgs || [];
              if (msgs && msgs.length > 0 && msgs[0].id_mittente) {
                const idMittente = msgs[0].id_mittente;
                if (!this.utentiMap[idMittente]) {
                  this.utenteService.getUtenteById(idMittente).subscribe({
                    next: (u: Utente) => {
                      this.utentiMap[idMittente] = u;
                    },
                    error: () => {}
                  });
                }
              }
            }
          });
        });
      },
      error: (err) => {
        this.errore = err.error?.detail || err.error?.errore || 'Errore nel caricamento dei suggerimenti.';
        this.loading = false;
      }
    });
  }

  vaiAProfilo(idMittente: number) {
    if (idMittente) {
      this.router.navigate(['/conversazioni/utente', idMittente]);
    }
  }

  completaSuggerimento(s: Suggerimento) {
    this.errore = '';
    this.suggerimentoService.aggiornaStato(s.id!, 'completato').subscribe({
      next: () => {
        s.stato = 'completato';
        // Aggiorna le liste
        this.suggerimentiRichiesti = this.suggerimentiRichiesti.filter(x => x.id !== s.id);
        this.suggerimentiCompletati.push(s);
        this.suggerimentiCompletati.sort((a, b) => a.id! - b.id!);
      },
      error: (err) => {
        this.errore = err.error?.detail || err.error?.errore || 'Errore durante l\'aggiornamento dello stato.';
      }
    });
  }
}