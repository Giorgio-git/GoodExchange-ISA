import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { UtenteService } from '../../servizi/utente.service';
import { Utente } from '../../modelli/utente.model';
import { ITALIA_GEODATA, RegioneData, ProvinciaData } from '../../modelli/italia-geodata';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent { 
  nuovoUtente: Utente = {
    id: 0,
    nome: '',
    cognome: '',
    username: '',
    password: '',
    codice_fiscale: '',
    regione: '',
    provincia: '',
    citta: '',
    via: '',
    civico: '',
    ruolo: 'utente',
    stato: 'attivo',
    crediti_valore_beni: 0,
    crediti_accumulati: 0,
    cauzione: 0
  };
  
  errore: string = '';

  // Dati e liste per menu a tendina a cascata (Indirizzo)
  regioni: RegioneData[] = ITALIA_GEODATA;
  provinceDisponibili: ProvinciaData[] = [];
  comuniDisponibili: string[] = [];
  cittaSelezionataInMenu: string = '';
  altroComuneAttivo: boolean = false;

  // inietto le dipendenze nel costruttore
  constructor(
    private utenteService: UtenteService, // per i servizi di utente (creaUtente)
    private router: Router  // per la navigazione dopo la registrazione
  ) {}

  // Scattato al cambio della Regione dal menu a tendina
  onRegioneChange(): void {
    this.nuovoUtente.provincia = '';
    this.nuovoUtente.citta = '';
    this.cittaSelezionataInMenu = '';
    this.altroComuneAttivo = false;
    this.comuniDisponibili = [];

    const regioneTrovata = this.regioni.find(r => r.nome === this.nuovoUtente.regione);
    this.provinceDisponibili = regioneTrovata ? regioneTrovata.province : [];
  }

  // Scattato al cambio della Provincia dal menu a tendina
  onProvinciaChange(): void {
    this.nuovoUtente.citta = '';
    this.cittaSelezionataInMenu = '';
    this.altroComuneAttivo = false;

    const provinciaTrovata = this.provinceDisponibili.find(p => p.sigla === this.nuovoUtente.provincia);
    if (provinciaTrovata) {
      this.comuniDisponibili = [...provinciaTrovata.comuni, 'Altro comune (specifica)...'];
    } else {
      this.comuniDisponibili = [];
    }
  }

  // Scattato al cambio del Comune dal menu a tendina
  onComuneMenuChange(): void {
    if (this.cittaSelezionataInMenu === 'Altro comune (specifica)...') {
      this.altroComuneAttivo = true;
      this.nuovoUtente.citta = '';
    } else {
      this.altroComuneAttivo = false;
      this.nuovoUtente.citta = this.cittaSelezionataInMenu;
    }
  }

  signup(): void {
    this.utenteService.createUtente(this.nuovoUtente).subscribe({
      next: () => {
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.errore = err.error?.detail || err.error?.errore || 'Errore durante la registrazione';
      }
    });
  }

  // Pulisce il form e resetta lo stato di validità Angular
  clearForm(): void {
    this.nuovoUtente = {
      id: 0,
      nome: '',
      cognome: '',
      username: '',
      password: '',
      codice_fiscale: '',
      regione: '',
      provincia: '',
      citta: '',
      via: '',
      civico: '',
      ruolo: 'utente',
      stato: 'attivo',
      crediti_valore_beni: 0,
      crediti_accumulati: 0,
      cauzione: 0
    };
    this.errore = '';
    this.provinceDisponibili = [];
    this.comuniDisponibili = [];
    this.cittaSelezionataInMenu = '';
    this.altroComuneAttivo = false;
  }
}