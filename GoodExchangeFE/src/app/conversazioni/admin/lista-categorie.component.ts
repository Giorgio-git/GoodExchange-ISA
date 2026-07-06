import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CategoriaService, Categoria } from '../../servizi/categoria.service';
import { Router } from '@angular/router';

@Component({
	selector: 'app-lista-categorie',
	templateUrl: './lista-categorie.component.html',
	styleUrls: ['./lista-categorie.component.css'],
	standalone: true,
	imports: [CommonModule]
})
export class ListaCategorieComponent implements OnInit {
	categorie: Categoria[] = [];

	constructor(private categoriaService: CategoriaService, private router: Router) {}

	ngOnInit(): void {
		this.categoriaService.getCategorie().subscribe({
			next: cats => this.categorie = cats,
			error: () => this.categorie = []
		});
	}

	vaiACreaCategoria() {
		this.router.navigate(['/admin/crea-categoria']);
	}
}
