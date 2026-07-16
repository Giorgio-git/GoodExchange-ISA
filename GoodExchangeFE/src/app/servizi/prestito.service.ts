import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Prestito } from '../modelli/prestito.model';

@Injectable({
  providedIn: 'root'
})
export class PrestitoService {

  private apiUrl = 'http://localhost:3000/api/prestiti';

  constructor(private http: HttpClient) {}

  // recupera tutti i prestiti, eventualmente filtrati (usa /filtri se sono presenti date o parametri specifici)
  getPrestiti(filtri?: any): Observable<Prestito[]> {
    let params = new HttpParams();
    let url = this.apiUrl;
    
    if (filtri) {
      Object.keys(filtri).forEach(key => {
        if (filtri[key] !== undefined && filtri[key] !== '') {
          params = params.set(key, filtri[key]);
        }
      });
      // Se sono presenti filtri per intervallo di date, usiamo l'endpoint dedicato /prestiti/filtri
      if (filtri.data_da || filtri.data_a) {
        url = `${this.apiUrl}/filtri`;
      }
    }
    return this.http.get<Prestito[]>(url, { params });
  }

  // recupera un prestito tramite id
  getPrestitoById(id: number): Observable<Prestito> {
    return this.http.get<Prestito>(`${this.apiUrl}/${id}`);
  }

  // verifica disponibilità di un bene per un periodo
  verificaDisponibilita(beneId: number, dataInizio: string, dataFine: string): Observable<{disponibile: boolean}> {
    const params = new HttpParams()
      .set('data_inizio', dataInizio)
      .set('data_fine', dataFine);
    
    return this.http.get<{disponibile: boolean}>(`${this.apiUrl}/disponibilita/${beneId}`, { params });
  }

  // ottiene il calendario di un bene per un mese specifico
  getCalendarioBene(beneId: number, anno: number, mese: number): Observable<Prestito[]> {
    const params = new HttpParams()
      .set('anno', anno.toString())
      .set('mese', mese.toString());
    
    return this.http.get<Prestito[]>(`${this.apiUrl}/calendario/${beneId}`, { params });
  }

  // crea un nuovo prestito
  createPrestito(nuovoPrestito: Partial<Prestito>): Observable<Prestito> {
    return this.http.post<Prestito>(this.apiUrl, nuovoPrestito);
  }

  // aggiorna lo stato di un prestito
  updateStatoPrestito(id: number, stato: string, note?: string): Observable<{ messaggio: string; prestito: Prestito }> {
    const body = { stato, note };
    return this.http.put<{ messaggio: string; prestito: Prestito }>(`${this.apiUrl}/${id}/stato`, body);
  }

  // elimina un prestito
  deletePrestito(id: number): Observable<{ messaggio: string }> {
    return this.http.delete<{ messaggio: string }>(`${this.apiUrl}/${id}`);
  }

  // metodi di utilità per il calendario

  // genera i giorni di un mese per il calendario
  generaGiorniMese(anno: number, mese: number): Date[] {
    const giorni: Date[] = [];
    const ultimoGiorno = new Date(anno, mese, 0).getDate();
    
    for (let giorno = 1; giorno <= ultimoGiorno; giorno++) {
      giorni.push(new Date(anno, mese - 1, giorno));
    }
    
    return giorni;
  }

  // Helper per formattare una data nativa JS nel formato YYYY-MM-DD locale (evitando lo slittamento UTC)
  private formatLocalYYYYMMDD(d: Date): string {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // verifica se un giorno è occupato basandosi sui prestiti
  isGiornoOccupato(data: Date, prestiti: Prestito[]): boolean {
    const dataString = this.formatLocalYYYYMMDD(data);
    
    return prestiti.some(prestito => {
      return dataString >= prestito.data_inizio && dataString <= prestito.data_fine;
    });
  }

  // formatta data per l'input HTML
  formatDateForInput(date: Date): string {
    return this.formatLocalYYYYMMDD(date);
  }


  // valida le date del prestito
  validateDates(dataInizio: string, dataFine: string): { valid: boolean; error?: string } {
    const oggi = new Date();
    oggi.setHours(0, 0, 0, 0);
    
    const inizio = new Date(dataInizio);
    const fine = new Date(dataFine);
    
    if (inizio < oggi) {
      return { valid: false, error: 'La data di inizio non può essere nel passato' };
    }
    
    if (fine <= inizio) {
      return { valid: false, error: 'La data di fine deve essere successiva alla data di inizio' };
    }
    
    const diffGiorni = (fine.getTime() - inizio.getTime()) / (1000 * 60 * 60 * 24);
    if (diffGiorni > 30) {
      return { valid: false, error: 'Il prestito non può durare più di 30 giorni' };
    }
    
    return { valid: true };
  }
}
