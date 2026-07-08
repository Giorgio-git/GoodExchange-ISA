import { Component, OnInit } from '@angular/core';
import { UtenteService } from '../../servizi/utente.service';
import { SessionService } from '../../servizi/session.service';
import { Utente } from '../../modelli/utente.model';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FeedbackService } from '../../servizi/feedback.service';
import { Feedback } from '../../modelli/feedback.model';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Messaggio } from '../../modelli/messaggio.model';
import { PreferitiService } from '../../servizi/preferiti.service';

@Component({
  selector: 'app-profilo',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './profilo.component.html',
  styleUrls: ['./profilo.component.css']
})
export class ProfiloComponent implements OnInit {
  messaggioPreferiti: string = '';
  isPreferito: boolean = false;
  showSegnalazione = false;
  utente: Utente | null = null;
  isAdmin: boolean = false;
  crediti_valore_beni: number = 0;
  crediti_accumulati: number = 0;

  utenteEdit: Partial<Utente> = {}; // Usato per visualizzare i dati dell'utente e separarli dall'utente loggato

  feedbackRicevuti: Feedback[] = [];
  messaggiFeedback: { [id: number]: Messaggio | null } = {};
  mittentiFeedback: { [id_utente: number]: Utente | null } = {};

  importoVersamento: number = 0;
  messaggioCauzione: string = '';


  constructor(
    private utenteService: UtenteService,
    private sessionService: SessionService,
    private route: ActivatedRoute,
    private feedbackService: FeedbackService,
    private messaggioService: MessaggioService,
    private preferitiService: PreferitiService
  ) {}

  versaCauzione(): void {
    console.log('Versamento cauzione per utente id:', this.utente?.id);
    if (!this.utente || !this.importoVersamento || this.importoVersamento <= 0) {
      this.messaggioCauzione = 'Inserisci un importo valido.';
      return;
    }
    const nuovaCauzione = Number(this.utente.cauzione || 0) + Number(this.importoVersamento);
    this.utenteService.aggiornaCauzioneUtente(this.utente.id, nuovaCauzione).subscribe({
      next: () => {
        this.utente!.cauzione = nuovaCauzione;
        this.utenteEdit.cauzione = nuovaCauzione;
        this.messaggioCauzione = 'Versamento effettuato!';
        this.importoVersamento = 0;
      },
      error: () => {
        this.messaggioCauzione = 'Errore nel versamento.';
        // azzera cauzione
        this.importoVersamento = 0;
      }
    });
  }

  ngOnInit(): void {
    // prova a recuperare l'id dalla route
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      // se l'id è presente nella route, visualizzo il profilo di quell'utente
      if (idParam) {
        const id = Number(idParam);

        this.sessionService.utenteLoggato$.subscribe(logged => {
          this.utente = logged;
          this.isAdmin = logged?.ruolo === 'admin';

          // Carica i dati dell'utente visualizzato
          this.utenteService.getUtenteById(id).subscribe(utente => {
            this.utenteEdit = { ...utente };
            this.caricaCrediti(utente.id);
            // Rimosso reset editing/modifiche
            this.caricaFeedbackRicevuti(utente.id);

            // Verifica se l'utente visualizzato è tra i preferiti
            if (logged && logged.id !== utente.id) {
              this.preferitiService.getPreferitiByUtente(logged.id).subscribe({
                next: (preferiti) => {
                  this.preferitiService.getPreferitiItems(preferiti.id).subscribe({
                    next: (items) => {
                      this.isPreferito = items.some(item => item.id_utente_preferito === utente.id);
                    },
                    error: () => { this.isPreferito = false; }
                  });
                },
                error: () => { this.isPreferito = false; }
              });
            }
          });
        });
      } 
      else {
        // se non è specificato un id, visualizzo il profilo dell'utente loggato
        this.sessionService.utenteLoggato$.subscribe(utente => {
          this.utente = utente;
          this.isAdmin = utente?.ruolo === 'admin';
          if (utente) {
            this.caricaCrediti(utente.id);
            this.utenteEdit = { ...utente };
            this.caricaFeedbackRicevuti(utente.id);
          } else {
            this.crediti_valore_beni = 0;
            this.crediti_accumulati = 0;
            this.utenteEdit = {};
            this.feedbackRicevuti = [];
          }
        });
      }
    });
  }

  aggiungiAiPreferiti(): void {
    if (!this.utente || !this.utenteEdit.id || this.utente.id === this.utenteEdit.id) return;
    this.messaggioPreferiti = '';
    this.preferitiService.getPreferitiByUtente(this.utente.id).subscribe({
      next: (preferiti) => {
        this.preferitiService.addUtentePreferito(preferiti.id, this.utenteEdit.id as number).subscribe({
          next: () => {
            this.messaggioPreferiti = 'Utente aggiunto ai preferiti!';
            this.isPreferito = true;
          },
          error: () => {
            this.messaggioPreferiti = "Errore nell'aggiunta ai preferiti.";
          }
        });
      },
      error: () => {
        this.messaggioPreferiti = 'Errore nel recupero della lista preferiti.';
      }
    });
  }

  rimuoviDaPreferiti(): void {
    if (!this.utente || !this.utenteEdit.id || this.utente.id === this.utenteEdit.id) return;
    this.messaggioPreferiti = '';
    this.preferitiService.getPreferitiByUtente(this.utente.id).subscribe({
      next: (preferiti) => {
        this.preferitiService.removeUtentePreferito(preferiti.id, this.utenteEdit.id as number).subscribe({
          next: () => {
            this.messaggioPreferiti = 'Utente rimosso dai preferiti!';
            this.isPreferito = false;
          },
          error: () => {
            this.messaggioPreferiti = "Errore nella rimozione dai preferiti.";
          }
        });
      },
      error: () => {
        this.messaggioPreferiti = 'Errore nel recupero della lista preferiti.';
      }
    });
  }

  caricaFeedbackRicevuti(id_destinatario: number): void {
    this.feedbackService.getFeedbackByDestinatario(id_destinatario).subscribe({
      next: (feedback) => {
        this.feedbackRicevuti = feedback;
        feedback.forEach(fb => {
          this.messaggioService.getMessaggiByTipo('feedback', fb.id).subscribe({
            next: (msgList) => {
              this.messaggiFeedback[fb.id!] = msgList.length > 0 ? msgList[0] : null;
            },
            error: () => {
              this.messaggiFeedback[fb.id!] = null;
            }
          });
          if (fb.id_utente && !this.mittentiFeedback[fb.id_utente]) {
            this.utenteService.getUtenteById(fb.id_utente).subscribe({
              next: (u) => {
                this.mittentiFeedback[fb.id_utente] = u;
              },
              error: () => {
                this.mittentiFeedback[fb.id_utente] = null;
              }
            });
          }
        });
      },
      error: () => {
        this.feedbackRicevuti = [];
      }
    });
  }

  caricaCrediti(id: number): void {
    this.utenteService.getCreditiUtente(id).subscribe({
      next: (res) => {
        this.crediti_valore_beni = res.crediti_valore_beni;
        this.crediti_accumulati = res.crediti_accumulati;
      },
      error: () => {
        this.crediti_valore_beni = 0;
        this.crediti_accumulati = 0;
      }
    });
  }

}