import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
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
	imports: [CommonModule, FormsModule, RouterModule],
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
		if (!this.idDestinatario || !this.idPrestito || !this.titolo?.trim() || !this.descrizione?.trim() || !this.voto) {
			this.messaggio = 'Compila sia il Titolo che la Descrizione per poter inviare il feedback.';
			return;
		}

		const utenteLoggato = this.sessionService.getLoggedUser();
		if (!utenteLoggato) {
			this.messaggio = 'Devi essere loggato.';
			return;
		}

		const d = new Date();
		const dataLocale = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

		// Crea feedback
		const nuovoFeedback: Feedback = {
			id_utente: utenteLoggato.id!,
			id_destinatario: this.idDestinatario,
			voto: this.voto,
			data: dataLocale
		};


			this.feedbackService.creaFeedback(nuovoFeedback).subscribe({
				next: (fb) => {
						// 2. Crea messaggio associato al feedback appena creato
						const nuovoMessaggio: Messaggio = {
							id_mittente: utenteLoggato.id!,
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
								this.router.navigate(['/prestiti']);
							}, 500);
						},
						error: (err) => { this.messaggio = err.error?.detail || err.error?.errore || 'Errore nell’invio del messaggio.'; }
					});
				},
				error: (err) => {
					this.messaggio = err.error?.detail || err.error?.errore || 'Errore nell’invio del feedback.';
				}
			});
	}

	annulla() {
		this.router.navigate(['/prestiti']);
	}
}

