import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CategoriaService } from '../../servizi/categoria.service';

@Component({
	selector: 'app-crea-categoria',
	templateUrl: './crea-categoria.component.html',
	styleUrls: ['./crea-categoria.component.css'],
	standalone: true,
	imports: [CommonModule, FormsModule]
})
export class CreaCategoriaComponent {
	nome: string = '';
	crediti: number | null = null;
	descrizione: string = '';
	error: string | null = null;
	success: string | null = null;


	constructor(private categoriaService: CategoriaService, private router: Router) {}

	submit() {
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
			this.categoriaService.creaCategoria(nuovaCategoria).subscribe({
				next: () => {
					this.success = 'Categoria creata con successo!';
					setTimeout(() => this.router.navigate(['/admin/categorie']), 1000);
				},
				error: () => {
					this.error = 'Errore nella creazione della categoria.';
				}
			});
	}
}
