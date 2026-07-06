export interface Segnalazione {
  id?: number;
  id_segnalante: number;
  id_segnalato?: number;
  data?: string;
  stato: 'aperta' | 'in_gestione' | 'risolta' | 'respinta';
}
