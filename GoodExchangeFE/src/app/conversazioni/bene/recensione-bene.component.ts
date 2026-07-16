import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RecensioneService } from '../../servizi/recensione.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Recensione } from '../../modelli/recensione.model';
import { Messaggio } from '../../modelli/messaggio.model';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { PrestitoService } from '../../servizi/prestito.service';

@Component({
	selector: 'app-recensione-bene',
	standalone: true,
	imports: [CommonModule, FormsModule, RouterModule],
	templateUrl: './recensione-bene.component.html',
	styleUrls: ['./recensione-bene.component.css']
})
export class RecensioneBeneComponent implements OnInit {

	voto: number = 0;
	titolo: string = '';
	messaggio: string = '';
	errore: string = '';
	successo: string = '';

	prestitoId: number | null = null;
	id_bene: number | null = null;
	id_beneficiario: number | null = null;
	id_destinatario: number | null = null;

	constructor(
		private recensioneService: RecensioneService,
		private messaggioService: MessaggioService,
		private prestitoService: PrestitoService,
		private route: ActivatedRoute,
		private router: Router
	) {}

	ngOnInit(): void {
		// Recupero l'id del prestito dalla rotta
		this.prestitoId = Number(this.route.snapshot.paramMap.get('id'));

		// Recupero i dati del prestito per ottenere id_bene, id_beneficiario e id_destinatario
		if (this.prestitoId) {
			this.prestitoService.getPrestitoById(this.prestitoId).subscribe({
				next: (prestito) => {
					this.id_bene = prestito.id_bene;
					this.id_beneficiario = prestito.id_beneficiario;
					this.id_destinatario = prestito.id_proprietario;
				},
				error: (err) => {
					this.errore = err.error?.detail || err.error?.errore || 'Errore nel caricamento dati prestito.';
				}
			});
		} else {
			this.errore = 'ID prestito non valido.';
		}
	}

	// Imposta il voto selezionato
	setVoto(star: number) {
		this.voto = star;
	}

	/**
	 * Invia la recensione dell'oggetto e, se presente, il messaggio associato.
	 * Il messaggio viene indirizzato al proprietario dell'oggetto (id_destinatario).
	 * Dopo l'invio, l'utente viene reindirizzato alla home.
	 */
	inviaRecensione() {
		if (this.voto === 0) {
			this.errore = 'Seleziona un voto.';
			this.successo = '';
			return;
		}
		this.errore = '';
		this.successo = '';
		// Crea la recensione
		const nuovaRecensione: Recensione = {
			id_bene: this.id_bene!,
			id_beneficiario: this.id_beneficiario!,
			voto: this.voto
		};
		this.recensioneService.createRecensione(nuovaRecensione).subscribe({
			next: (recensione) => {

				// Se l'utente ha scritto un messaggio, lo invia come messaggio associato
				if (this.messaggio && this.messaggio.trim().length > 0) {
					// Il campo tipo deve essere una stringa ('recensione') come richiesto dal database
					const nuovoMessaggio: Messaggio = {
						id_mittente: this.id_beneficiario!, // chi scrive la recensione
						id_destinatario: this.id_destinatario!, // proprietario dell'oggetto
						titolo: this.titolo || '',
						contenuto: this.messaggio,
						tipo: 'recensione',
						id_riferito: recensione.id!
					};
					this.messaggioService.creaMessaggio(nuovoMessaggio).subscribe({
						next: () => {
							this.resetForm();
							this.successo = 'Recensione e messaggio inviati!';
							// Reindirizza alla home dopo invio
							this.router.navigate(['/home']);
						},
						error: (err) => {
							this.errore = err.error?.detail || err.error?.errore || 'Errore nell’invio del messaggio.';
						}
					});
				} else {
					// Solo recensione, senza messaggio
					this.resetForm();
					this.successo = 'Recensione inviata!';
					// Reindirizza alla home dopo invio
					this.router.navigate(['/home']);
				}
			},
			error: (err) => {
				this.errore = err.error?.detail || err.error?.errore || 'Errore nell’invio della recensione.';
			}
		});
	}

	// Reset del form dopo l'invio
	resetForm() {
		this.voto = 0;
		this.titolo = '';
		this.messaggio = '';
		this.successo = '';
	}

	annulla() {
		this.router.navigate(['/prestiti']);
	}
}

