import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { SessionService } from '../../servizi/session.service';
import { CommonModule } from '@angular/common';
import { MessaggioComponent } from '../messaggio/messaggio.component';
import { ActivatedRoute, Router } from '@angular/router';
import { Prestito } from '../../modelli/prestito.model';
import { Messaggio } from '../../modelli/messaggio.model';
import { PrestitoService } from '../../servizi/prestito.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Utente } from '../../modelli/utente.model';
import { UtenteService } from '../../servizi/utente.service';

@Component({
	selector: 'app-dettaglio-prestito',
	standalone: true,
	imports: [CommonModule, MessaggioComponent, FormsModule],
	templateUrl: './dettaglio-prestito.component.html',
	styleUrls: ['./dettaglio-prestito.component.css']
})
export class DettaglioPrestitoComponent implements OnInit {
	prestito: Prestito | null = null;
	erroreStato: string = '';
	successoStato: string = '';
	
	messaggi: Messaggio[] = [];
	utenti: { [id: number]: Utente } = {};
	loading = true;
	titoloMessaggio: string = '';
	contenutoMessaggio: string = '';
	invioError: string = '';
	invioSuccess: string = '';
	loggedUser: Utente | null = null;

		constructor(
			private route: ActivatedRoute,
			private router: Router,
			private prestitoService: PrestitoService,
			private messaggioService: MessaggioService,
			private sessionService: SessionService,
			private utenteService: UtenteService
		) {}

	ngOnInit(): void {
		const id = Number(this.route.snapshot.paramMap.get('id'));
		if (!id) return;
		this.sessionService.utenteLoggato$.subscribe((user: Utente | null) => {
			this.loggedUser = user;
		});
			this.prestitoService.getPrestitoById(id).subscribe(prestito => {
				this.prestito = prestito;
				// Carica messaggi riferiti a questo prestito
				this.messaggioService.getMessaggiByTipo('prestito', id).subscribe(messaggi => {
					this.messaggi = messaggi;
					// Popola la mappa utenti per i mittenti dei messaggi
					const mittentiUnici = Array.from(new Set(messaggi.map(m => m.id_mittente)));
					mittentiUnici.forEach(idMittente => {
						if (!this.utenti[idMittente]) {
							this.utenteService.getUtenteById(idMittente).subscribe(utente => {
								this.utenti[idMittente] = utente;
							});
						}
					});
					this.loading = false;
				});
			});
	}

	// Utility per visualizzare username mittente
	getUsernameMittente(messaggio: Messaggio): string {
		// Se hai una mappa utenti, puoi mostrare username, altrimenti mostra id
		return this.utenti[messaggio.id_mittente]?.username || `Utente #${messaggio.id_mittente}`;
	}

		// Cambia lo stato del prestito (accetta/rifiuta/completa) e reindirizza alla tabella prestiti
			cambiaStatoPrestito(nuovoStato: 'accettato' | 'rifiutato' | 'completato') {
				console.log('Bottone cliccato, valore passato:', nuovoStato);
				if (!this.prestito) return;
				this.erroreStato = '';
				this.successoStato = '';
				console.log('Invio al backend:', { id: this.prestito.id, stato: nuovoStato });
				this.prestitoService.updateStatoPrestito(this.prestito.id, nuovoStato).subscribe({
					next: res => {
						console.log('Risposta backend:', res);
						this.successoStato = `Prestito ${nuovoStato} con successo.`;
						this.prestito = res.prestito;
						// Reindirizza automaticamente alla tabella dei prestiti
						this.router.navigate(['/prestiti']);
					},
					error: (err) => {
						console.error('Errore backend:', err);
						this.erroreStato = 'Errore nella modifica dello stato.';
					}
				});
			}

		// Invio nuovo messaggio associato al prestito
		inviaMessaggio(): void {
		if (!this.loggedUser || !this.prestito) {
			this.invioError = 'Utente o prestito non disponibili.';
			return;
		}
		if (!this.titoloMessaggio || !this.contenutoMessaggio) {
			this.invioError = 'Compila titolo e contenuto.';
			return;
		}
		// Destinatario: se l'utente loggato è il beneficiario, destinatario è il proprietario, viceversa
		const id_destinatario = (this.loggedUser.id === this.prestito.id_beneficiario)
			? this.prestito.id_proprietario
			: this.prestito.id_beneficiario;
		const nuovoMessaggio: Partial<Messaggio> = {
			id_mittente: this.loggedUser.id,
			id_destinatario,
			titolo: this.titoloMessaggio,
			contenuto: this.contenutoMessaggio,
			tipo: 'prestito',
			id_riferito: this.prestito.id
		};
		this.messaggioService.creaMessaggio(nuovoMessaggio).subscribe({
			next: () => {
				this.invioSuccess = 'Messaggio inviato!';
				this.invioError = '';
				this.titoloMessaggio = '';
				this.contenutoMessaggio = '';
				// Ricarica la lista messaggi
				this.messaggioService.getMessaggiByTipo('prestito', this.prestito!.id).subscribe(messaggi => {
					this.messaggi = messaggi;
				});
			},
			error: () => {
				this.invioError = 'Errore invio messaggio.';
				this.invioSuccess = '';
			}
		});
	}
}
