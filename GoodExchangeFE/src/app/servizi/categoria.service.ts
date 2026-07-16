import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Categoria } from '../modelli/categoria.model';

@Injectable({ providedIn: 'root' })
export class CategoriaService {
  private apiUrl = '/api/categorie';

  constructor(private http: HttpClient) { }

  /**
   * Recupera l'elenco di tutte le categorie.
   * Corrisponde a: GET /api/categorie
   */
  getCategorie(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(this.apiUrl);
  }

  /**
   * Recupera il dettaglio di una singola categoria per ID.
   * Corrisponde a: GET /api/categorie/{id}
   */
  getCategoriaById(id: number): Observable<Categoria> {
    return this.http.get<Categoria>(`${this.apiUrl}/${id}`);
  }

  /**
   * Crea una nuova categoria.
   * Corrisponde a: POST /api/categorie
   */
  creaCategoria(categoria: Categoria): Observable<any> {
    return this.http.post(this.apiUrl, categoria);
  }

  /**
   * Aggiorna una categoria esistente.
   * Corrisponde a: PUT /api/categorie/{id}
   */
  updateCategoria(id: number, aggiornamenti: Partial<Categoria>): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, aggiornamenti);
  }

  /**
   * Elimina una categoria per ID.
   * Corrisponde a: DELETE /api/categorie/{id}
   */
  deleteCategoria(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
