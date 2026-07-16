import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Messaggio } from '../modelli/messaggio.model';

@Injectable({ providedIn: 'root' })
export class MessaggioService {
	private apiUrl = '/api/messaggi';

	constructor(private http: HttpClient) {}

	getMessaggiByDestinatario(id_destinatario: number): Observable<Messaggio[]> {
		return this.http.get<Messaggio[]>(`${this.apiUrl}/destinatario/${id_destinatario}`).pipe(
			map(messaggi => (messaggi || []).sort((a, b) => (a.id || 0) - (b.id || 0)))
		);
	}

	getMessaggiByMittente(id_mittente: number): Observable<Messaggio[]> {
		return this.http.get<Messaggio[]>(`${this.apiUrl}/mittente/${id_mittente}`).pipe(
			map(messaggi => (messaggi || []).sort((a, b) => (a.id || 0) - (b.id || 0)))
		);
	}

	getMessaggiByTipo(tipo: string, id_riferito?: number): Observable<Messaggio[]> {
		let url = `${this.apiUrl}/tipo/${tipo}`;
		if (id_riferito !== undefined) {
			url += `?id_riferito=${id_riferito}`;
		}
		return this.http.get<Messaggio[]>(url).pipe(
			map(messaggi => (messaggi || []).sort((a, b) => (a.id || 0) - (b.id || 0)))
		);
	}

	getMessaggioById(id: number): Observable<Messaggio> {
		return this.http.get<Messaggio>(`${this.apiUrl}/${id}`);
	}

	creaMessaggio(messaggio: Partial<Messaggio>): Observable<{ id: number }> {
		return this.http.post<{ id: number }>(`${this.apiUrl}`, messaggio);
	}

	aggiornaMessaggio(id: number, messaggio: Partial<Messaggio>): Observable<{ success: boolean }> {
		return this.http.put<{ success: boolean }>(`${this.apiUrl}/${id}`, messaggio);
	}

	eliminaMessaggio(id: number): Observable<{ success: boolean }> {
		return this.http.delete<{ success: boolean }>(`${this.apiUrl}/${id}`);
	}
}
