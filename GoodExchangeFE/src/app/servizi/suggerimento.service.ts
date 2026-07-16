import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Suggerimento } from '../modelli/suggerimento.model';

@Injectable({ providedIn: 'root' })
export class SuggerimentoService {
  private apiUrl = '/api/suggerimenti';

  constructor(private http: HttpClient) {}

  getAll(filtri?: any): Observable<Suggerimento[]> {
    let params = new HttpParams();
    if (filtri) {
      Object.keys(filtri).forEach(k => {
        if (filtri[k] !== undefined && filtri[k] !== null && filtri[k] !== '') {
          params = params.set(k, filtri[k]);
        }
      });
    }
    return this.http.get<Suggerimento[]>(this.apiUrl, { params });
  }

  getByUtente(id_mittente: number): Observable<Suggerimento[]> {
    return this.http.get<Suggerimento[]>(`${this.apiUrl}/utente/${id_mittente}`);
  }

  creaSuggerimento(id_mittente: number): Observable<Suggerimento> {
    return this.http.post<Suggerimento>(this.apiUrl, { id_mittente });
  }

  aggiornaStato(id: number, stato: 'richiesto' | 'completato'): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}/stato`, { stato });
  }
}
