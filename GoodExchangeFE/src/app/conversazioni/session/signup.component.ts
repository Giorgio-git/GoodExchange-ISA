import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { UtenteService } from '../../servizi/utente.service';
import { Utente } from '../../modelli/utente.model';

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

  // inietto le dipendenze nel costruttore
  constructor(
    private utenteService: UtenteService, // per i servizi di utente (creaUtente)
    private router: Router  // per la navigazione dopo la registrazione
  ) {}

  signup(): void {
    this.utenteService.createUtente(this.nuovoUtente).subscribe({
      next: () => {
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.errore = err.error?.errore || 'Errore durante la registrazione';
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

  }
}