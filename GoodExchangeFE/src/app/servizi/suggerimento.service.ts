import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Suggerimento } from '../modelli/suggerimento.model';

@Injectable({ providedIn: 'root' })
export class SuggerimentoService {
  private apiUrl = 'http://localhost:3000/api/suggerimenti';

  constructor(private http: HttpClient) {}

  getAll(): Observable<Suggerimento[]> {
    return this.http.get<Suggerimento[]>(this.apiUrl);
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
