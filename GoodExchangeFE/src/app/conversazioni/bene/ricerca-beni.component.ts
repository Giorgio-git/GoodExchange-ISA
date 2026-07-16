import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { BeneService } from '../../servizi/bene.service';
import { UtenteService } from '../../servizi/utente.service';
import { Utente } from '../../modelli/utente.model';
import { Bene } from '../../modelli/bene.model';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CategoriaService } from '../../servizi/categoria.service';
import { Categoria } from '../../modelli/categoria.model';
import { SessionService } from '../../servizi/session.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-ricerca-beni',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './ricerca-beni.component.html',
  styleUrls: ['./ricerca-beni.component.css']
})
export class RicercaBeniComponent implements OnInit, OnDestroy {
  beni: Bene[] = [];
  utenti: { [id: number]: Utente } = {};
  categorie: Categoria[] = [];
  error: string | null = null;
  loggedUser: Utente | null = null;
  isAdmin: boolean = false;
  isClient: boolean = false;
  immaginiBeni: { [id: number]: string | null } = {};
  private objectUrls: Array<string> = [];
  private userSub?: Subscription;

  // Campi per il template-driven form
  regione: string = '';
  provincia: string = '';
  citta: string = '';
  via: string = '';
  civico: string = '';

  constructor(
    private beneService: BeneService,
    private utenteService: UtenteService,
    private categoriaService: CategoriaService,
    private sessionService: SessionService
  ) {}

  ngOnInit(): void {
    // Carica le categorie per visualizzazione
    this.categoriaService.getCategorie().subscribe({
      next: cats => this.categorie = cats,
      error: () => this.categorie = []
    });
    // Recupera utente loggato e ruolo tramite SessionService
    this.userSub = this.sessionService.utenteLoggato$.subscribe((user: Utente | null) => {
      this.loggedUser = user;
      this.isAdmin = user?.ruolo === 'admin';
      this.isClient = user?.ruolo === 'utente';
    });
  }

  getNomeCategoria(id_categoria: number): string {
    const cat = this.categorie.find((c: Categoria) => c.id === id_categoria);
    return cat ? cat.nome : '-';
  }

  getCreditiCategoria(id_categoria: number): number {
    const cat = this.categorie.find((c: Categoria) => c.id === id_categoria);
    return cat ? cat.crediti : 0;
  }

  cercaBeni(event?: Event) {
    // Reset dell'errore
    this.error = null;
    // Costruisce l'oggetto filtri in base ai campi compilati
    const filtri: { [key: string]: string } = {};
    if (this.regione) filtri['regione'] = this.regione;
    if (this.provincia) filtri['provincia'] = this.provincia;
    if (this.citta) filtri['citta'] = this.citta;
    if (this.via) filtri['via'] = this.via;
    if (this.civico) filtri['civico'] = this.civico;

    // Richiede la lista dei beni filtrati dal BeneService
    this.beneService.getBeni(filtri).subscribe({
      next: (beni) => {
        this.beni = beni; // lista beni trovati

        // Rilascia gli URL precedenti delle immagini
        this.objectUrls.forEach((url: string) => URL.revokeObjectURL(url));
        this.objectUrls = [];
        // Per ogni bene, gestisce il caricamento dell'immagine
        this.beni.forEach((bene: Bene) => {
          if (bene.foto) {
            // Se la foto è già presente, la usa direttamente
            this.immaginiBeni[bene.id!] = bene.foto;
          } else {
            // Altrimenti la recupera tramite BeneService e crea un objectURL
            this.beneService.getImmagineBene(bene.id!).subscribe({
              next: (blob: Blob) => {
                if (blob.size > 0) {
                  const url = URL.createObjectURL(blob);
                  this.immaginiBeni[bene.id!] = url;
                  this.objectUrls.push(url);
                } else {
                  // Se il blob è vuoto, nessuna immagine disponibile
                  this.immaginiBeni[bene.id!] = null;
                }
              },
              error: () => {
                // In caso di errore, nessuna immagine disponibile
                this.immaginiBeni[bene.id!] = null;
              }
            });
          }
        });

        // Recupera i dati dei proprietari per ogni bene (serve solo a visualizzare nome proprietario)
        // OSS sfrutto l'oggetto Set che rappresenta il concetto matematico di insieme e per questo non ha duplicati
        //     dopo devo riconvertirlo in array con Array.from()
        const idsProprietari = Array.from(new Set(beni.map(b => b.id_proprietario)));
        
        idsProprietari.forEach(id => {
          // Richiede i dati dell'utente proprietario tramite UtenteService
          this.utenteService.getUtenteById(id).subscribe({
            next: (utente) => {
              this.utenti[id] = utente;
            },
            error: (err) => {
              this.error = 'Errore nel recupero dei dati dei proprietari';
            }
          });
        });
      },
      error: (err) => {
        this.error = 'Errore nel recupero dei beni';
      }
    });
  }

  ngOnDestroy(): void {
    this.userSub?.unsubscribe();
    this.objectUrls.forEach((url: string) => URL.revokeObjectURL(url));
    this.objectUrls = [];
  }
}