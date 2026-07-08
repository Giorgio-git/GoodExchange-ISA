import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BeneService } from '../../servizi/bene.service';
import { PrestitoService } from '../../servizi/prestito.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { SessionService } from '../../servizi/session.service';
import { Bene } from '../../modelli/bene.model';
import { Utente } from '../../modelli/utente.model';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// MatDatepickerModule: per il componente di selezione della data nel form di richiesta prestito
import { MatDatepickerModule } from '@angular/material/datepicker';
// MatFormFieldModule: per i contenitori dei campi input in stile Material
import { MatFormFieldModule } from '@angular/material/form-field';
// MatInputModule: per gli input Material (date, testo, ecc.)
import { MatInputModule } from '@angular/material/input';
// provideNativeDateAdapter: provider per gestire le date in formato nativo JS (necessario per il datepicker Material)
import { provideNativeDateAdapter } from '@angular/material/core';

@Component({
	selector: 'app-crea-prestito',
	standalone: true,
	imports: [CommonModule, FormsModule, MatDatepickerModule, MatFormFieldModule, MatInputModule],
	// Il provider serve per abilitare l'adapter nativo delle date, così il datepicker di Angular Material usa oggetti Date standard JS
	providers: [provideNativeDateAdapter()],
	templateUrl: './crea-prestito.component.html',
	styleUrls: ['./crea-prestito.component.css']
})
export class CreaPrestitoComponent implements OnInit {
	// Per selezione intervallo
	selezioneStep: 'inizio' | 'fine' = 'inizio';

	bene: Bene | null = null;
	urlImmagine: string | null = null;

	occupiedDates: Date[] = [];
	dataInizio: Date | null = null;
	dataFine: Date | null = null;

	errore: string = '';
	successo: string = '';

	titoloMessaggio: string = '';
	contenutoMessaggio: string = '';

	loggedUser: Utente | null = null;

	constructor(
		private route: ActivatedRoute,
		private router: Router,
		private beneService: BeneService,
		private prestitoService: PrestitoService,
		private messaggioService: MessaggioService,
		private sessionService: SessionService
	) {}

	ngOnInit(): void {
		const idBene = Number(this.route.snapshot.paramMap.get('id'));

		if (!idBene) return;
		this.sessionService.utenteLoggato$.subscribe(user => {
			this.loggedUser = user;
		});
		// Recupera il bene
		this.beneService.getBeneById(idBene).subscribe({
			next: (bene) => {
				this.bene = bene;
				this.beneService.getImmagineBene(bene.id!).subscribe({
					next: (blob) => {
						this.urlImmagine = blob.size > 0 ? URL.createObjectURL(blob) : null;
					},
					error: () => { this.urlImmagine = null; }
				});
				// Recupera le date occupate
				this.prestitoService.getPrestiti({ id_bene: bene.id }).subscribe(prestiti => {
					// i prestiti occupanti sono quelli con stato accettato o in_corso
					const prestitiOccupanti = prestiti.filter(p => p.stato === 'accettato' || p.stato === 'in_corso');
					this.occupiedDates = [];
					prestitiOccupanti.forEach(p => {
						const start = new Date(p.data_inizio);
						const end = new Date(p.data_fine);
						for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
							this.occupiedDates.push(new Date(d));
						}
					});
				});
			},
			error: () => { this.errore = 'Bene non trovato.'; }
		});
	}


	dateFilter = (date: Date | null): boolean => {
		if (!date) return false;
		// Se la data che gli passo è tra le date occupate, ritorna false
		return !this.occupiedDates.some((d: Date) => d.toDateString() === date.toDateString());
	};

	richiediPrestito(): void {
		if (!this.bene || !this.loggedUser || !this.dataInizio || !this.dataFine || !this.titoloMessaggio || !this.contenutoMessaggio) {
			this.errore = 'Compila tutti i campi.';
			this.successo = '';
			return;
		}
			const nuovoPrestito = {
				id_bene: this.bene.id,
				id_beneficiario: this.loggedUser.id,
				id_proprietario: this.bene.id_proprietario,
				data_inizio: this.dataInizio.toISOString().slice(0,10),
				data_fine: this.dataFine.toISOString().slice(0,10),
				stato: 'richiesto' as 'richiesto'
			};
		this.prestitoService.createPrestito(nuovoPrestito).subscribe({
			next: prestito => {
				// Crea messaggio associato
				const nuovoMessaggio = {
					id_mittente: this.loggedUser!.id,
					id_destinatario: this.bene!.id_proprietario,
					titolo: this.titoloMessaggio,
					contenuto: this.contenutoMessaggio,
					tipo: 'prestito',
					id_riferito: prestito.id
				};
				this.messaggioService.creaMessaggio(nuovoMessaggio).subscribe({
					next: () => {
						this.successo = 'Richiesta inviata con successo!';
						this.errore = '';
						setTimeout(() => {
							this.router.navigate(['/prestiti', prestito.id]);
						}, 1200);
					},
					error: () => {
						this.errore = 'Prestito creato, ma errore nell’invio del messaggio.';
						this.successo = '';
					}
				});
			},
			error: () => {
				this.errore = 'Errore nella creazione del prestito.';
				this.successo = '';
			}
		});
	}
}