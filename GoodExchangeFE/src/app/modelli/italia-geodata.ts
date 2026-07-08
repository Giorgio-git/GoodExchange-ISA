// modello scritto appositamente per riportare tutte le regioni, province e comuni d'Italia mappati gerarchicamente per il componente di registrazione


export interface ProvinciaData {
  sigla: string;
  nome: string;
  comuni: string[];
}

export interface RegioneData {
  nome: string;
  province: ProvinciaData[];
}

export const ITALIA_GEODATA: RegioneData[] = [
  {
    nome: 'Abruzzo',
    province: [
      {
        sigla: 'AQ',
        nome: "L'Aquila",
        comuni: ["L'Aquila", "Avezzano", "Sulmona", "Celano", "Pratola Peligna", "Tagliacozzo", "Castel di Sangro", "Carsoli"]
      },
      {
        sigla: 'CH',
        nome: 'Chieti',
        comuni: ["Chieti", "Vasto", "Lanciano", "Francavilla al Mare", "Ortona", "San Salvo", "Atessa", "Guardiagrele"]
      },
      {
        sigla: 'PE',
        nome: 'Pescara',
        comuni: ["Pescara", "Montesilvano", "Spoltore", "Città Sant'Angelo", "Penne", "Cepagatti", "Pianella", "Loreto Aprutino"]
      },
      {
        sigla: 'TE',
        nome: 'Teramo',
        comuni: ["Teramo", "Roseto degli Abruzzi", "Giulianova", "Martinsicuro", "Silvi", "Pineto", "Alba Adriatica", "Atri"]
      }
    ]
  },
  {
    nome: 'Basilicata',
    province: [
      {
        sigla: 'MT',
        nome: 'Matera',
        comuni: ["Matera", "Pisticci", "Policoro", "Bernalda", "Montescaglioso", "Ferrandina", "Montalbano Jonico", "Scanzano Jonico"]
      },
      {
        sigla: 'PZ',
        nome: 'Potenza',
        comuni: ["Potenza", "Melfi", "Lavello", "Rionero in Vulture", "Lauria", "Venosa", "Avigliano", "Tito"]
      }
    ]
  },
  {
    nome: 'Calabria',
    province: [
      {
        sigla: 'CZ',
        nome: 'Catanzaro',
        comuni: ["Catanzaro", "Lamezia Terme", "Soverato", "Borgia", "Curinga", "Sellia Marina", "Girifalco", "Davoli"]
      },
      {
        sigla: 'CS',
        nome: 'Cosenza',
        comuni: ["Cosenza", "Corigliano-Rossano", "Rende", "Castrovillari", "Acri", "Montalto Uffugo", "Cassano all'Ionio", "San Giovanni in Fiore", "Paola", "Amantea"]
      },
      {
        sigla: 'KR',
        nome: 'Crotone',
        comuni: ["Crotone", "Isola di Capo Rizzuto", "Cirò Marina", "Cutro", "Petilia Policastro", "Mesoraca", "Strongoli", "Rocca di Neto"]
      },
      {
        sigla: 'RC',
        nome: 'Reggio Calabria',
        comuni: ["Reggio Calabria", "Palmi", "Gioia Tauro", "Siderno", "Taurianova", "Rosarno", "Villa San Giovanni", "Locri", "Polistena", "Bagnara Calabra"]
      },
      {
        sigla: 'VV',
        nome: 'Vibo Valentia',
        comuni: ["Vibo Valentia", "Pizzo", "Mileto", "Serra San Bruno", "Tropea", "Nicotera", "Filadelfia", "Ricadi"]
      }
    ]
  },
  {
    nome: 'Campania',
    province: [
      {
        sigla: 'AV',
        nome: 'Avellino',
        comuni: ["Avellino", "Ariano Irpino", "Montoro", "Solofra", "Mercogliano", "Monteforte Irpino", "Atripalda", "Cervinara"]
      },
      {
        sigla: 'BN',
        nome: 'Benevento',
        comuni: ["Benevento", "Montesarchio", "Sant'Agata de' Goti", "San Giorgio del Sannio", "Airola", "Telese Terme", "Apice", "Guardia Sanframondi"]
      },
      {
        sigla: 'CE',
        nome: 'Caserta',
        comuni: ["Caserta", "Aversa", "Marcianise", "Maddaloni", "Santa Maria Capua Vetere", "Mondragone", "Castel Volturno", "Sessa Aurunca", "Casal di Principe", "San Felice a Cancello"]
      },
      {
        sigla: 'NA',
        nome: 'Napoli',
        comuni: ["Napoli", "Giugliano in Campania", "Torre del Greco", "Pozzuoli", "Casoria", "Castellammare di Stabia", "Afragola", "Marano di Napoli", "Portici", "Ercolano", "Casalnuovo di Napoli", "San Giorgio a Cremano", "Torre Annunziata", "Quarto", "Pomigliano d'Arco", "Melito di Napoli", "Caivano", "Sorrento"]
      },
      {
        sigla: 'SA',
        nome: 'Salerno',
        comuni: ["Salerno", "Cava de' Tirreni", "Battipaglia", "Scafati", "Nocera Inferiore", "Eboli", "Pagani", "Angri", "Sarno", "Pontecagnano Faiano", "Nocera Superiore", "Capaccio Paestum", "Agropoli"]
      }
    ]
  },
  {
    nome: 'Emilia-Romagna',
    province: [
      {
        sigla: 'BO',
        nome: 'Bologna',
        comuni: ["Bologna", "Imola", "Casalecchio di Reno", "San Lazzaro di Savena", "Valsamoggia", "San Giovanni in Persiceto", "Castel San Pietro Terme", "Zola Predosa", "Budrio", "Pianoro", "Medicina", "Castenaso", "Sasso Marconi"]
      },
      {
        sigla: 'FE',
        nome: 'Ferrara',
        comuni: [
          "Argenta", "Bondeno", "Cento", "Codigoro", "Comacchio", "Copparo", "Ferrara",
          "Fiscaglia", "Goro", "Jolanda di Savoia", "Lagosanto", "Masi Torello", "Mesola",
          "Ostellato", "Poggio Renatico", "Portomaggiore", "Riva del Po", "Terre del Reno",
          "Tresignana", "Vigarano Mainarda", "Voghiera"
        ]
      },
      {
        sigla: 'FC',
        nome: 'Forlì-Cesena',
        comuni: ["Forlì", "Cesena", "Cesenatico", "Savignano sul Rubicone", "Forlimpopoli", "San Mauro Pascoli", "Bertinoro", "Gambettola", "Meldola", "Longiano", "Gatteo"]
      },
      {
        sigla: 'MO',
        nome: 'Modena',
        comuni: ["Modena", "Carpi", "Sassuolo", "Formigine", "Castelfranco Emilia", "Vignola", "Mirandola", "Maranello", "Pavullo nel Frignano", "Fiorano Modenese", "Nonantola", "Finale Emilia", "Soliera"]
      },
      {
        sigla: 'PR',
        nome: 'Parma',
        comuni: ["Parma", "Fidenza", "Salsomaggiore Terme", "Collecchio", "Noceto", "Medesano", "Montechiarugolo", "Langhirano", "Sorbolo Mezzani", "Traversetolo"]
      },
      {
        sigla: 'PC',
        nome: 'Piacenza',
        comuni: ["Piacenza", "Fiorenzuola d'Arda", "Castel San Giovanni", "Rottofreno", "Podenzano", "Borgonovo Val Tidone", "Rivergaro", "Pontenure"]
      },
      {
        sigla: 'RA',
        nome: 'Ravenna',
        comuni: ["Ravenna", "Faenza", "Lugo", "Cervia", "Bagnacavallo", "Russi", "Alfonsine", "Conselice", "Castel Bolognese", "Brisighella"]
      },
      {
        sigla: 'RE',
        nome: 'Reggio Emilia',
        comuni: ["Reggio Emilia", "Correggio", "Scandiano", "Casalgrande", "Guastalla", "Castellarano", "Rubiera", "Novellara", "Quattro Castella", "Sant'Ilario d'Enza", "Cadelbosco di Sopra"]
      },
      {
        sigla: 'RN',
        nome: 'Rimini',
        comuni: ["Rimini", "Riccione", "Santarcangelo di Romagna", "Bellaria-Igea Marina", "Cattolica", "Misano Adriatico", "Coriano", "Verucchio", "Novafeltria", "Morciano di Romagna"]
      }
    ]
  },
  {
    nome: 'Friuli-Venezia Giulia',
    province: [
      {
        sigla: 'GO',
        nome: 'Gorizia',
        comuni: ["Gorizia", "Monfalcone", "Ronchi dei Legionari", "Grado", "Cormons", "Staranzano", "Gradisca d'Isonzo", "San Canzian d'Isonzo"]
      },
      {
        sigla: 'PN',
        nome: 'Pordenone',
        comuni: ["Pordenone", "Sacile", "Cordenons", "Azzano Decimo", "Porcia", "San Vito al Tagliamento", "Maniago", "Fiume Veneto", "Fontanafredda", "Spilimbergo"]
      },
      {
        sigla: 'TS',
        nome: 'Trieste',
        comuni: ["Trieste", "Muggia", "Duino-Aurisina", "San Dorligo della Valle", "Sgonico", "Monrupino"]
      },
      {
        sigla: 'UD',
        nome: 'Udine',
        comuni: ["Udine", "Codroipo", "Tavagnacco", "Cervignano del Friuli", "Latisana", "Cividale del Friuli", "Gemona del Friuli", "Tolmezzo", "Pasian di Prato", "Tarcento"]
      }
    ]
  },
  {
    nome: 'Lazio',
    province: [
      {
        sigla: 'FR',
        nome: 'Frosinone',
        comuni: ["Frosinone", "Cassino", "Alatri", "Sora", "Ceccano", "Ferentino", "Veroli", "Anagni", "Pontecorvo", "Monte San Giovanni Campano"]
      },
      {
        sigla: 'LT',
        nome: 'Latina',
        comuni: ["Latina", "Aprilia", "Terracina", "Formia", "Fondi", "Cisterna di Latina", "Sezze", "Gaeta", "Minturno", "Sabaudia", "Priverno", "Pontinia"]
      },
      {
        sigla: 'RI',
        nome: 'Rieti',
        comuni: ["Rieti", "Fara in Sabina", "Cittaducale", "Poggio Mirteto", "Borgorose", "Montopoli di Sabina", "Contigliano", "Magliano Sabina"]
      },
      {
        sigla: 'RM',
        nome: 'Roma',
        comuni: ["Roma", "Guidonia Montecelio", "Fiumicino", "Pomezia", "Tivoli", "Anzio", "Velletri", "Civitavecchia", "Nettuno", "Ardea", "Monterotondo", "Albano Laziale", "Marino", "Ciampino", "Cerveteri", "Fonte Nuova", "Genzano di Roma", "Mentana", "Frascati", "Colleferro"]
      },
      {
        sigla: 'VT',
        nome: 'Viterbo',
        comuni: ["Viterbo", "Civita Castellana", "Tarquinia", "Montefiascone", "Vetralla", "Nepi", "Soriano nel Cimino", "Ronciglione", "Montalto di Castro", "Capranica"]
      }
    ]
  },
  {
    nome: 'Liguria',
    province: [
      {
        sigla: 'GE',
        nome: 'Genova',
        comuni: ["Genova", "Rapallo", "Chiavari", "Sestri Levante", "Lavagna", "Arenzano", "Recco", "Santa Margherita Ligure", "Cogoleto", "Campomorone"]
      },
      {
        sigla: 'IM',
        nome: 'Imperia',
        comuni: ["Imperia", "Sanremo", "Ventimiglia", "Taggia", "Bordighera", "Vallecrosia", "Diano Marina", "Camporosso"]
      },
      {
        sigla: 'SP',
        nome: 'La Spezia',
        comuni: ["La Spezia", "Sarzana", "Arcola", "Lerici", "Santo Stefano di Magra", "Castelnuovo Magra", "Bolano", "Portovenere"]
      },
      {
        sigla: 'SV',
        nome: 'Savona',
        comuni: ["Savona", "Albenga", "Varazze", "Cairo Montenotte", "Finale Ligure", "Loano", "Alassio", "Albisola Superiore", "Pietra Ligure", "Vado Ligure"]
      }
    ]
  },
  {
    nome: 'Lombardia',
    province: [
      {
        sigla: 'BG',
        nome: 'Bergamo',
        comuni: ["Bergamo", "Treviglio", "Seriate", "Dalmine", "Romano di Lombardia", "Albino", "Caravaggio", "Alzano Lombardo", "Stezzano", "Osio Sotto", "Nembro", "Ponte San Pietro"]
      },
      {
        sigla: 'BS',
        nome: 'Brescia',
        comuni: ["Brescia", "Desenzano del Garda", "Montichiari", "Lumezzane", "Palazzolo sull'Oglio", "Rovato", "Chiari", "Ghedi", "Gussago", "Lonato del Garda", "Concesio", "Darfo Boario Terme"]
      },
      {
        sigla: 'CO',
        nome: 'Como',
        comuni: ["Como", "Cantù", "Mariano Comense", "Erba", "Olgiate Comasco", "Lurate Caccivio", "Fino Mornasco", "Turate", "Lomazzo"]
      },
      {
        sigla: 'CR',
        nome: 'Cremona',
        comuni: ["Cremona", "Crema", "Casalmaggiore", "Castelleone", "Soresina", "Pandino", "Soncino", "Rivolta d'Adda"]
      },
      {
        sigla: 'LC',
        nome: 'Lecco',
        comuni: ["Lecco", "Merate", "Calolziocorte", "Casatenovo", "Valmadrera", "Mandello del Lario", "Oggiono", "Galbiate"]
      },
      {
        sigla: 'LO',
        nome: 'Lodi',
        comuni: ["Lodi", "Codogno", "Casalpusterlengo", "Sant'Angelo Lodigiano", "Lodi Vecchio", "Zelo Buon Persico", "Tavazzano con Villavesco"]
      },
      {
        sigla: 'MN',
        nome: 'Mantova',
        comuni: ["Mantova", "Castiglione delle Stiviere", "Suzzara", "Viadana", "Porto Mantovano", "Curtatone", "Castel Goffredo", "Virgilio", "Goito", "Asola"]
      },
      {
        sigla: 'MI',
        nome: 'Milano',
        comuni: ["Milano", "Sesto San Giovanni", "Cinisello Balsamo", "Legnano", "Rho", "Cologno Monzese", "Paderno Dugnano", "Rozzano", "San Giuliano Milanese", "Pioltello", "Bollate", "Segrate", "Corsico", "Cernusco sul Naviglio", "Abbiategrasso", "San Donato Milanese", "Parabiago", "Buccinasco", "Garbagnate Milanese", "Bresso"]
      },
      {
        sigla: 'MB',
        nome: 'Monza e della Brianza',
        comuni: ["Monza", "Lissone", "Seregno", "Desio", "Cesano Maderno", "Limbiate", "Brugherio", "Vimercate", "Giussano", "Muggiò", "Seveso", "Nova Milanese", "Meda"]
      },
      {
        sigla: 'PV',
        nome: 'Pavia',
        comuni: ["Pavia", "Vigevano", "Voghera", "Mortara", "Stradella", "Gambolò", "Garlasco", "Broni", "Casorate Primo"]
      },
      {
        sigla: 'SO',
        nome: 'Sondrio',
        comuni: ["Sondrio", "Morbegno", "Tirano", "Chiavenna", "Livigno", "Cosio Valtellino", "Grosio", "Teglio"]
      },
      {
        sigla: 'VA',
        nome: 'Varese',
        comuni: ["Varese", "Busto Arsizio", "Gallarate", "Saronno", "Cassano Magnago", "Tradate", "Somma Lombardo", "Caronno Pertusella", "Malnate", "Samarate", "Cardano al Campo"]
      }
    ]
  },
  {
    nome: 'Marche',
    province: [
      {
        sigla: 'AN',
        nome: 'Ancona',
        comuni: ["Ancona", "Senigallia", "Jesi", "Osimo", "Fabriano", "Falconara Marittima", "Castelfidardo", "Chiaravalle", "Loreto", "Montemarciano"]
      },
      {
        sigla: 'AP',
        nome: 'Ascoli Piceno',
        comuni: ["Ascoli Piceno", "San Benedetto del Tronto", "Grottammare", "Monteprandone", "Folignano", "Castel di Lama", "Spinetoli"]
      },
      {
        sigla: 'FM',
        nome: 'Fermo',
        comuni: ["Fermo", "Porto Sant'Elpidio", "Porto San Giorgio", "Sant'Elpidio a Mare", "Montegranaro", "Monte Urano", "Pedaso"]
      },
      {
        sigla: 'MC',
        nome: 'Macerata',
        comuni: ["Macerata", "Civitanova Marche", "Recanati", "Tolentino", "Potenza Picena", "Corridonia", "San Severino Marche", "Porto Recanati", "Morrovalle"]
      },
      {
        sigla: 'PU',
        nome: 'Pesaro e Urbino',
        comuni: ["Pesaro", "Fano", "Vallefoglia", "Urbino", "Mondolfo", "Fossombrone", "Cagli", "Fermignano", "Tavullia", "Cartoceto"]
      }
    ]
  },
  {
    nome: 'Molise',
    province: [
      {
        sigla: 'CB',
        nome: 'Campobasso',
        comuni: ["Campobasso", "Termoli", "Bojano", "Campomarino", "Larino", "Montenero di Bisaccia", "Riccia", "Guglionesi"]
      },
      {
        sigla: 'IS',
        nome: 'Isernia',
        comuni: ["Isernia", "Venafro", "Agnone", "Frosolone", "Montaquila", "Pozzilli", "Sesto Campano"]
      }
    ]
  },
  {
    nome: 'Piemonte',
    province: [
      {
        sigla: 'AL',
        nome: 'Alessandria',
        comuni: ["Alessandria", "Casale Monferrato", "Novi Ligure", "Tortona", "Acqui Terme", "Valenza", "Ovada", "Serravalle Scrivia"]
      },
      {
        sigla: 'AT',
        nome: 'Asti',
        comuni: ["Asti", "Canelli", "Nizza Monferrato", "San Damiano d'Asti", "Costigliole d'Asti", "Villanova d'Asti"]
      },
      {
        sigla: 'BI',
        nome: 'Biella',
        comuni: ["Biella", "Cossato", "Vigliano Biellese", "Candelo", "Trivero", "Mongrando", "Valdilana"]
      },
      {
        sigla: 'CN',
        nome: 'Cuneo',
        comuni: ["Cuneo", "Alba", "Bra", "Fossano", "Mondovì", "Savigliano", "Saluzzo", "Borgo San Dalmazzo", "Busca", "Racconigi"]
      },
      {
        sigla: 'NO',
        nome: 'Novara',
        comuni: ["Novara", "Borgomanero", "Trecate", "Galliate", "Arona", "Oleggio", "Cameri", "Castelletto sopra Ticino"]
      },
      {
        sigla: 'TO',
        nome: 'Torino',
        comuni: ["Torino", "Moncalieri", "Collegno", "Rivoli", "Nichelino", "Settimo Torinese", "Grugliasco", "Chieri", "Pinerolo", "Venaria Reale", "Carmagnola", "Chivasso", "Ivrea", "Orbassano", "Rivalta di Torino", "Caselle Torinese", "San Mauro Torinese"]
      },
      {
        sigla: 'VB',
        nome: 'Verbano-Cusio-Ossola',
        comuni: ["Verbania", "Domodossola", "Omegna", "Gravellona Toce", "Villadossola", "Cannobio", "Stresa"]
      },
      {
        sigla: 'VC',
        nome: 'Vercelli',
        comuni: ["Vercelli", "Borgosesia", "Santhià", "Gattinara", "Crescentino", "Trino", "Varallo", "Serravalle Sesia"]
      }
    ]
  },
  {
    nome: 'Puglia',
    province: [
      {
        sigla: 'BA',
        nome: 'Bari',
        comuni: ["Bari", "Altamura", "Molfetta", "Bitonto", "Monopoli", "Corato", "Gravina in Puglia", "Modugno", "Gioia del Colle", "Triggiano", "Terlizzi", "Putignano", "Santeramo in Colle", "Noicattaro", "Conversano", "Mola di Bari", "Ruvo di Puglia", "Palo del Colle", "Acquaviva delle Fonti"]
      },
      {
        sigla: 'BT',
        nome: 'Barletta-Andria-Trani',
        comuni: ["Andria", "Barletta", "Trani", "Bisceglie", "Canosa di Puglia", "Trinitapoli", "San Ferdinando di Puglia", "Margherita di Savoia", "Minervino Murge", "Spinazzola"]
      },
      {
        sigla: 'BR',
        nome: 'Brindisi',
        comuni: ["Brindisi", "Fasano", "Francavilla Fontana", "Ostuni", "Mesagne", "Ceglie Messapica", "San Vito dei Normanni", "Carovigno", "Oria", "Latiano"]
      },
      {
        sigla: 'FG',
        nome: 'Foggia',
        comuni: ["Foggia", "Cerignola", "Manfredonia", "San Severo", "Lucera", "Mattinata", "Vieste", "San Giovanni Rotondo", "Torremaggiore", "Apricena", "Monte Sant'Angelo", "Orta Nova"]
      },
      {
        sigla: 'LE',
        nome: 'Lecce',
        comuni: ["Lecce", "Nardò", "Galatina", "Copertino", "Gallipoli", "Casarano", "Tricase", "Galatone", "Maglie", "Squinzano", "Veglie", "Monteroni di Lecce", "Surbo", "Trepuzzi"]
      },
      {
        sigla: 'TA',
        nome: 'Taranto',
        comuni: ["Taranto", "Martina Franca", "Massafra", "Grottaglie", "Manduria", "Ginosa", "Castellaneta", "Sava", "Palagiano", "Mottola", "San Giorgio Ionico", "Laterza"]
      }
    ]
  },
  {
    nome: 'Sardegna',
    province: [
      {
        sigla: 'CA',
        nome: 'Cagliari',
        comuni: ["Cagliari", "Quartu Sant'Elena", "Selargius", "Assemini", "Capoterra", "Monserrato", "Sestu", "Sinnai", "Quartucciu"]
      },
      {
        sigla: 'NU',
        nome: 'Nuoro',
        comuni: ["Nuoro", "Siniscola", "Macomer", "Dorgali", "Oliena", "Orosei", "Tortolì", "Lanusei"]
      },
      {
        sigla: 'OR',
        nome: 'Oristano',
        comuni: ["Oristano", "Terralba", "Cabras", "Bosa", "Marrubiu", "Santa Giusta", "Ghilarza", "Mogoro"]
      },
      {
        sigla: 'SS',
        nome: 'Sassari',
        comuni: ["Sassari", "Olbia", "Alghero", "Porto Torres", "Sorso", "Tempio Pausania", "Arzachena", "Sennori", "Ozieri", "La Maddalena"]
      },
      {
        sigla: 'SU',
        nome: 'Sud Sardegna',
        comuni: ["Carbonia", "Iglesias", "Villacidro", "Guspini", "Sant'Antioco", "Dolianova", "Serramanna", "Sanluri"]
      }
    ]
  },
  {
    nome: 'Sicilia',
    province: [
      {
        sigla: 'AG',
        nome: 'Agrigento',
        comuni: ["Agrigento", "Sciacca", "Licata", "Canicattì", "Favara", "Palma di Montechiaro", "Ribera", "Porto Empedocle", "Raffadali", "Menfi"]
      },
      {
        sigla: 'CL',
        nome: 'Caltanissetta',
        comuni: ["Caltanissetta", "Gela", "Niscemi", "San Cataldo", "Mazzarino", "Riesi", "Mussomeli", "Sommatino"]
      },
      {
        sigla: 'CT',
        nome: 'Catania',
        comuni: ["Catania", "Acireale", "Misterbianco", "Paternò", "Caltagirone", "Adrano", "Mascalucia", "Aci Catena", "Belpasso", "Giarre", "Gravina di Catania", "San Giovanni la Punta", "Tremestieri Etneo", "Biancavilla", "Palagonia"]
      },
      {
        sigla: 'EN',
        nome: 'Enna',
        comuni: ["Enna", "Piazza Armerina", "Nicosia", "Leonforte", "Barrafranca", "Troina", "Valguarnera Caropepe", "Agira"]
      },
      {
        sigla: 'ME',
        nome: 'Messina',
        comuni: ["Messina", "Barcellona Pozzo di Gotto", "Milazzo", "Patti", "Sant'Agata di Militello", "Capo d'Orlando", "Taormina", "Lipari", "Giardini-Naxos", "Santa Teresa di Riva"]
      },
      {
        sigla: 'PA',
        nome: 'Palermo',
        comuni: ["Palermo", "Bagheria", "Monreale", "Carini", "Partinico", "Misilmeri", "Termini Imerese", "Villabate", "Cefalù", "Ficarazzi", "Cinisi", "Terrasini", "Corleone"]
      },
      {
        sigla: 'RG',
        nome: 'Ragusa',
        comuni: ["Ragusa", "Vittoria", "Modica", "Comiso", "Scicli", "Pozzallo", "Ispica", "Santa Croce Camerina", "Acate"]
      },
      {
        sigla: 'SR',
        nome: 'Siracusa',
        comuni: ["Siracusa", "Augusta", "Avola", "Lentini", "Noto", "Floridia", "Pachino", "Rosolini", "Carlentini", "Melilli"]
      },
      {
        sigla: 'TP',
        nome: 'Trapani',
        comuni: ["Trapani", "Marsala", "Mazara del Vallo", "Alcamo", "Castelvetrano", "Erice", "Castellammare del Golfo", "Partanna", "Salemi", "Valderice"]
      }
    ]
  },
  {
    nome: 'Toscana',
    province: [
      {
        sigla: 'AR',
        nome: 'Arezzo',
        comuni: ["Arezzo", "Montevarchi", "Cortona", "San Giovanni Valdarno", "Sansepolcro", "Castiglion Fiorentino", "Terranuova Bracciolini", "Bibbiena"]
      },
      {
        sigla: 'FI',
        nome: 'Firenze',
        comuni: ["Firenze", "Scandicci", "Sesto Fiorentino", "Empoli", "Campi Bisenzio", "Bagno a Ripoli", "Fucecchio", "Pontassieve", "Lastra a Signa", "Signa", "Borgo San Lorenzo", "Castelfiorentino", "San Casciano in Val di Pesa", "Figline e Incisa Valdarno"]
      },
      {
        sigla: 'GR',
        nome: 'Grosseto',
        comuni: ["Grosseto", "Follonica", "Orbetello", "Monte Argentario", "Roccastrada", "Massa Marittima", "Castiglione della Pescaia", "Gavorrano"]
      },
      {
        sigla: 'LI',
        nome: 'Livorno',
        comuni: ["Livorno", "Piombino", "Rosignano Marittimo", "Cecina", "Collesalvetti", "Campiglia Marittima", "Portoferraio", "Castagneto Carducci"]
      },
      {
        sigla: 'LU',
        nome: 'Lucca',
        comuni: ["Lucca", "Viareggio", "Capannori", "Camaiore", "Pietrasanta", "Massarosa", "Altopascio", "Seravezza", "Barga", "Forte dei Marmi"]
      },
      {
        sigla: 'MS',
        nome: 'Massa-Carrara',
        comuni: ["Massa", "Carrara", "Aulla", "Fivizzano", "Pontremoli", "Montignoso"]
      },
      {
        sigla: 'PI',
        nome: 'Pisa',
        comuni: ["Pisa", "Cascina", "San Giuliano Terme", "Pontedera", "San Miniato", "Ponsacco", "Santa Croce sull'Arno", "Castelfranco di Sotto", "Volterra", "Calcinaia"]
      },
      {
        sigla: 'PT',
        nome: 'Pistoia',
        comuni: ["Pistoia", "Quarrata", "Monsummano Terme", "Pescia", "Montecatini Terme", "Agliana", "Serravalle Pistoiese", "Pieve a Nievole"]
      },
      {
        sigla: 'PO',
        nome: 'Prato',
        comuni: ["Prato", "Montemurlo", "Carmignano", "Vaiano", "Poggio a Caiano", "Vernio"]
      },
      {
        sigla: 'SI',
        nome: 'Siena',
        comuni: ["Siena", "Poggibonsi", "Colle di Val d'Elsa", "Montepulciano", "Sinalunga", "Sovicille", "Monteriggioni", "Castelnuovo Berardenga"]
      }
    ]
  },
  {
    nome: 'Trentino-Alto Adige',
    province: [
      {
        sigla: 'BZ',
        nome: 'Bolzano',
        comuni: ["Bolzano", "Merano", "Bressanone", "Laives", "Brunico", "Appiano sulla Strada del Vino", "Lana", "Caldaro sulla Strada del Vino", "Renon"]
      },
      {
        sigla: 'TN',
        nome: 'Trento',
        comuni: ["Trento", "Rovereto", "Pergine Valsugana", "Arco", "Riva del Garda", "Mori", "Ala", "Lavis", "Levico Terme", "Mezzolombardo"]
      }
    ]
  },
  {
    nome: 'Umbria',
    province: [
      {
        sigla: 'PG',
        nome: 'Perugia',
        comuni: ["Perugia", "Foligno", "Città di Castello", "Spoleto", "Gubbio", "Assisi", "Bastia Umbra", "Corciano", "Marsciano", "Todi", "Umbertide", "Castiglione del Lago"]
      },
      {
        sigla: 'TR',
        nome: 'Terni',
        comuni: ["Terni", "Orvieto", "Narni", "Amelia", "Montecastrilli", "San Gemini", "Stroncone"]
      }
    ]
  },
  {
    nome: 'Valle d\'Aosta',
    province: [
      {
        sigla: 'AO',
        nome: 'Aosta',
        comuni: ["Aosta", "Sarre", "Châtillon", "Saint-Vincent", "Quart", "Pont-Saint-Martin", "Saint-Christophe", "Gressan", "Courmayeur"]
      }
    ]
  },
  {
    nome: 'Veneto',
    province: [
      {
        sigla: 'BL',
        nome: 'Belluno',
        comuni: ["Belluno", "Feltre", "Borgo Valbelluna", "Sedico", "Ponte nelle Alpi", "Santa Giustina", "Cortina d'Ampezzo", "Cadore"]
      },
      {
        sigla: 'PD',
        nome: 'Padova',
        comuni: ["Padova", "Albignasego", "Selvazzano Dentro", "Vigonza", "Cittadella", "Abano Terme", "Piove di Sacco", "Monselice", "Este", "Cadoneghe", "Rubano", "Campodarsego"]
      },
      {
        sigla: 'RO',
        nome: 'Rovigo',
        comuni: ["Rovigo", "Adria", "Porto Viro", "Lendinara", "Occhiobello", "Badia Polesine", "Porto Tolle", "Taglio di Po"]
      },
      {
        sigla: 'TV',
        nome: 'Treviso',
        comuni: ["Treviso", "Conegliano", "Castelfranco Veneto", "Montebelluna", "Vittorio Veneto", "Mogliano Veneto", "Paese", "Oderzo", "Villorba", "Preganziol", "Vedelago"]
      },
      {
        sigla: 'VE',
        nome: 'Venezia',
        comuni: ["Venezia", "Chioggia", "San Donà di Piave", "Mira", "Spinea", "Mirano", "Jesolo", "Portogruaro", "Martellago", "Scorzè", "Santa Maria di Sala", "Cavarzere"]
      },
      {
        sigla: 'VR',
        nome: 'Verona',
        comuni: ["Verona", "Villafranca di Verona", "Legnago", "San Giovanni Lupatoto", "San Bonifacio", "Bussolengo", "Sona", "Pescantina", "Negrar di Valpolicella", "Cerea", "Bovolone", "Valeggio sul Mincio"]
      },
      {
        sigla: 'VI',
        nome: 'Vicenza',
        comuni: ["Vicenza", "Bassano del Grappa", "Schio", "Valdagno", "Arzignano", "Montecchio Maggiore", "Thiene", "Lonigo", "Romano d'Ezzelino", "Malo", "Cassola"]
      }
    ]
  }
];
