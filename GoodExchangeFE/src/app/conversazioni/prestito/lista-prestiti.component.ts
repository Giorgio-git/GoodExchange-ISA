import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { Prestito } from '../../modelli/prestito.model';
import { Utente } from '../../modelli/utente.model';
import { PrestitoService } from '../../servizi/prestito.service';
import { BeneService } from '../../servizi/bene.service';
import { SessionService } from '../../servizi/session.service';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
	selector: 'app-lista-prestiti',
	standalone: true,
	imports: [CommonModule, FormsModule, RouterModule],
	templateUrl: './lista-prestiti.component.html',
	styleUrls: ['./lista-prestiti.component.css']
})
export class ListaPrestitiComponent implements OnInit, OnDestroy {
	prestitiRichiesti: Prestito[] = [];
	prestitiConcessi: Prestito[] = [];
	utenteLoggato: Utente | null = null;
	statoFiltroRichiesti: string = '';
	statoFiltroConcessi: string = '';
	ricercaNomeRichiesti: string = '';
	ricercaNomeConcessi: string = '';
	isAdmin: boolean = false;
	loading = true;
	tabSelezionato: 'richiesti' | 'concessi' = 'richiesti';
	tuttiIPrestiti: Prestito[] = [];
	erroreStato: string = '';
	successoStato: string = '';
	private userSub?: Subscription;

	// Per feedback modal
	showFeedbackModal: boolean = false;
	feedbackPrestito: Prestito | null = null;
	feedbackDestinatarioId: number | null = null;

	statiPossibili = [
		'richiesto', 'accettato', 'rifiutato', 'in_corso', 'completato', 'annullato'
	];

		constructor(
			private prestitoService: PrestitoService,
			private beneService: BeneService,
			private sessionService: SessionService,
			private router: Router,
			private cdr: ChangeDetectorRef
		) {}

		ngOnInit(): void {
			this.userSub = this.sessionService.utenteLoggato$.subscribe((user: Utente | null) => {
				this.utenteLoggato = user;
				this.isAdmin = user?.ruolo === 'admin';
				if (!user) {
					this.loading = false;
					return;
				}
				if (this.isAdmin) {
					this.prestitoService.getPrestiti().subscribe({
						next: prestiti => {
							this.tuttiIPrestiti = prestiti.sort((a, b) => (a.id || 0) - (b.id || 0));
							this.loading = false;
						},
						error: () => this.loading = false
					});
				} else {
					this.prestitoService.getPrestiti({
						id_beneficiario: user.id
					}).subscribe({
						next: prestitiRichiesti => {
							this.prestitiRichiesti = prestitiRichiesti;
							this.prestitoService.getPrestiti({
								id_proprietario: user.id
							}).subscribe({
								next: prestitiConcessi => {
									this.prestitiConcessi = prestitiConcessi;
									this.loading = false;
								},
								error: () => this.loading = false
							});
						},
						error: () => this.loading = false
					});
				}
			});
		}

	// Cambia lo stato di un prestito dalla tabella admin con aggiornamento immutabile istantaneo della vista
	cambiaStatoPrestitoAdmin(prestito: Prestito, nuovoStato: string) {
		this.erroreStato = '';
		this.successoStato = '';
		this.prestitoService.updateStatoPrestito(prestito.id!, nuovoStato).subscribe({
			next: res => {
				prestito.stato = res.prestito.stato;
				// Aggiorna la reference dell'array così che Angular noti la modifica
				this.tuttiIPrestiti = this.tuttiIPrestiti.map(item => item.id === prestito.id ? { ...item, stato: res.prestito.stato } : item);
				this.successoStato = `Stato del prestito #${prestito.id} aggiornato a "${res.prestito.stato}".`;
				// Aggiorna stato bene: in_corso -> occupato (false), altro -> disponibile (true)
				const nuovoStatoBene = (res.prestito.stato === 'in_corso') ? false : true;
				this.beneService.updateBene(prestito.id_bene, { stato: nuovoStatoBene }).subscribe();
				this.cdr.detectChanges();
			},
			error: err => {
				this.erroreStato = err.error?.detail || err.error?.errore || 'Errore nell\'aggiornamento dello stato del prestito.';
				this.cdr.detectChanges();
			}
		});
	}


	getPrestitiRichiestiFiltrati(): Prestito[] {
		let filtrati = this.prestitiRichiesti;
		if (this.statoFiltroRichiesti) {
			filtrati = filtrati.filter(p => p.stato === this.statoFiltroRichiesti);
		}
		if (this.ricercaNomeRichiesti) {
			filtrati = filtrati.filter(p => (p.bene_nome || '').toLowerCase().includes(this.ricercaNomeRichiesti.toLowerCase()));
		}
		return filtrati;
	}

	getPrestitiConcessiFiltrati(): Prestito[] {
		let filtrati = this.prestitiConcessi;
		if (this.statoFiltroConcessi) {
			filtrati = filtrati.filter(p => p.stato === this.statoFiltroConcessi);
		}
		if (this.ricercaNomeConcessi) {
			filtrati = filtrati.filter(p => (p.bene_nome || '').toLowerCase().includes(this.ricercaNomeConcessi.toLowerCase()));
		}
		return filtrati;
	}

	selezionaTab(tab: 'richiesti' | 'concessi') {
		this.tabSelezionato = tab;
	}

	vaiADettaglio(id: number) {
		this.router.navigate(['/prestiti', id]);
	}

	vaiAProfilo(id?: number) {
		if (id) {
			this.router.navigate(['/conversazioni/utente', id]);
		}
	}

	// Mostra il modal feedback
	apriFeedback(prestito: Prestito, destinatarioId: number) {
		this.feedbackPrestito = prestito;
		this.feedbackDestinatarioId = destinatarioId;
		this.showFeedbackModal = true;
	}

	chiudiFeedback() {
		this.showFeedbackModal = false;
		this.feedbackPrestito = null;
		this.feedbackDestinatarioId = null;
	}

	ngOnDestroy(): void {
		this.userSub?.unsubscribe();
	}
}
