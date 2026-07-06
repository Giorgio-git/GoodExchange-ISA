import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
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
export class ListaPrestitiComponent implements OnInit {
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
			private router: Router
		) {}

		ngOnInit(): void {
			this.utenteLoggato = this.sessionService.getLoggedUser();
			this.isAdmin = this.utenteLoggato?.ruolo === 'admin';
			if (!this.utenteLoggato) return;
			if (this.isAdmin) {
				this.prestitoService.getPrestiti().subscribe(prestiti => {
					this.tuttiIPrestiti = prestiti;
					this.loading = false;
				});
			} else {
				this.prestitoService.getPrestiti({
					id_beneficiario: this.utenteLoggato.id
				}).subscribe(prestitiRichiesti => {
					this.prestitiRichiesti = prestitiRichiesti;
					this.prestitoService.getPrestiti({
						id_proprietario: this.utenteLoggato!.id
					}).subscribe(prestitiConcessi => {
						this.prestitiConcessi = prestitiConcessi;
						this.loading = false;
					});
				});
			}
		}

	// Cambia lo stato di un prestito dalla tabella admin
		cambiaStatoPrestitoAdmin(prestito: Prestito, nuovoStato: string) {
			this.erroreStato = '';
			this.successoStato = '';
			this.prestitoService.updateStatoPrestito(prestito.id, nuovoStato).subscribe({
				next: res => {
					prestito.stato = res.prestito.stato;
					this.successoStato = `Stato del prestito #${prestito.id} aggiornato a ${res.prestito.stato}`;
					// Aggiorna stato bene: in_corso -> occupato (false), altro -> disponibile (true)
					const nuovoStatoBene = (res.prestito.stato === 'in_corso') ? false : true;
					this.beneService.updateBene(prestito.id_bene, { stato: nuovoStatoBene }).subscribe();
				},
				error: (err) => {
					this.erroreStato = `Errore aggiornamento stato prestito #${prestito.id}`;
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
}
