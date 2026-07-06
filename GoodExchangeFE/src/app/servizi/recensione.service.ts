import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Recensione } from '../modelli/recensione.model';

@Injectable({
    providedIn: 'root'
})
export class RecensioneService {
    private apiUrl = 'http://localhost:3000/api/recensioni';

    constructor(private http: HttpClient) {}

    // recupera tutte le recensioni, eventualmente filtrate
    getRecensioni(filtri?: any): Observable<Recensione[]> {
        let params = new HttpParams();

        // Se ci sono filtri, aggiungili ai parametri della richiesta http
        if (filtri) {
            // per ogni chiave nei filtri
            Object.keys(filtri).forEach(key => {
                // se il valore del filtro non è undefined o una stringa vuota, aggiungilo ai parametri
                if (filtri[key] !== undefined && filtri[key] !== '') {
                    // set crea un nuovo oggetto params di tipo HttpParams con il nuovo parametro aggiunto
                    params = params.set(key, filtri[key]);
                }
            });
        }
        return this.http.get<Recensione[]>(this.apiUrl, { params });
    }

    // recupera una recensione tramite id
    getRecensioneById(id: number): Observable<Recensione> {
        return this.http.get<Recensione>(`${this.apiUrl}/${id}`);
    }

    // crea una nuova recensione
    createRecensione(nuovaRecensione: Recensione): Observable<Recensione> {
        return this.http.post<Recensione>(this.apiUrl, nuovaRecensione);
    }

    // aggiorna una recensione (tutti i dati o quelli specificati)
    updateRecensione(id: number, aggiornamento: Partial<Recensione>): Observable<{ messaggio: string }> {
        return this.http.put<{ messaggio: string }>(`${this.apiUrl}/${id}`, aggiornamento);
    }

    // elimina una recensione
    deleteRecensione(id: number): Observable<{ messaggio: string }> {
        return this.http.delete<{ messaggio: string }>(`${this.apiUrl}/${id}`);
    }
}