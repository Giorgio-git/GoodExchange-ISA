import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SuggerimentoService } from '../../servizi/suggerimento.service';
import { MessaggioService } from '../../servizi/messaggio.service';
import { Suggerimento } from '../../modelli/suggerimento.model';
import { Messaggio } from '../../modelli/messaggio.model';

@Component({
  selector: 'app-lista-suggerimenti',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lista-suggerimenti.component.html',
  styleUrls: ['./lista-suggerimenti.component.css']
})
export class ListaSuggerimentiComponent implements OnInit {
  suggerimentiRichiesti: Suggerimento[] = [];
  suggerimentiCompletati: Suggerimento[] = [];
  messaggi: { [id: number]: Messaggio[] } = {};
  loading = true;

  constructor(
    private suggerimentoService: SuggerimentoService,
    private messaggioService: MessaggioService
  ) {}

  ngOnInit(): void {
    this.suggerimentoService.getAll().subscribe({
      next: suggerimenti => {
        this.suggerimentiRichiesti = suggerimenti.filter(s => s.stato === 'richiesto').sort((a, b) => a.id - b.id);
        this.suggerimentiCompletati = suggerimenti.filter(s => s.stato === 'completato').sort((a, b) => a.id - b.id);
        this.loading = false;
        // Carica i messaggi per ogni suggerimento
        [...this.suggerimentiRichiesti, ...this.suggerimentiCompletati].forEach(s => {
          this.messaggioService.getMessaggiByTipo('suggerimento', s.id).subscribe((msgs: Messaggio[]) => {
            this.messaggi[s.id] = msgs;
          });
        });
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  completaSuggerimento(s: Suggerimento) {
    this.suggerimentoService.aggiornaStato(s.id, 'completato').subscribe(() => {
      s.stato = 'completato';
      // Aggiorna le liste
      this.suggerimentiRichiesti = this.suggerimentiRichiesti.filter(x => x.id !== s.id);
      this.suggerimentiCompletati.push(s);
      this.suggerimentiCompletati.sort((a, b) => a.id - b.id);
    });
  }
}