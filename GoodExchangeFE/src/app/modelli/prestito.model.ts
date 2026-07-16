export interface Prestito {
  id?: number;
  id_bene: number;
  id_proprietario: number;
  id_beneficiario: number;
  data_inizio: string; // formato YYYY-MM-DD
  data_fine: string;   // formato YYYY-MM-DD
  data_richiesta?: string;
  stato: 'richiesto' | 'accettato' | 'rifiutato' | 'in_corso' | 'completato' | 'annullato';
  crediti_utilizzati?: number;
  note?: string;
  created_at?: string;

  // Campi aggiuntivi dalle JOIN
  bene_nome?: string;
  beneficiario_username?: string;
  proprietario_username?: string;
}