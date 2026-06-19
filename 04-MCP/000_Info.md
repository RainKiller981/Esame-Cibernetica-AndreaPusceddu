
La metodologia con la quale ho testato questi sistemi è basata su un approccio empirico di _Trial and Error_, più che su un protocollo scientifico predefinito.

La fase di setup iniziale ha richiesto circa mezz'ora e il supporto combinato di Gemini e Antigravity CLI. L'obiettivo era modificare le impostazioni per rendere compatibile **Blender-MCP** (legato all'ecosistema Claude CLI) con **Gemini CLI**, operando principalmente con Gemini 3.1 High Pro e Claude Sonnet.

I primi test ruotavano attorno a tre interrogativi principali:

- Cosa succede se richiedo la generazione di un modello complesso?
- Come vengono strutturati gerarchicamente gli oggetti all'interno del programma?
- Qual è la differenza di output tra l'uso "puro" del server MCP con Gemini e l'integrazione di API esterne come Sketchfab?

## Fase 1: Forme Base e il Test del Velociraptor

Dopo aver generato con successo le primitive di base (la classica "sfera 1.0.1" che fa da "Hello World" in questi test) e aver verificato la capacità del sistema di applicare texture colorate in autonomia, sono passato a un soggetto organico e complesso: un velociraptor.

Lasciando operare il terminale in totale autonomia, l'output si è rivelato un conglomerato di poligoni e solidi di qualità discutibile. Sebbene la silhouette ricordasse un dinosauro, si trattava perlopiù di forme abbozzate. Da questo test sono emerse due criticità:

- Il programma tendeva a generare nuovi soggetti e forme l'uno sull'altro senza cancellare le iterazioni precedenti. Spesso creava una sorta di "scheletro" di base e una mesh esterna sovrapposti. 
  **Soluzione:** Inviare prompt di pulizia a fine generazione (es. eliminare i vecchi solidi, rimuovere gli scarti e "scollegare" lo scheletro dalla mesh principale).
- All'aumentare dei dettagli richiesti nel prompt, la macchina tendeva a produrre forme sempre più anomale e distorte. 
  **Soluzione parziale:** L'integrazione iniziale con l'API di Sketchfab ha aiutato a recuperare asset migliori in tempi rapidi, ma ha risolto il problema di modellazione solo in minima parte, costringendomi a dover sperimentare direttamente su Blender e sul terminale per eliminare parte degli oggetti generati in eccesso, che sovraccaricavano il computer e il terminale.

## Fase 2: L'Evoluzione del Workflow (Python, GEM e Agents)

La necessità di un controllo spaziale e strutturale più rigoroso ha portato a un'evoluzione significativa del metodo di lavoro:

- Creazione di un GEM dedicato, evoluto grazie ai test di ricostruzione della nave _Nostromo_ (dal film Alien), intuendo che lavorando direttamente con script Python generati dal GEM si ottenevano risultati chirurgici: posizionamento esatto, intersezioni calcolate e un setup della scena molto più pulito.
- Creazione di due agenti IA complementari (uno per compensare i punti ciechi dell'altro) progettati per supportare la lettura e l'analisi degli script Python generati dal GEM.

## Fase 3: Test Ambientali e Spaziali

Ho messo alla prova il nuovo sistema sviluppando un bar in stile western (fornendo poche indicazioni spaziali) e un armadio in stile Art Nouveau.

In entrambi i casi, l'uso di Sketchfab ha garantito un'ottima qualità visiva, ma il problema principale è diventato il **posizionamento spaziale**. 

Nel caso del bar, ho provato a fornire a Gemini un'immagine di riferimento. A una prima occhiata il risultato sembrava caotico, ma un'analisi più attenta ha rivelato un comportamento affascinante: lo script Python aveva replicato al 90% il layout bidimensionale dell'immagine, fallendo però nel tradurlo correttamente nella profondità del 3D. 
**Soluzione parziale**: Generare singolarmente i singoli elementi e fornire al Python semplici comandi su come posizionare i vari oggetti nella stanza. Da qui nasce un nuovo problema: Python non riesce a localizzare al meglio nello spazio la posizione originale degli oggetti, perdendo sempre di più con il progredire della conversazione. 

Per l'armadio, il supporto esterno è stato vitale: lasciata a se stessa, l'IA produceva design ridicoli e infantili, ben lontani dagli standard di un modellatore.
**Soluzione nulla**: nei vari tentativi non si era riuscito ottenere un risultato ottimale in nessuno dei tentativi, ma ha sottolineato l'importanza di rimanere entro un determinato limite di risposte prima che si perda completamente il compito da parte di Gemini 3.1, calcolando un totale di max. 7.
## Fase 4: Complessità, Xenomorfi e l'Inferno del Rigging

In parallelo al progetto della Nostromo II, ho tentato di generare un uovo di Xenomorfo e lo Xenomorfo stesso all'interno dello scenario. Chiedere alla macchina di modellare due soggetti complessi contemporaneamente senza API esterne ha portato a risultati molto scarsi: forme basiche, sovrapposizioni e oggetti che si auto-eliminavano.

Reintroducendo Sketchfab la qualità è tornata ad alzarsi, ma sono riemersi i bug tecnici: le mesh non si separavano dagli scheletri generati dall'IA e gli Agent ignoravano le istruzioni, continuando a sovrapporre i modelli. L'uso di Python è stato risolutivo per separare le parti, applicare le texture e fare pulizia degli scarti (che appesantivano drasticamente il rendering). Tuttavia, gli script Python forzavano i modelli a incastrarsi nella geometria della Nostromo per trovare un punto di appoggio. 
**La soluzione vincente** è stata programmare un piano invisibile (una base di appoggio neutra) su cui far spawnare i soggetti, dando a Python la possibilità di localizzare una base.

_Nota a margine:_ In un tentativo correlato a quest'ultimo, la creazione degli scheletri e i tentativi di animazione (rigging) si sono rivelati un vero e proprio inferno. Questo mi ha confermato che, per guidare efficacemente l'IA in questo specifico settore, è necessaria una profonda competenza tecnica sulle basi della modellazione 3D e dell'animazione 3D tradizionale.
## Fase 5: Ottimizzazione del Terminale e il Tempio Greco

Un tentativo impulsivo di collegare il terminale direttamente a Gemini tramite Chrome si è rivelato un passo falso, facendomi dimenticare che stavo già usando gli Agent e il terminale di Antigravity CLI. Ho dovuto riadattare il sistema di Blender-MCP al nuovo CLI, un'operazione che, grazie a Gemini Pro, ha richiesto fortunatamente solo 5 minuti.

L'ultimo test con questo setup consolidato ha riguardato la generazione di un Tempio Greco e di un albero, divisi in due approcci:

- **Generazione Procedurale Pura (Il Tempio):** Creato interamente da zero senza API. Basandomi sulle proporzioni del Partenone, la forma iniziale in low poly era esteticamente gradevole. Tuttavia, aumentando la complessità (richiedendo colonne crollate o interni dettagliati), il sistema ha iniziato a cedere, lasciando gli oggetti come solidi base vuoti e poco definiti. Sorprendentemente, la gestione autonoma delle luci e l'illuminazione ambientale hanno dato fin da subito risultati positivi.
- **Tentativo di Corruzione e Raffinamento (L'Albero):** Reintroducendo Sketchfab su un progetto già impostato, l'API ha iniziato a "corrompere" la scena, tentando di sostituire il lavoro procedurale con asset esterni di dubbia qualità. L'albero generato presentava una grande varietà di materiali e texture, ma applicati in modo dozzinale e sbrigativo. Inoltre, il sistema di screenshot automatico del terminale si è rivelato inaffidabile, producendo inquadrature pessime che ostacolavano l'analisi del risultato finale, fattore notato anche negli esperimenti precedenti solo fino a questo punto.
## Conclusioni e Sviluppi Futuri

La sperimentazione fin qui condotta dimostra che l'integrazione di Gemini con software di modellazione come Blender tramite architetture MCP è un territorio di cui ho una conoscenza ancora tecnicamente molto immatura. 
L'approccio empirico, basato sulla dinamica del _Trial and Error_ si è rivelato adeguato e necessario per mappare i reali limiti della macchina, tracciando un confine netto tra l'automazione possibile e l'imprescindibile intervento umano, aprendo però anche alla necessità di dover supportare queste sperimentazione attraverso anche a un potenziamento teorico e di maggiore ricerca basato su sperimentazioni effettuate da altri soggetti.

Il dato più importante emerso da questa fase è che **il ponte vincente tra IA e 3D non è il Text-to-3D puro, ma il Text-to-Code-to-3D.** Claude e Gemini non hanno vera consapevolezza spaziale del sistema con cui si sta interagendo, ma sono eccellenti programmatori nella loro gestione. Per supportare e migliorare la generazione futura, è necessario spostare il focus sull'istruire gli Agent a scrivere script Python sempre più rigorosi:

- L'IA ha bisogno di coordinate matematiche e basi di appoggio predefinite per capire dove far _spawnare_ o intersecare i modelli, altrimenti cercherà di fonderli tra loro. 
- Gli Agent devono essere istruiti a generare il codice a compartimenti stagni (es. una funzione per pulire la scena, una per generare la mesh, una per applicare la texture). Questo permette di isolare e correggere gli errori (come la mancata eliminazione dei solidi vecchi) senza dover rigenerare tutto da zero.
- Poiché le immagini catturate dal terminale risultano spesso inaffidabili per valutare il lavoro, è molto più efficace far scrivere a Python un output testuale dello stato della scena e darlo in pasto a Gemini/Claude per le correzioni spaziali.

Dall'analisi dei vari test, emergono pattern di comportamento molto chiari da parte dell'intelligenza artificiale:

| **Categoria** | **Elemento**                               | **Descrizione dell'Impatto**                                                                                                                                                                                                                                                           |
| ------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟢            | **Prototipazione concettuale**             | Il sistema eccelle nel generare primitive, impostare geometrie architettoniche di base e nell'assegnare materiali e colori primari. <br>Con un maggiore studio di questa dinamica è evidente come si potrebbe ottenere un risultato più avanzato se si collegano altri sistemi ed API. |
| 🟢            | **Efficacia dell'approccio procedurale**   | Costringere l'IA ad agire tramite script matematici (Python), invece di farle "immaginare" le forme, aumenta drasticamente la precisione e il controllo della scena.                                                                                                                   |
| 🔴            | **Degrado qualitativo nei dettagli**       | All'aumentare della complessità come rovine, interni o multi-soggetti, la macchina va in confusione, restituendo solidi deformi o masse caotiche.                                                                                                                                      |
| 🔴            | **Gestione delle API esterne (Sketchfab)** | Se da un lato risolvono il dettaglio visivo, dall'altro introducono "corruzione procedurale": l'IA perde il controllo della coerenza estetica e spaziale inserendo asset fuori scala o distanti dalla tematica che si sta affrontando.                                                 |
| 🔴            | **Limite strutturale del Rigging**         | La creazione di armature (_rigging_) e l'animazione si confermano attualmente ingestibili in modo puramente automatizzato.                                                                                                                                                             |

Per governare la macchina, è necessario padroneggiare la materia. Questa ricerca evidenzia che, per superare gli stalli attuali, le ore di studio devono concentrarsi non solo sull'ingegnerizzazione dei prompt, ma sulle basi della modellazione 3D tradizionale, della topologia e del rigging.

L'intelligenza artificiale, in questo contesto, esegue ciecamente. Solo fornendole una "gabbia" procedurale solida, costruita su principi di modellazione reali e governata da script Python chirurgici, si potranno ottenere, su questa linea di pensiero, maggiori risultati dal punto di vista tecnico e visivo. 

Si notifica la necessità di evolvere il sistema da mero Trial and Error in una ricerca ingegneristica più strutturata e critico-analitica, con una maggiore attenzione ai tentativi di creazione e una possibile integrazione di agenti e fattori esterni che supportino nella creazione, magari con il supporto anche di Claude Code per testare in un ambiente più avanzato.