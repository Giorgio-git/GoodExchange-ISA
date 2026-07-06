import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FeedbackService } from '../../servizi/feedback.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Feedback } from '../../modelli/feedback.model';
import { Messaggio } from '../../modelli/messaggio.model';
import { SessionService } from '../../servizi/session.service';

@Component({
	selector: 'app-feedback',
	standalone: true,
	imports: [CommonModule, FormsModule],
	templateUrl: './feedback.component.html',
	styleUrls: ['./feedback.component.css']
})
export class FeedbackComponent implements OnInit {
	idDestinatario!: number;
	idPrestito!: number;
	voto: number = 5;
	titolo: string = '';
	descrizione: string = '';
	messaggio: string = '';

		constructor(
			private route: ActivatedRoute,
			private feedbackService: FeedbackService,
			private messaggioService: MessaggioService,
			private sessionService: SessionService,
			private router: Router
		) {}

	ngOnInit(): void {
		this.idPrestito = Number(this.route.snapshot.paramMap.get('idPrestito'));
		this.idDestinatario = Number(this.route.snapshot.paramMap.get('idDestinatario'));
	}

	inviaFeedback() {
		if (!this.idDestinatario || !this.idPrestito || !this.titolo || !this.descrizione || !this.voto) {
			this.messaggio = 'Compila tutti i campi.';
			return;
		}

		const utenteLoggato = this.sessionService.getLoggedUser();
		if (!utenteLoggato) {
			this.messaggio = 'Devi essere loggato.';
			return;
		}

		// Crea feedback
		const nuovoFeedback: Feedback = {
			id_utente: utenteLoggato.id,
			id_destinatario: this.idDestinatario,
			voto: this.voto,
			data: new Date().toISOString().slice(0, 10)
		};

			this.feedbackService.creaFeedback(nuovoFeedback).subscribe({
				next: (fb) => {
						// 2. Crea messaggio associato al feedback appena creato
						const nuovoMessaggio: Messaggio = {
							id_mittente: utenteLoggato.id,
							id_destinatario: this.idDestinatario,
							titolo: this.titolo,
							contenuto: this.descrizione,
							tipo: 'feedback',
							id_riferito: fb.id! // Associa il messaggio all'id del feedback
						};
					this.messaggioService.creaMessaggio(nuovoMessaggio).subscribe({
						next: () => {
							this.messaggio = 'Feedback inviato con successo!';
							setTimeout(() => {
								this.router.navigate(['/']);
							}, 500);
						},
						error: () => { this.messaggio = 'Errore nell invio del messaggio.'; }
					});
				},
				error: () => {
					this.messaggio = 'Errore nell invio del feedback.';
				}
			});
	}
}
