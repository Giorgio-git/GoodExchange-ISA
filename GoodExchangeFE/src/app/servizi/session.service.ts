import { Injectable } from '@angular/core';

// BehaviorSubject = tipo speciale di Observable che mantiene l'ultimo valore emesso e lo restituisce al 
// componente che si iscrive (anche se l'iscrizione è avvenuta dopo l'emissione del valore memorizzato)
import { BehaviorSubject} from 'rxjs';
import { Utente } from '../modelli/utente.model';

@Injectable({ providedIn: 'root' })
export class SessionService {
  
  // BehaviorSubject per notificare cambiamenti utente 
  // Inizio specificandolo null perchè deve sempre avere un valore iniziale
  private utenteLoggatoSubject = new BehaviorSubject<Utente | null>(null);

  // Dichiariamo l'observable PUBBLICO utenteLoggato$ al quale si possono iscrivere tutti i componenti
  // tramite il metodo .subscribe() per ricevere aggiornamenti in tempo reale sull'utente loggato
  public utenteLoggato$ = this.utenteLoggatoSubject.asObservable();

  // OSS uso asObservable() per esporre solo l'Observable e non il BehaviorSubject che consentirebbe agli altri
  // componenti di emettere nuovi valori (cambiando ad esempio l'utente loggato).
  // In questo modo chi si iscrive può solo ricevere aggiornamenti


  constructor() {
    // Carica utente dal localStorage all'avvio
    this.caricaUtenteLoggato();
  }

  // Carica utente dal localStorage
  private caricaUtenteLoggato(): void {
    // Evita errori in SSR/server-side: localStorage esiste solo nel browser
    if (typeof window !== 'undefined' && window.localStorage) {
      // prendo l'utente salvato nel localStorage
      const raw = localStorage.getItem('utente');
      // se esiste lo converto da stringa a oggetto Utente, altrimenti è null
      const utente = raw ? JSON.parse(raw) as Utente : null;
      this.utenteLoggatoSubject.next(utente); // aggiorno il BehaviorSubject
    } else {
      this.utenteLoggatoSubject.next(null);
    }
  }

  // Restituisce l'utente loggato salvato in localStorage
  getLoggedUser(): Utente | null {
    return this.utenteLoggatoSubject.value;
  }

  // Salva l'utente loggato in localStorage dopo il login
  setLoggedUser(user: Utente): void {
    // per risolvere un problema in SSR/server-side
    if (typeof window !== 'undefined' && window.localStorage) {
      // salvataggio dell'utente nel localStorage
      localStorage.setItem('utente', JSON.stringify(user));
    }
    // Aggiorna il BehaviorSubject con il nuovo utente
    this.utenteLoggatoSubject.next(user);
  }

  // Rimuove l'utente salvato in localStorage dopo il logout
  clearLoggedUser(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('utente');
    }
    this.utenteLoggatoSubject.next(null);
    console.log('Logout effettuato, utente rimosso');
  }
}