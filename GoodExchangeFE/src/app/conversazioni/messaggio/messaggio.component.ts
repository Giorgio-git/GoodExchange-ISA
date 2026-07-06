import { Component, Input } from '@angular/core';
import { Messaggio } from '../../modelli/messaggio.model';

@Component({
	selector: 'app-messaggio',
	templateUrl: './messaggio.component.html',
	styleUrls: ['./messaggio.component.css']
})
export class MessaggioComponent {
	// Dato che è un componente figlio usiamo il decoratore @Input per ricevere i dati da tutti i componenti genitori che lo implementano inserendone il template
	@Input() messaggio!: Messaggio;
	@Input() mittenteUsername?: string;
}
