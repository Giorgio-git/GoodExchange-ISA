import { Component } from '@angular/core';
import { Router } from '@angular/router'; // per la navigazione tra pagine
import { CommonModule } from '@angular/common'; // per le direttive common come ngIf e ngFor
import { FormsModule } from '@angular/forms'; // per il two-way binding
import { CategoriaService } from '../../servizi/categoria.service'; // per il servizio categoria che si occupa di fare la chiamata al backend

@Component({
	selector: 'app-crea-categoria', // tag che posso usare nel file html per attivare questo componente
	templateUrl: './crea-categoria.component.html', // file html che contiene la struttura del componente
	styleUrls: ['./crea-categoria.component.css'], // file css che contiene lo stile del componente
	standalone: true, // rende il componente standalone, cioè non dipende da nessun modulo
	imports: [CommonModule, FormsModule] // importo le direttive common e FormsModule
})
export class CreaCategoriaComponent {
	nome: string = '';
	crediti: number | null = null;
	descrizione: string = '';
	error: string | null = null;
	success: string | null = null;


	constructor(private categoriaService: CategoriaService, private router: Router) { }
	// quando il componente nasce vengono iniettati il servizio categoria per chiamare il backend e il router per navigare tra le pagine 

	submit() {
		// 1. Validazione lato client (se i campi obbligatori non sono compilati non mando neanche la richiesta al backend)
		if (!this.nome || this.crediti === null) {
			this.error = 'Compila tutti i campi obbligatori.';
			return;
		}
		this.error = null;
		const nuovaCategoria = {
			nome: this.nome,
			crediti: this.crediti,
			descrizione: this.descrizione
		};
		// 2. Chiamata al servizio (che a sua volta chiama il backend)
		this.categoriaService.creaCategoria(nuovaCategoria).subscribe({
			next: () => {
				this.success = 'Categoria creata con successo!';
				setTimeout(() => this.router.navigate(['/admin/categorie']), 1000);
			},
			error: (err) => {
				this.error = err.error?.detail || err.error?.errore || 'Errore nella creazione della categoria.';
			}
		});
	}
}
