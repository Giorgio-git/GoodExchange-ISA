import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Segnalazione } from '../modelli/segnalazione.model';

@Injectable({ providedIn: 'root' })
export class SegnalazioneService {
  private apiUrl = '/api/segnalazioni';

  constructor(private http: HttpClient) {}

  creaSegnalazione(segnalazione: Partial<Segnalazione>): Observable<Segnalazione> {
    return this.http.post<Segnalazione>(this.apiUrl, segnalazione);
  }

  getSegnalazioni(filtri?: any): Observable<Segnalazione[]> {
    let params = new HttpParams();
    if (filtri) {
      Object.keys(filtri).forEach(k => {
        if (filtri[k] !== undefined && filtri[k] !== null && filtri[k] !== '') {
          params = params.set(k, filtri[k]);
        }
      });
    }
    return this.http.get<Segnalazione[]>(this.apiUrl, { params });
  }

  getSegnalazioneById(id: number): Observable<Segnalazione> {
    return this.http.get<Segnalazione>(`${this.apiUrl}/${id}`);
  }

  aggiornaStatoSegnalazione(id: number, stato: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}/stato`, { stato });
  }
}
