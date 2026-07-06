export interface Messaggio {
	id?: number;
	id_mittente: number;
	id_destinatario: number;
	titolo: string;
	contenuto: string;
	tipo: string; // correzione: enum stringa come nel db
	id_riferito: number;
}
