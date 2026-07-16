import { Injectable } from "@angular/core";
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Feedback } from '../modelli/feedback.model';

@Injectable({
    providedIn: 'root'
})
export class FeedbackService {
    private apiUrl = '/api/feedback';

    constructor(private http: HttpClient) {}

    // Recupera feedback ricevuti da un utente tramite id_destinatario
    getFeedbackByDestinatario(id_destinatario: number): Observable<Feedback[]> {
        return this.http.get<Feedback[]>(`${this.apiUrl}/${id_destinatario}`);
    }

    // Recupera feedback tramite username destinatario
    getFeedbackByUsername(username: string): Observable<Feedback[]> {
        return this.http.get<Feedback[]>(`${this.apiUrl}/username/${username}`);
    }

    // Crea un nuovo feedback
    creaFeedback(feedback: Partial<Feedback>): Observable<Feedback> {
        return this.http.post<Feedback>(this.apiUrl, feedback);
    }

    // Elimina un feedback
    eliminaFeedback(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${id}`);
    }
}
