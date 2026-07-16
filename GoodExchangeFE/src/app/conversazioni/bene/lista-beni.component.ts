import { Component, OnInit, Input, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { Bene } from '../../modelli/bene.model';
import { Utente } from '../../modelli/utente.model';
import { BeneService } from '../../servizi/bene.service';
import { SessionService } from '../../servizi/session.service';
import { CategoriaService } from '../../servizi/categoria.service';
import { Categoria } from '../../modelli/categoria.model';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-lista-beni',
  templateUrl: './lista-beni.component.html',
  styleUrls: ['./lista-beni.component.css'],
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule]
})
export class ListaBeniComponent implements OnInit, OnDestroy {
  categoriaFiltro: number | null = null;
  immaginiBeni: { [id: number]: string | null } = {};
  private objectUrls: Array<string> = [];
  private routeSub?: Subscription;
  private userSub?: Subscription;

  @Input() soloMiei: boolean = false;
  beni: Bene[] = [];
  categorie: Categoria[] = [];
  loggedUser: Utente | null = null;
  isAdmin: boolean = false;
  isClient: boolean = false; 
  searchBeni: string = '';
  regione: string = '';
  provincia: string = '';
  citta: string = '';
  via: string = '';
  civico: string = '';

  constructor(
    private beneService: BeneService,
    private sessionService: SessionService,
    private categoriaService: CategoriaService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Carica le categorie disponibili dal servizio
    this.categoriaService.getCategorie().subscribe({
      next: (categorie: Categoria[]) => {
        this.categorie = categorie;
      },
      error: (err) => {
        console.error('Errore nel caricamento categorie:', err);
        this.categorie = []; 
      }
    });

    // Sottoscrive ai parametri della route e allo stato sessione
    this.routeSub = this.route.queryParams.subscribe(params => {
      if (params['miei'] !== undefined) {
        this.soloMiei = params['miei'] === 'true' || params['miei'] === true;
      } else {
        this.soloMiei = false;
      }

      this.userSub?.unsubscribe();
      this.userSub = this.sessionService.utenteLoggato$.subscribe(user => {
        this.loggedUser = user;
        this.isAdmin = user?.ruolo === 'admin';
        this.isClient = user?.ruolo === 'utente';
        this.caricaBeni(params['search']);
      });
    });
  }

  // Carica i beni dal servizio, applicando eventuali filtri e ricerca
  caricaBeni(search?: string): void {
    let filtri: { [key: string]: string | number } = {};

    // se l'utente è nella sezione "i miei beni" metto come filtro l'id proprietario dei beni uguale al suo id
    if (this.soloMiei && this.isClient && this.loggedUser && this.loggedUser.id !== undefined) {
      filtri['id_proprietario'] = this.loggedUser.id; // Filtra per id proprietario
    }

    // Filtri per luogo
    if (this.regione) filtri['regione'] = this.regione;
    if (this.provincia) filtri['provincia'] = this.provincia;
    if (this.citta) filtri['citta'] = this.citta;
    if (this.via) filtri['via'] = this.via;
    if (this.civico) filtri['civico'] = this.civico;

    // Richiede i beni al servizio con i filtri
    this.beneService.getBeni(filtri).subscribe({
      next: (beni: Bene[]) => {
        let filtered = beni; // Array di beni ricevuti

        // Se è selezionata una categoria, filtra per categoria
        if (this.categoriaFiltro !== null) {
          filtered = filtered.filter((b: Bene) => b.id_categoria === this.categoriaFiltro);
        }

        // Se è presente una stringa di ricerca filtra sul campo nome del bene
        if (search && search.trim()) {
          const parole = search.trim().toLowerCase().split(/\s+/); // Divide la ricerca in parole usando come separatore qualunque tipo di spazio
          filtered = filtered.filter((bene: Bene) => {
            if (!bene.nome) return false; // Salta se nome mancante
            const nomeLower = bene.nome.toLowerCase(); // Nome in minuscolo
            return parole.every(parola => nomeLower.includes(parola)); // Verifica che tutte le parole siano presenti nel nome (corrispondenza parziale e case-insensitive)
          });
        }

        // manca la logica per filtrare per luogo

        this.beni = filtered; // Aggiorna array dei beni da mostrare

        // Prima di caricare nuove immagini, rilascia gli URL precedenti
        this.objectUrls.forEach((url: string) => URL.revokeObjectURL(url));
        this.objectUrls = [];

        // Carica l'immagine per ogni bene
        this.beni.forEach((bene: Bene) => {
          if (bene.foto) {
            this.immaginiBeni[bene.id!] = bene.foto; // Usa foto già presente
          } else {
            // Se non c'è foto, la richiede al servizio
            this.beneService.getImmagineBene(bene.id!).subscribe({
              next: (blob: Blob) => {
                if (blob.size > 0) {
                  const url = URL.createObjectURL(blob); // Crea url temporaneo da mettere nel src dell'immagine
                  this.immaginiBeni[bene.id!] = url; // Salva url immagine
                  this.objectUrls.push(url); // Salva url per rilascio memoria
                } else {
                  this.immaginiBeni[bene.id!] = null; // Nessuna immagine se errore
                }
              },
              error: () => {
                this.immaginiBeni[bene.id!] = null; // Nessuna immagine se errore
              }
            });
          }
        });
      },
      error: (err: any) => {
        console.error('Errore nel caricamento dei beni:', err); 
        this.beni = []; 
      }
    });
  }

  // Gestisce la ricerca dei beni dalla barra di ricerca
  onSearchBeni(): void {
    const query: string = this.searchBeni.trim(); // Prende il testo della ricerca
    this.caricaBeni(query); // Carica beni filtrati per ricerca
  }

  // Gestisce il cambio del filtro categoria
  onCategoriaFiltroChange(): void {
    // Se la select restituisce null resetta il filtro
    if (this.categoriaFiltro === null) {
      this.categoriaFiltro = null; // Nessun filtro
    } else if (!isNaN(Number(this.categoriaFiltro))) {
      this.categoriaFiltro = Number(this.categoriaFiltro); // Converte in numero
    }
    this.caricaBeni(); // Ricarica i beni con nuovo filtro
  }

  // Restituisce il nome della categoria dato l'id
  getNomeCategoria(id_categoria: number): string {
    const cat = this.categorie.find((c: Categoria) => c.id === id_categoria); // Cerca la categoria
    return cat ? cat.nome : 'Categoria sconosciuta'; // Restituisce nome o fallback
  }

  // Rilascia tutti gli URL generati e cancella sottoscrizioni quando il componente viene distrutto
  ngOnDestroy(): void {
    this.routeSub?.unsubscribe();
    this.userSub?.unsubscribe();
    this.objectUrls.forEach((url: string) => URL.revokeObjectURL(url));
    this.objectUrls = [];
  }
}