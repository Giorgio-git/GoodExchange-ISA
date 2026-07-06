import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SuggerimentoService } from '../../servizi/suggerimento.service';
import { SessionService } from '../../servizi/session.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Messaggio } from '../../modelli/messaggio.model';

@Component({
  selector: 'app-suggerimento',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './suggerimento.component.html',
  styleUrls: ['./suggerimento.component.css']
})
export class SuggerimentoComponent {
  titolo = '';
  contenuto = '';
  errore = '';
  successo = false;

  annulla() {
    this.titolo = '';
    this.contenuto = '';
    this.errore = '';
    this.successo = false;
    this.router.navigate(['/']);
  }

  constructor(
    private suggerimentoService: SuggerimentoService,
    private sessionService: SessionService,
    private messaggioService: MessaggioService,
    private router: Router
  ) {}

  inviaSuggerimento() {
    const utente = this.sessionService.getLoggedUser();
    if (!utente) {
      this.errore = 'Devi essere loggato.';
      return;
    }
    if (!this.titolo.trim() || !this.contenuto.trim()) {
      this.errore = 'Compila tutti i campi.';
      return;
    }
    this.suggerimentoService.creaSuggerimento(utente.id).subscribe({
      next: suggerimento => {
        const nuovoMessaggio: Partial<Messaggio> = {
          titolo: this.titolo,
          contenuto: this.contenuto,
          tipo: 'suggerimento',
          id_riferito: suggerimento.id,
          id_mittente: utente.id,
          id_destinatario: 1 // admin
        };
        this.messaggioService.creaMessaggio(nuovoMessaggio).subscribe({
          next: () => {
            this.successo = true;
            this.titolo = '';
            this.contenuto = '';
            this.errore = '';
            setTimeout(() => {
              this.router.navigate(['/']);
            }, 500);
          },
          error: () => {
            this.errore = 'Errore invio messaggio.';
          }
        });
      },
      error: () => {
        this.errore = 'Errore creazione suggerimento.';
      }
    });
  }

}