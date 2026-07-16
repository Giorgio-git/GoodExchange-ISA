export interface Suggerimento {
  id?: number;
  id_mittente: number;
  stato: 'richiesto' | 'completato';
  data?: string;
}
