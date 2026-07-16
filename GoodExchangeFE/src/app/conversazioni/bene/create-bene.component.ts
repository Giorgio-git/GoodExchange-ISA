import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BeneService } from '../../servizi/bene.service';
import { CategoriaService } from '../../servizi/categoria.service';
import { Categoria } from '../../modelli/categoria.model';
import { SessionService } from '../../servizi/session.service';
import { Router } from '@angular/router';
import { Bene } from '../../modelli/bene.model';

@Component({
	selector: 'app-create-bene',
	templateUrl: './create-bene.component.html',
	styleUrls: ['./create-bene.component.css'],
		standalone: true,
		imports: [CommonModule, FormsModule],
})
export class CreateBeneComponent implements OnInit {
	nome: string = '';
	descrizione: string = '';
	id_categoria: number | null = null;
	peso: number | null = null;
	stato: boolean = true;
	selectedFile: File | null = null;
	categorie: Categoria[] = [];
	error: string | null = null;
	success: string | null = null;
	loggedUserId: number | null = null;

	constructor(
		private beneService: BeneService,
		private categoriaService: CategoriaService,
		private sessionService: SessionService,
		private router: Router
	) {}

	ngOnInit(): void {
		this.categoriaService.getCategorie().subscribe({
			next: cats => this.categorie = cats,
			error: err => this.categorie = []
		});
		const user = this.sessionService.getLoggedUser();
		this.loggedUserId = user && user.id !== undefined ? user.id : null;
	}


	// Ricorda $event è l'oggetto generato dal browser ogni volta che avviene un cambiamento nell'input file
	onFileChange(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files && input.files.length > 0) {
			this.selectedFile = input.files[0];
		}
	}


	// funzione di invio della form
	submit() {
		if (!this.nome || !this.id_categoria || !this.loggedUserId) {
			this.error = 'Compila tutti i campi obbligatori.';
			return;
		}
		this.error = null;

		// Non invio crediti_richiesti, lo recupero solo dalla categoria
		const bene: Bene = {
			nome: this.nome,
			descrizione: this.descrizione,
			id_categoria: this.id_categoria,
			peso: this.peso || 0,
			stato: this.stato,
			id_proprietario: this.loggedUserId
		};
		this.beneService.createBene(bene).subscribe({
			next: nuovoBene => {
				if (this.selectedFile && nuovoBene.id) {
					this.beneService.uploadImmagineBene(nuovoBene.id, this.selectedFile).subscribe({
						next: () => {
							this.success = 'Bene creato con successo!';
							setTimeout(() => this.router.navigate(['/beni'], { queryParams: { miei: true } }), 1200);
						},
						error: err => {
							this.error = err.error?.detail || err.error?.errore || 'Bene creato, ma si è verificato un errore durante il caricamento dell\'immagine.';
						}
					});
				} else {
					this.success = 'Bene creato con successo!';
					setTimeout(() => this.router.navigate(['/beni'], { queryParams: { miei: true } }), 1200);
				}
			},
			error: err => {
				this.error = err.error?.detail || err.error?.errore || 'Errore nella creazione del bene.';
			}
		});
	}
}
