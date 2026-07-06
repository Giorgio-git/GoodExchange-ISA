import { Component, OnInit } from '@angular/core';
import { Recensione } from '../../modelli/recensione.model';
import { Messaggio } from '../../modelli/messaggio.model';
import { RecensioneService } from '../../servizi/recensione.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Bene } from '../../modelli/bene.model';
import { Utente } from '../../modelli/utente.model';
import { BeneService } from '../../servizi/bene.service';
import { PrestitoService } from '../../servizi/prestito.service';
import { CategoriaService, Categoria } from '../../servizi/categoria.service';
import { SessionService } from '../../servizi/session.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
import { MatNativeDateModule } from '@angular/material/core';
import { RouterModule } from '@angular/router';
import { UtenteService } from '../../servizi/utente.service';
import { error } from 'console';

@Component({
    selector: 'app-dettaglio-bene',
    standalone: true,
    imports: [CommonModule, FormsModule, MatDatepickerModule, MatInputModule, MatNativeDateModule, RouterModule],
    templateUrl: './dettaglio-bene.component.html',
    styleUrls: ['./dettaglio-bene.component.css']
})
export class DettaglioBeneComponent implements OnInit {
    urlImmagine: string | null = null;
    private lastObjectUrl: string | null = null;

    imgError: boolean = false;
    bene: Bene | null = null;
    recensioni: (Recensione & { messaggi: Messaggio[] })[] = [];
    mittenti: { [id: number]: Utente } = {};    // mittenti delle recensioni recuperati in questo array per mostrarne lo username
    categoria: Categoria | null = null;
    proprietario: Utente | null = null;
    loggedUser: Utente | null = null;
    isAdmin: boolean = false;
    isProprietario: boolean = false;
    loading: boolean = true;
    notFound: boolean = false;
    showEditForm: boolean = false;
    editBene: Partial<Bene> = {};
    categorieList: Categoria[] = [];
    occupiedDates: Date[] = [];
    editError: string = '';
    editSuccess: string = '';

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private beneService: BeneService,
        private categoriaService: CategoriaService,
        private sessionService: SessionService,
        private prestitoService: PrestitoService,
        private recensioneService: RecensioneService,
        private messaggioService: MessaggioService,
        private utenteService: UtenteService
    ) {}

    // Torna indietro nella cronologia del browser
    goBack(): void {
        window.history.back();
    }

    // Inizializza il componente e carica tutti i dati necessari
    ngOnInit(): void {
        // Prende l'id del bene dalla route
        const id = Number(this.route.snapshot.paramMap.get('id'));

        if (!id) return; // Se l'id non è valido, esce
        
        this.sessionService.utenteLoggato$.subscribe(user => {
            this.loggedUser = user;
            this.isAdmin = user?.ruolo === 'admin';
        });

        // Carica il bene dal servizio
        this.beneService.getBeneById(id).subscribe({
            next: (bene) => {
                console.log('[DettaglioBene] getBeneById result:', bene);
                if (!bene || !bene.id) {
                    this.notFound = true;
                    return;
                }
                this.bene = bene;
                // Verifica se l'utente loggato è il proprietario (uso i !! per covertire il valore in booleano)
                this.isProprietario = !!this.loggedUser && bene.id_proprietario === this.loggedUser.id;
                // Carica il proprietario del bene
                this.utenteService.getUtenteById(bene.id_proprietario).subscribe({
                    next: utente => {
                        this.proprietario = utente;
                    },
                    error: () => {
                        this.proprietario = null;
                    }
                });

                // Carica l'immagine associata al bene usando URL temporaneo
                this.beneService.getImmagineBene(bene.id).subscribe({
                    next: (blob) => {
                        // Rilascia l'eventuale URL precedente
                        if (this.lastObjectUrl) {
                            URL.revokeObjectURL(this.lastObjectUrl);
                            this.lastObjectUrl = null;
                        }
                        if (blob.size > 0) {
                            const objectUrl = URL.createObjectURL(blob);
                            this.urlImmagine = objectUrl;
                            this.lastObjectUrl = objectUrl;
                            this.imgError = false;
                        } else {
                            this.urlImmagine = null;
                            this.imgError = true;
                        }
                    },
                    error: (err) => {
                        if (this.lastObjectUrl) {
                            URL.revokeObjectURL(this.lastObjectUrl);
                            this.lastObjectUrl = null;
                        }
                        this.urlImmagine = null;
                        this.imgError = true;
                    }
                });

                // Carica le categorie e associa la categoria al bene
                this.categoriaService.getCategorie().subscribe({
                    next: (categorie) => {
                        this.categoria = categorie.find(c => c.id === bene.id_categoria) || null;
                        this.categorieList = categorie;
                    }
                });

                // Recupera i prestiti del bene e calcola le date occupate
                this.prestitoService.getPrestiti({ id_bene: bene.id }).subscribe(prestiti => {
                    // Filtra solo i prestiti accettati o in corso
                    const prestitiOccupanti = prestiti.filter(p => p.stato === 'accettato' || p.stato === 'in_corso');

                    this.occupiedDates = []; // Array per le date occupate
                    prestitiOccupanti.forEach(p => {
                        const start = new Date(p.data_inizio);
                        const end = new Date(p.data_fine);

                        // Aggiunge tutte le date tra inizio e fine
                        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
                            this.occupiedDates.push(new Date(d));
                        }
                    });
                });

                this.recensioneService.getRecensioni({ id_bene: bene.id }).subscribe(recensioni => {
                // Ordina le recensioni dalla più recente alla meno recente
                recensioni = recensioni.sort((a, b) => (b.id! - a.id!));

                this.recensioni = recensioni.map(recensione => ({ ...recensione, messaggi: [] }));

                this.recensioni.forEach((rec, idx) => {
                    // Carica i messaggi
                    this.messaggioService.getMessaggiByTipo('recensione', rec.id).subscribe(messaggi => {
                    this.recensioni[idx].messaggi = (messaggi || []).sort((a, b) => a.id! - b.id!);
                    });

                    // Carica il mittente solo se non già presente
                    if (!this.mittenti[rec.id_beneficiario]) {
                    this.utenteService.getUtenteById(rec.id_beneficiario).subscribe({
                        next: utente => {
                        this.mittenti[rec.id_beneficiario] = utente;
                        },
                        error: () => {
                        this.mittenti[rec.id_beneficiario] = { id: rec.id_beneficiario, username: `Utente #${rec.id_beneficiario}` } as Utente;
                        }
                    });
                    }
                });
                });
            },
            error: (err) => {
                this.loading = false;
                this.notFound = true;
                console.error('[DettaglioBene] Errore getBeneById:', err);
            }
        });
    }




    // Navigazione alla pagina di creazione prestito: attiva il componente crea-prestito passando l'id del bene
    vaiACreaPrestito(): void {
        if (this.bene && this.bene.id) {
            this.router.navigate(['/beni', this.bene.id, 'richiedi-prestito']);
        }
    }


    // Gestisce la selezione di un file immagine per l'upload
    onFileSelected(event: any) {
        if (!this.bene) return;
        const file = event.target.files[0];
        if (!file) return;
        this.beneService.uploadImmagineBene(this.bene.id!, file).subscribe({
            next: () => {
                // Dopo l'upload, ricarica l'immagine aggiornata
                this.beneService.getImmagineBene(this.bene!.id!).subscribe({
                    next: (blob) => {
                        // Rilascia l'eventuale URL precedente
                        if (this.lastObjectUrl) {
                            URL.revokeObjectURL(this.lastObjectUrl);
                            this.lastObjectUrl = null;
                        }
                        if (blob.size > 0) {
                            const objectUrl = URL.createObjectURL(blob);
                            this.urlImmagine = objectUrl;
                            this.lastObjectUrl = objectUrl;
                            this.imgError = false;
                        } else {
                            this.urlImmagine = null;
                            this.imgError = true;
                        }
                    },
                    error: (err) => {
                        if (this.lastObjectUrl) {
                            URL.revokeObjectURL(this.lastObjectUrl);
                            this.lastObjectUrl = null;
                        }
                        this.urlImmagine = null;
                        this.imgError = true;
                    }
                });
            },
            error: (err) => {
                this.imgError = true;
            }
        });
    }
    ngOnDestroy(): void {
        // Rilascia l'eventuale URL immagine generato
        if (this.lastObjectUrl) {
            URL.revokeObjectURL(this.lastObjectUrl);
            this.lastObjectUrl = null;
        }
    }

    // Mostra/nasconde il form di modifica e precompila i campi
    toggleEditForm(): void {
        if (!this.bene) return; // Se il bene non è caricato, esce

        this.showEditForm = !this.showEditForm; // Altera la visibilità del form
        if (this.showEditForm) {
            // Precompila i campi modificabili con i dati attuali
            this.editBene = {
                nome: this.bene.nome,
                descrizione: this.bene.descrizione,
                peso: this.bene.peso,
                id_categoria: this.bene.id_categoria,
                crediti_richiesti: this.bene.crediti_richiesti,
                foto: this.bene.foto
            };
            this.editError = '';
            this.editSuccess = '';
        }
    }

    // Salva le modifiche apportate al bene
    salvaModifiche(): void {
        if (!this.bene) return; // Se il bene non è caricato, esce

        // Validazione: tutti i campi obbligatori (foto non obbligatoria, crediti_richiesti non richiesto)
        if (!this.editBene.nome || !this.editBene.descrizione || !this.editBene.peso || !this.editBene.id_categoria) {
            this.editError = 'Tutti i campi sono obbligatori.';
            this.editSuccess = '';
            return;
        }
        
        // Esegue la chiamata al servizio per aggiornare il bene
        this.beneService.updateBene(this.bene.id!, this.editBene).subscribe({
            next: () => {
                this.editSuccess = 'Modifica salvata con successo!';
                this.editError = '';
                // Aggiorna la vista locale con i nuovi dati
                if (this.bene) {
                    Object.assign(this.bene, this.editBene);
                }
                this.showEditForm = false;
            },
            error: () => {
                this.editError = 'Errore nel salvataggio. Riprova.';
                this.editSuccess = '';
            }
        });
    }

}