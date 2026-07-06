import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Segnalazione } from '../modelli/segnalazione.model';

@Injectable({ providedIn: 'root' })
export class SegnalazioneService {
  private apiUrl = 'http://localhost:3000/api/segnalazioni';

  constructor(private http: HttpClient) {}

  creaSegnalazione(segnalazione: Partial<Segnalazione>): Observable<Segnalazione> {
    return this.http.post<Segnalazione>(this.apiUrl, segnalazione);
  }

  getSegnalazioni(filtri?: any): Observable<Segnalazione[]> {
    let url = this.apiUrl;
    if (filtri) {
      const params = new URLSearchParams();
      Object.keys(filtri).forEach(k => {
        if (filtri[k] !== undefined && filtri[k] !== null && filtri[k] !== '') {
          params.append(k, filtri[k]);
        }
      });
      url += '?' + params.toString();
    }
    return this.http.get<Segnalazione[]>(url);
  }

  getSegnalazioneById(id: number): Observable<Segnalazione> {
    return this.http.get<Segnalazione>(`${this.apiUrl}/${id}`);
  }

  aggiornaStatoSegnalazione(id: number, stato: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}/stato`, { stato });
  }
}
