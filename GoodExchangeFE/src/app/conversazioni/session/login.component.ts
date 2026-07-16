import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { UtenteService } from '../../servizi/utente.service';
import { SessionService } from '../../servizi/session.service';
import { Utente } from '../../modelli/utente.model';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {

  // Dati del form
  username: string = '';
  password: string = '';
  
  // Messaggio di errore
  errore: string = '';

  constructor(
    private utenteService: UtenteService,
    private sessionService: SessionService,
    private router: Router
  ) {}

  // Effettua il login
  login(): void {
    this.utenteService.login(this.username, this.password).subscribe({
      next: (response: { messaggio: string; utente: Utente }) => {
        // Controlla se utente è bloccato
        if (response.utente.stato === 'disattivo') {
          this.errore = 'Il tuo account è stato bloccato. Contatta l\'assistenza.';
          return; // se è bloccato interrompe il flusso
        }
        
        // Salva utente nella sessione
        this.sessionService.setLoggedUser(response.utente);
        
        // Reindirizzo alla home
        this.router.navigate(['/home']);
      },
      error: (err) => {
        // Mostra errore
        this.errore = err.error?.detail || err.error?.errore || 'Username o password errati';
      }
    });
  }

  // Pulisce i campi del form
  clearForm(): void {
    this.username = '';
    this.password = '';
    this.errore = '';
  }
}