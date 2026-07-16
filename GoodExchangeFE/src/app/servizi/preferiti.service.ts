import { Injectable } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Preferiti, PreferitiItem } from '../modelli/preferiti.model';

// OSS sono i service sia di preferiti che di preferitiItem


@Injectable({
  providedIn: 'root'
})
export class PreferitiService {
  private apiUrl = 'http://localhost:3000/api';

  constructor(private http: HttpClient) { }

  // Ottieni la lista preferiti di un utente
  getPreferitiByUtente(id_utente: number): Observable<Preferiti> {
    return this.http.get<Preferiti>(`${this.apiUrl}/preferiti/${id_utente}`);
  }

  // Crea una lista preferiti per un utente
  createPreferiti(id_utente: number, id_preferiti: number): Observable<{ messaggio: string }> {
    return this.http.post<{ messaggio: string }>(`${this.apiUrl}/preferiti/${id_utente}`, { id_preferiti });
  }

  // Elimina la lista preferiti di un utente
  deletePreferiti(id_utente: number): Observable<{ messaggio: string }> {
    return this.http.delete<{ messaggio: string }>(`${this.apiUrl}/preferiti/${id_utente}`);
  }

  // Ottieni tutti gli utenti preferiti per una lista
  getPreferitiItems(id_preferiti: number): Observable<PreferitiItem[]> {
    return this.http.get<PreferitiItem[]>(`${this.apiUrl}/preferitiItem/${id_preferiti}`);
  }

  // Aggiungi utente preferito alla lista
  addUtentePreferito(id_preferiti: number, id_utente_preferito: number): Observable<{ messaggio: string }> {
    return this.http.post<{ messaggio: string }>(`${this.apiUrl}/preferitiItem/${id_preferiti}/${id_utente_preferito}`, {});
  }

  // Rimuovi utente preferito dalla lista
  removeUtentePreferito(id_preferiti: number, id_utente_preferito: number): Observable<{ messaggio: string }> {
    return this.http.delete<{ messaggio: string }>(`${this.apiUrl}/preferitiItem/${id_preferiti}/${id_utente_preferito}`);
  }
}
