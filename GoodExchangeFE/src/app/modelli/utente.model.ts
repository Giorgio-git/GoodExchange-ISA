export interface Utente {
  id?: number;
  username: string;
  password: string;
  nome: string;
  cognome: string;
  codice_fiscale: string;
  regione: string;
  provincia: string;
  citta: string;
  via: string;
  civico: string;
  ruolo: 'admin' | 'utente';
  stato: 'attivo' | 'disattivo';
  crediti_valore_beni: number;
  crediti_accumulati: number;
  cauzione: number;
  reputazione?: number | null;
  created_at?: string;
}
