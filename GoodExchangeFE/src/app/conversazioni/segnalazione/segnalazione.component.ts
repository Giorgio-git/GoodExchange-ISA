import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { SegnalazioneService } from '../../servizi/segnalazione.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Segnalazione } from '../../modelli/segnalazione.model';
import { Messaggio } from '../../modelli/messaggio.model';
import { Utente } from '../../modelli/utente.model';
import { SessionService } from '../../servizi/session.service';

@Component({
  selector: 'app-segnalazione',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './segnalazione.component.html',
  styleUrls: ['./segnalazione.component.css']
})
export class SegnalazioneComponent implements OnInit, OnDestroy {
  idSegnalato!: number;
  titolo: string = '';
  contenuto: string = '';
  messaggioSuccesso = '';
  messaggioErrore = '';
  utenteLoggato: Utente | null = null;
  private userSub?: Subscription;

  constructor(
    private segnalazioneService: SegnalazioneService,
    private messaggioService: MessaggioService,
    private sessionService: SessionService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Recupera l'id dell'utente segnalato dai parametri della rotta
    const idParam = this.route.snapshot.paramMap.get('id');
    this.idSegnalato = idParam ? Number(idParam) : 0;
    this.userSub = this.sessionService.utenteLoggato$.subscribe(utente => {
      this.utenteLoggato = utente;
    });
  }

  inviaSegnalazione() {
    this.messaggioSuccesso = '';
    this.messaggioErrore = '';

    if (!this.utenteLoggato || !this.utenteLoggato.id) {
      this.messaggioErrore = 'Devi essere loggato per inviare una segnalazione.';
      return;
    }

    // 1. Crea la segnalazione
    const nuovaSegnalazione: Segnalazione = {
      id_segnalante: this.utenteLoggato.id,
      id_segnalato: this.idSegnalato,
      stato: 'aperta'
    };
    this.segnalazioneService.creaSegnalazione(nuovaSegnalazione).subscribe({
      next: segnalazione => {
        // 2. Crea il messaggio associato
        const nuovoMessaggio: Messaggio = {
          titolo: this.titolo,
          contenuto: this.contenuto,
          tipo: 'segnalazione',
          id_riferito: segnalazione.id!,
          id_mittente: this.utenteLoggato!.id!,
          id_destinatario: this.idSegnalato
        };
        this.messaggioService.creaMessaggio(nuovoMessaggio).subscribe({
          next: () => {
            this.messaggioSuccesso = 'Segnalazione inviata con successo!';
            setTimeout(() => { this.router.navigate(['/home']); }, 1200);
            // Resetta il form
            this.titolo = '';
            this.contenuto = '';
          },
          error: (err) => {
            this.messaggioErrore = err.error?.detail || err.error?.errore || 'Errore nell’invio del messaggio.';
          }
        });
      },
      error: (err) => {
        this.messaggioErrore = err.error?.detail || err.error?.errore || 'Errore nell’invio della segnalazione.';
      }
    });
  }

  ngOnDestroy(): void {
    this.userSub?.unsubscribe();
  }
}
