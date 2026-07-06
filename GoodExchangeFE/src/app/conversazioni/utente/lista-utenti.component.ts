import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UtenteService } from '../../servizi/utente.service';
import { Utente } from '../../modelli/utente.model';
import { Router } from '@angular/router';
import { SessionService } from '../../servizi/session.service';

@Component({
  selector: 'app-lista-utenti',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lista-utenti.component.html',
  styleUrls: ['./lista-utenti.component.css']
})
export class ListaUtentiComponent implements OnInit {
  utenti: Utente[] = [];
  loggedUserId: number | null = null;
  loading = true;

  constructor(
    private utenteService: UtenteService,
    private router: Router,
    private sessionService: SessionService
  ) {}

  ngOnInit(): void {
    this.sessionService.utenteLoggato$.subscribe(user => {
      this.loggedUserId = user?.id ?? null;
      this.utenteService.getUtenti().subscribe({
        next: utenti => {
          this.utenti = utenti.filter(u => u.id !== this.loggedUserId);
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        }
      });
    });
  }

  vaiAProfilo(id: number) {
    this.router.navigate(['/conversazioni/utente', id]);
  }

  cambiaStatoUtente(utente: Utente) {
    const nuovoStato = utente.stato === 'attivo' ? 'disattivo' : 'attivo';
    this.utenteService.changeStatoUtente(utente.id, nuovoStato).subscribe({
      next: () => {
        utente.stato = nuovoStato;
      },
      error: () => {
        alert('Errore nel cambio stato utente');
      }
    });
  }

  ritiraCauzione(utente: Utente) {
    this.utenteService.ritiraCauzioneUtente(utente.id).subscribe({
      next: () => {
        utente.cauzione = 0;
      },
      error: () => {
        alert('Errore nel ritiro cauzione');
      }
    });
  }
}
