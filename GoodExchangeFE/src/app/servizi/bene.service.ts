// Per poter utilizzare la dependency injection, possiamo usare il decoratore @Injectable
import { Injectable } from '@angular/core';
// HttpClient per fare richieste http al backend e HttpParams per costruire i parametri da inviare nelle query string
    import { HttpClient, HttpParams } from '@angular/common/http';
    // Observabile per lavorare con i metodi http
    import { Observable } from 'rxjs';
    import { Bene } from '../modelli/bene.model';

@Injectable({
  providedIn: 'root'
})
export class BeneService {

  private apiUrl = 'http://localhost:3000/api/beni';

  constructor(private http: HttpClient) {}

  // Upload immagine bene
  uploadImmagineBene(id: number, file: File): Observable<any> {
    const formData = new FormData();  // oggetto javascript di classe FormData per costruire dati da inviare con una richiesta http di tipo multipart/form-data
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/${id}/immagine`, formData);
  }

  // Download immagine bene (restituisce blob)
  getImmagineBene(id: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/${id}/immagine`, { responseType: 'blob' });
  }

  // Delete immagine bene
  deleteImmagineBene(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}/immagine`);
  }

  // recupera tutti i beni, eventualmente filtrati
  getBeni(filtri?: any): Observable<Bene[]> {
    let params = new HttpParams();
    
    // Se ci sono filtri, aggiungili ai parametri della richiesta http
    if (filtri) {
      // per ogni chiave nei filtri
      Object.keys(filtri).forEach(key => {
        // se il valore del filtro non è undefined o una stringa vuota, aggiungilo ai parametri
        if (filtri[key] !== undefined && filtri[key] !== '') {
          // set crea un nuovo oggetto params di tipo HttpParams con il nuovo parametro aggiunto
          params = params.set(key, filtri[key]);
          // es. params = "?nome=martello&categoria=ferramenta"
        }
      });
    }
    // Restituisci l'Observable della richiesta http
    // come secondo parametro passo un oggetto (sintassi abbreviata - sarebbe { params: params })
    return this.http.get<Bene[]>(this.apiUrl, { params });
  }
  
    // Recupera beni filtrati e le relative immagini (se il backend lo supporta)
    getBeniConImmagini(filtri?: any): Observable<Bene[]> {
      let params = new HttpParams();
      if (filtri) {
        Object.keys(filtri).forEach(key => {
          if (filtri[key] !== undefined && filtri[key] !== '') {
            params = params.set(key, filtri[key]);
          }
        });
      }
      return this.http.get<Bene[]>(this.apiUrl, { params });
    }

  // recupera un bene tramite id
  getBeneById(id: number): Observable<Bene> {
    return this.http.get<Bene>(`${this.apiUrl}/${id}`);
  }

  // crea un nuovo bene
  createBene(nuovoBene: Bene): Observable<Bene> {
    return this.http.post<Bene>(this.apiUrl, nuovoBene);
  }

  // aggiorna un bene (tutti i dati o quelli specificati)
  updateBene(id: number, aggiornamento: Partial<Bene>): Observable<{ messaggio: string }> {
    return this.http.put<{ messaggio: string }>(`${this.apiUrl}/${id}`, aggiornamento);
  }

  // blocca un bene cambiandone lo stato
  blockBene(id: number): Observable<{ messaggio: string }> {
    return this.http.put<{ messaggio: string }>(`${this.apiUrl}/${id}/blocca`, null);
  }

  // sblocca un bene cambiandone lo stato
  unblockBene(id: number): Observable<{ messaggio: string }> {
    return this.http.put<{ messaggio: string }>(`${this.apiUrl}/${id}/sblocca`, null);
  }

}