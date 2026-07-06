
import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Utente } from '../modelli/utente.model';

@Injectable({
    providedIn: 'root'
})
export class UtenteService {
    private apiUrl = 'http://localhost:3000/api/utenti';

    constructor(private http: HttpClient) {}

    // recupera tutti gli utenti, eventualmente filtrati
    getUtenti(filtri?: any): Observable<Utente[]> {
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
        return this.http.get<Utente[]>(this.apiUrl, { params });
    }

    // recupera un utente tramite id
    getUtenteById(id: number): Observable<Utente> {
        return this.http.get<Utente>(`${this.apiUrl}/${id}`);
    }


    // crea un nuovo utente -- CONTROLLATA
    createUtente(nuovoUtente: Utente): Observable<Utente> {
        return this.http.post<Utente>(this.apiUrl, nuovoUtente);
    }

    // login con username e password passati nel body POST
    login(username: string, password: string): Observable<{ messaggio: string, utente: Utente }> {
        return this.http.post<{ messaggio: string, utente: Utente }>(
        `${this.apiUrl}/login`,
        { username, password }
        );
    }

    // aggiorna un utente (tutti i dati o quelli specificati)
    updateUtente(id: number, aggiornamento: Partial<Utente>): Observable<{ messaggio: string }> {
        return this.http.put<{ messaggio: string }>(`${this.apiUrl}/${id}`, aggiornamento);
    }

    // cambia lo stato di un utente (attivo/disattivo)
    changeStatoUtente(id: number, stato: 'attivo' | 'disattivo'): Observable<{ messaggio: string }> {
        return this.http.put<{ messaggio: string }>(`${this.apiUrl}/${id}/stato`, { stato });
    }

    /**
     * Recupera i crediti dell'utente (accumulati e valore beni) tramite endpoint dedicato
     */
    getCreditiUtente(id: number): Observable<{ crediti_valore_beni: number, crediti_accumulati: number }> {
        return this.http.get<{ crediti_valore_beni: number, crediti_accumulati: number }>(`${this.apiUrl}/${id}/crediti`);
    }

    // aggiorna la cauzione di un utente a un valore specifico
    aggiornaCauzioneUtente(id: number, cauzione: number): Observable<{ messaggio: string }> {
        return this.http.put<{ messaggio: string }>(`${this.apiUrl}/${id}/cauzione`, { cauzione });
    }

    // azzera la cauzione di un utente
    ritiraCauzioneUtente(id: number): Observable<{ messaggio: string }> {
        return this.aggiornaCauzioneUtente(id, 0);
    }
}