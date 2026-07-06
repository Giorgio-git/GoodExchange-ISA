import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { CommonModule } from '@angular/common';
import { PreferitiService } from '../../servizi/preferiti.service';
import { SessionService } from '../../servizi/session.service';
import { UtenteService } from '../../servizi/utente.service';
import { PreferitiItem } from '../../modelli/preferiti.model';
import { Utente } from '../../modelli/utente.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-preferiti',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './preferiti.component.html',
  styleUrls: ['./preferiti.component.css']
})
export class PreferitiComponent implements OnInit {
  utentiPreferiti: Utente[] = [];
  errore: string = '';

  constructor(
    private preferitiService: PreferitiService,
    private sessionService: SessionService,
    private utenteService: UtenteService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.caricaUtentiPreferiti();
  }

  caricaUtentiPreferiti(): void {
    const utente = this.sessionService.getLoggedUser();
    if (!utente) {
      this.utentiPreferiti = [];
      return;
    }

    this.preferitiService.getPreferitiByUtente(utente.id).subscribe({
      next: (preferiti) => {
        // Passo la list adssociata all'utente loggato per recuperarne gli item
        this.preferitiService.getPreferitiItems(preferiti.id).subscribe({
          next: (items: PreferitiItem[]) => {
            if (items.length === 0) {
              this.utentiPreferiti = [];
              return;
            }
            // Carica i dati degli utenti preferiti
            const richieste = items.map(item =>
              this.utenteService.getUtenteById(item.id_utente_preferito)
            );

            // Uso il forkJoin perchè ogni richiesta è un Observable e voglio aspettare che tutte siano completate
            forkJoin(richieste).subscribe({
              next: (utenti) => {
                this.utentiPreferiti = utenti.filter(u => !!u);
              },
              error: () => {
                this.errore = 'Errore nel caricamento utenti preferiti';
              }
            });
          },
          error: () => {
            this.errore = 'Errore nel caricamento utenti preferiti';
          }
        });
      },
      error: () => {
        this.errore = 'Errore nel caricamento lista preferiti';
      }
    });
  }

  vaiAlProfilo(id: number): void {
    this.router.navigate(['/conversazioni/utente', id]);
  }

  rimuoviPreferito(id_utente_preferito: number): void {
    const utente = this.sessionService.getLoggedUser();
    if (!utente) return;
    this.preferitiService.getPreferitiByUtente(utente.id).subscribe({
      next: (preferiti) => {
        this.preferitiService.removeUtentePreferito(preferiti.id, id_utente_preferito).subscribe({
          next: () => {
            this.caricaUtentiPreferiti();
          },
          error: () => {
            this.errore = 'Errore nella rimozione';
          }
        });
      }
    });
  }
}
