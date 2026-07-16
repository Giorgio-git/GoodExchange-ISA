export interface Bene {
  id?: number; // il valore sarà assegnato dal backend
  nome: string;
  descrizione?: string;
  peso?: number;
  id_categoria: number;
  categoria?: string;
  crediti_richiesti?: number;
  id_proprietario: number;
  stato: boolean; // true = disponibile, false = occupato
  foto?: string;
  created_at?: string;
}