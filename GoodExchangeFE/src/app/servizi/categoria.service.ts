import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Categoria {
  id: number;
  nome: string;
  crediti: number;
  descrizione?: string;
}

@Injectable({ providedIn: 'root' })
export class CategoriaService {

  creaCategoria(categoria: { nome: string; crediti: number; descrizione?: string }): Observable<any> {
    return this.http.post(this.apiUrl, categoria);
  }
  private apiUrl = 'http://localhost:3000/api/categorie';

  constructor(private http: HttpClient) { }

  getCategorie(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(this.apiUrl);
  }
}
