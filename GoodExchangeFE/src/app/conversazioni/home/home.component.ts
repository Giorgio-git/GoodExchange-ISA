import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ListaBeniComponent } from '../bene/lista-beni.component';

import { Utente } from '../../modelli/utente.model';
import { SessionService } from '../../servizi/session.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, ListaBeniComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  // variabili gestione utente
  loggedUser: Utente | null = null;
  isAdmin: boolean = false;
  isClient: boolean = false;

  constructor(
    private sessionService: SessionService,
    private router: Router
  ) { }

  vaiASuggerimento() {
    this.router.navigate(['/suggerimento']);
  }

  ngOnInit(): void {
    // iscrizione ai cambiamenti dell'utente loggato
    this.sessionService.utenteLoggato$.subscribe(user => {
      this.loggedUser = user;
      this.isAdmin = user?.ruolo === 'admin';
      this.isClient = user?.ruolo === 'utente';
    });
  }

}