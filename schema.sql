CREATE TABLE utente (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  nome VARCHAR(100) NOT NULL,
  cognome VARCHAR(100) NOT NULL,
  codice_fiscale VARCHAR(16) NOT NULL UNIQUE,
  regione VARCHAR(100) NOT NULL,
  provincia VARCHAR(100) NOT NULL,
  citta VARCHAR(100) NOT NULL,
  via VARCHAR(200) NOT NULL,
  civico VARCHAR(10) NOT NULL,
  ruolo VARCHAR(20) DEFAULT 'utente' CHECK (ruolo IN ('admin','utente')),
  stato VARCHAR(20) DEFAULT 'attivo' CHECK (stato IN ('attivo','disattivo')),
  crediti_valore_beni INTEGER DEFAULT 0,
  crediti_accumulati INTEGER DEFAULT 0,
  cauzione DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_cauzione_non_negativa CHECK (cauzione >= 0),
  CONSTRAINT chk_crediti_non_negativi CHECK (crediti_valore_beni >= 0 AND crediti_accumulati >= 0)
);

CREATE TABLE categoria (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL UNIQUE,
  crediti INTEGER NOT NULL DEFAULT 0,
  descrizione TEXT
);

CREATE TABLE bene (
  id SERIAL PRIMARY KEY,
  id_proprietario INTEGER NOT NULL REFERENCES utente(id),
  id_categoria INTEGER NOT NULL REFERENCES categoria(id),
  nome VARCHAR(45) NOT NULL,
  descrizione TEXT,
  peso DECIMAL(10,3) DEFAULT NULL,
  stato BOOLEAN DEFAULT NULL,
  immagine BYTEA
);

CREATE TABLE feedback (
  id SERIAL PRIMARY KEY,
  id_utente INTEGER NOT NULL REFERENCES utente(id) ON DELETE CASCADE,
  id_destinatario INTEGER NOT NULL REFERENCES utente(id) ON DELETE CASCADE,
  voto INTEGER NOT NULL CHECK (voto >= 1 AND voto <= 5),
  data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_different_feedback_users CHECK (id_utente <> id_destinatario)
);

CREATE TABLE messaggio (
  id SERIAL PRIMARY KEY,
  id_mittente INTEGER NOT NULL REFERENCES utente(id),
  id_destinatario INTEGER NOT NULL REFERENCES utente(id),
  titolo VARCHAR(100) NOT NULL DEFAULT 'senza titolo',
  contenuto TEXT NOT NULL,
  tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('prestito','recensione','segnalazione','feedback','suggerimento')),
  id_riferito INTEGER NOT NULL
);

CREATE TABLE preferiti (
  id SERIAL PRIMARY KEY,
  id_utente INTEGER NOT NULL UNIQUE REFERENCES utente(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "preferitiItem" (
  id INTEGER NOT NULL REFERENCES preferiti(id),
  id_utente_preferito INTEGER NOT NULL REFERENCES utente(id) ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (id, id_utente_preferito)
);

CREATE TABLE prestito (
  id SERIAL PRIMARY KEY,
  id_bene INTEGER NOT NULL,
  id_proprietario INTEGER NOT NULL,
  id_beneficiario INTEGER NOT NULL REFERENCES utente(id) ON DELETE CASCADE,
  data_inizio DATE NOT NULL,
  data_fine DATE NOT NULL,
  stato VARCHAR(20) NOT NULL CHECK (stato IN ('richiesto','accettato','in_corso','completato','rifiutato','annullato')),
  data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prestito_bene FOREIGN KEY (id_bene) REFERENCES bene(id) ON DELETE CASCADE,
  CONSTRAINT fk_prestito_proprietario FOREIGN KEY (id_proprietario) REFERENCES utente(id),
  CONSTRAINT chk_date_prestito CHECK (data_fine > data_inizio)
);

CREATE TABLE recensione (
  id SERIAL PRIMARY KEY,
  id_bene INTEGER NOT NULL,
  id_beneficiario INTEGER NOT NULL REFERENCES utente(id) ON DELETE CASCADE,
  voto INTEGER NOT NULL CHECK (voto >= 1 AND voto <= 5),
  data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE segnalazione (
  id SERIAL PRIMARY KEY,
  id_segnalante INTEGER NOT NULL REFERENCES utente(id) ON DELETE CASCADE,
  id_segnalato INTEGER DEFAULT NULL REFERENCES utente(id) ON DELETE SET NULL,
  data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  stato VARCHAR(20) DEFAULT 'aperta' CHECK (stato IN ('aperta','in_gestione','risolta','respinta'))
);

CREATE TABLE suggerimento (
  id SERIAL PRIMARY KEY,
  id_mittente INTEGER NOT NULL,
  data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  stato VARCHAR(20) NOT NULL DEFAULT 'richiesto' CHECK (stato IN ('richiesto','completato'))
);

-- Creazione Indici per ottimizzazione (B+Tree)
CREATE INDEX idx_prestito_id_bene ON prestito(id_bene);
CREATE INDEX idx_prestito_id_proprietario ON prestito(id_proprietario);
CREATE INDEX idx_recensione_id_bene ON recensione(id_bene);
CREATE INDEX idx_segnalazione_bene ON segnalazione(id_segnalato);
CREATE INDEX idx_utente_citta ON utente(citta);
CREATE INDEX idx_utente_provincia ON utente(provincia);
CREATE INDEX idx_prestito_stato ON prestito(stato);
CREATE INDEX idx_bene_categoria_stato ON bene(id_categoria, stato);
CREATE INDEX idx_prestito_bene_date ON prestito(id_bene, data_inizio, data_fine);
CREATE INDEX idx_messaggio_destinatario ON messaggio(id_destinatario);
CREATE INDEX idx_feedback_destinatario_data ON feedback(id_destinatario, data DESC);
