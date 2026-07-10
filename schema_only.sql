CREATE TABLE `bene` (
  `id` int NOT NULL,
  `id_proprietario` int NOT NULL,
  `id_categoria` int NOT NULL,
  `nome` varchar(45) NOT NULL,
  `descrizione` text,
  `peso` decimal(10,3) DEFAULT NULL,
  `stato` tinyint(1) DEFAULT NULL,
  `immagine` longblob,
  PRIMARY KEY (`id`),
  KEY `bene_utente_idx` (`id_proprietario`),
  KEY `bene-categoria_idx` (`id_categoria`),
  CONSTRAINT `bene-categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categoria` (`id`),
  CONSTRAINT `bene_utente` FOREIGN KEY (`id_proprietario`) REFERENCES `utente` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `categoria` (
  `id` int NOT NULL,
  `nome` varchar(100) NOT NULL,
  `crediti` int NOT NULL DEFAULT '0',
  `descrizione` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nome` (`nome`),
  KEY `idx_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `contatore` (
  `nome_tabella` varchar(50) NOT NULL,
  `ultimo_id` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`nome_tabella`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `feedback` (
  `id` int NOT NULL,
  `id_utente` int NOT NULL,
  `id_destinatario` int NOT NULL,
  `voto` int NOT NULL,
  `data` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_utente` (`id_utente`),
  KEY `idx_destinatario` (`id_destinatario`),
  KEY `idx_voto` (`voto`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`id_utente`) REFERENCES `utente` (`id`) ON DELETE CASCADE,
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`id_destinatario`) REFERENCES `utente` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_different_feedback_users` CHECK ((`id_utente` <> `id_destinatario`)),
  CONSTRAINT `feedback_chk_1` CHECK (((`voto` >= 1) and (`voto` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `messaggio` (
  `id` int NOT NULL,
  `id_mittente` int NOT NULL,
  `id_destinatario` int NOT NULL,
  `titolo` varchar(100) NOT NULL DEFAULT 'senza titolo',
  `contenuto` text NOT NULL,
  `tipo` enum('prestito','recensione','segnalazione','feedback','suggerimento') NOT NULL,
  `id_riferito` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `messaggio-mittente_idx` (`id_mittente`),
  KEY `messaggio-destinatario_idx` (`id_destinatario`),
  CONSTRAINT `messaggio-destinatario` FOREIGN KEY (`id_destinatario`) REFERENCES `utente` (`id`),
  CONSTRAINT `messaggio-mittente` FOREIGN KEY (`id_mittente`) REFERENCES `utente` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `preferiti` (
  `id` int NOT NULL,
  `id_utente` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_utente_UNIQUE` (`id_utente`),
  CONSTRAINT `id_utente` FOREIGN KEY (`id_utente`) REFERENCES `utente` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `preferitiItem` (
  `id` int NOT NULL,
  `id_utente_preferito` int NOT NULL,
  PRIMARY KEY (`id`,`id_utente_preferito`),
  KEY `id_utente_preferito` (`id_utente_preferito`),
  CONSTRAINT `id_preferito` FOREIGN KEY (`id`) REFERENCES `preferiti` (`id`),
  CONSTRAINT `id_utente_preferito` FOREIGN KEY (`id_utente_preferito`) REFERENCES `utente` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `prestito` (
  `id` int NOT NULL,
  `id_bene` int NOT NULL,
  `id_proprietario` int NOT NULL,
  `id_beneficiario` int NOT NULL,
  `data_inizio` date NOT NULL,
  `data_fine` date NOT NULL,
  `stato` enum('richiesto','accettato','in_corso','completato','rifiutato','annullato') NOT NULL,
  `data` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_utente_richiedente` (`id_beneficiario`),
  KEY `idx_date_range` (`data_inizio`,`data_fine`),
  KEY `idx_stato` (`stato`),
  CONSTRAINT `prestito_ibfk_2` FOREIGN KEY (`id_beneficiario`) REFERENCES `utente` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `recensione` (
  `id` int NOT NULL,
  `id_bene` int NOT NULL,
  `id_beneficiario` int NOT NULL,
  `voto` int NOT NULL,
  `data` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_oggetto` (`id_bene`),
  KEY `idx_acquirente` (`id_beneficiario`),
  KEY `idx_voto` (`voto`),
  CONSTRAINT `recensione_ibfk_2` FOREIGN KEY (`id_beneficiario`) REFERENCES `utente` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recensione_chk_1` CHECK (((`voto` >= 1) and (`voto` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `segnalazione` (
  `id` int NOT NULL,
  `id_segnalante` int NOT NULL,
  `id_segnalato` int DEFAULT NULL,
  `data` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `stato` enum('aperta','in_gestione','risolta','respinta') DEFAULT 'aperta',
  PRIMARY KEY (`id`),
  KEY `idx_segnalante` (`id_segnalante`),
  KEY `idx_segnalato` (`id_segnalato`),
  KEY `idx_stato` (`stato`),
  KEY `idx_data` (`data`),
  CONSTRAINT `segnalazione_ibfk_1` FOREIGN KEY (`id_segnalante`) REFERENCES `utente` (`id`) ON DELETE CASCADE,
  CONSTRAINT `segnalazione_ibfk_2` FOREIGN KEY (`id_segnalato`) REFERENCES `utente` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `suggerimento` (
  `id` int NOT NULL,
  `id_mittente` int NOT NULL,
  `data` datetime DEFAULT CURRENT_TIMESTAMP,
  `stato` enum('richiesto','completato') NOT NULL DEFAULT 'richiesto',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `utente` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `cognome` varchar(100) NOT NULL,
  `codice_fiscale` varchar(16) NOT NULL,
  `regione` varchar(100) NOT NULL,
  `provincia` varchar(100) NOT NULL,
  `citta` varchar(100) NOT NULL,
  `via` varchar(200) NOT NULL,
  `civico` varchar(10) NOT NULL,
  `ruolo` enum('admin','utente') DEFAULT 'utente',
  `stato` enum('attivo','disattivo') DEFAULT 'attivo',
  `crediti_valore_beni` int DEFAULT '0',
  `crediti_accumulati` int DEFAULT '0',
  `cauzione` decimal(10,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `codice_fiscale` (`codice_fiscale`),
  KEY `idx_username` (`username`),
  KEY `idx_codice_fiscale` (`codice_fiscale`),
  KEY `idx_ruolo` (`ruolo`),
  KEY `idx_stato` (`stato`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

