# RelaxER
**RelaxER** è uno strumento di tipo *rule-based Machine Learning* che si avvale di tecniche di *Active Learning* capace di eseguire task di Entity Resolution, anche in contesti in cui il numero di dati etichettati è esiguo. Il processo di **Entity Resolution**, anche chiamato *Data Matching* o *Record Linkage*, ha lo scopo di ricercare record all’interno di uno o più dataset che si riferiscono alla stessa entità del mondo reale. **RelaxER** per operare utilizza un approccio basato su funzioni di similarità per costruire delle regole volte a stabilire quando due tuple rappresentano la stessa entità attraverso delle congiunzioni di predicati.

# Installazione
Per installare **RelaxER** e tutte le sue dipendenze, scaricare il sorgente e lanciare il seguente comando nella directory:
```
pip install .
```

# Utilizzo
Il tool può essere utilizzato in due modalità:
- come libreria
- attraverso la GUI

### Libreria
**RelaxER** può essere utilizzato come libreria all'interno di un qualsiasi programma Python. Un esempio è il file [runner.py](https://github.com/EmanueleBasso/RelaxER/blob/master/runner.py).

### GUI
Per utilizzare invece **RelaxER** attraverso la GUI creare un file Python che esegue la sua applicazione grafica. Un esempio è il file [runner_gui.py](https://github.com/EmanueleBasso/RelaxER/blob/master/runner_gui.py).

## Quick Start
1. Nell'utilizzo come libreria, innanzitutto bisogna importare il tool e indicare la directory e i file di partenza:
```python
from relaxER import MatchingRules

matching_rules = MatchingRules(directory_path="dataset/BeerAdvo-RateBeer", first_table="tableA.csv", second_table="tableB.csv")
```

2. Poi bisogna eseguire il discovery delle regole sul *Labelled Set*:
```python
rule_repository = matching_rules.run_discovery(initial_pairs="labelled.csv")
```

3. Infine si possono valutare le regole ottenute sul *Test Set* e applicarle alle coppie non etichettate:
```python
matching_rules.run_eval(rule_repository, test="test.csv")

matching_rules.run_prediction(rule_repository, output="prediction.csv")
```

# Approccio
### Algoritmo di generazione delle regole
La scoperta delle regole di similarità viene effettuata in modo automatico dal sistema attraverso un algoritmo di generazione *greedy*, che sfrutta in parte il
concetto di *dominanza* per spostarsi verso punti che portano a risultati possibilmente più precisi. L’idea complessiva dell’algoritmo è generare iterativamente nuove regole a partire dal *Labelled Set* somministrato, con l’obiettivo di cercare di coprire quante più coppie etichettate possibili.

### Processo di Active Learning
L'innovazione di **RelaxER** risiede proprio nel suo particolare processo di **Active Learning** e dell'euristica utilizzata. Infatti, per trovare le regole che garantiscono le performance migliori bisognerebbe avere un gran numero di coppie etichettate. Tuttavia etichettare manualmente un sottoinsieme così grande risulta essere un processo lungo ed oneroso, infattibile per dataset reali. Per questo motivo sono state introdotte delle tecniche di *Active Learning* che permettono di ridurre notevolmente il numero di coppie che è necessario etichettare.

L’idea chiave dell’Active Learning è che mentre i **falsi positivi** possono aiutare a migliorare le regole già scoperte, i **falsi negativi** possono essere d’aiuto nello scoprire nuove regole. Lo scopo dell’Active Learning è quindi ricercare queste due tipologie di istanze e chiedere all’utente di indicare se sono un match o meno.

È stata introdotta un'euristica, la **Rule-Relaxed heuristic**, per ridurre lo spazio di ricerca dei falsi negativi, in modo da concentrarsi solo sulle regioni più promettenti. Lo scopo di questa euristica è quello di mantenere tutti i predicati di una regola già scoperta ma rilassarli di una frazione α.

Il processo di Active Learning opera quindi nel seguente modo:
1. Viene effettua un’esecuzione dell’algoritmo di generazione delle regole sul *Labelled Set* iniziale così da ottenere un primo *Rule Repository*.
2. Il sistema seleziona delle coppie di tuple probabili falsi negativi e probabili falsi positivi, e le mostra all’utente chiedendogli di etichettarle.
3. Una volta che l’utente etichetta le coppie presentate, queste ultime sono aggiunte al *Labelled Set* insieme con la label fornita dall’utente.
4. A questo punto viene rilanciato l’algoritmo di generazione delle regole sul *Labelled Set* aggiornato ottenendo un nuovo insieme di regole.

# Valutazione sperimentale
Sono stati eseguiti dei test su 5 dataset strutturati messi a disposizione dagli autori del **DeepMatcher**, uno strumento di *Deep Learning* per la risoluzione del task di Entity Resolution. I test mostrano come **RelaxER** riesca ad ottenere risultati migliori rispetto a strumenti *learning-based* in contesti in cui il Training Set è esiguo, in quanto le performance dei sistemi di Machine Learning e Deep Learning degradano nel momento in cui ci sono pochi dati etichettati. Inoltre RelaxER ha il vantaggio di generare delle regole che sono facilmente interpretabili e comprensibili dall’essere umano, perfino per un utente non esperto.

I test mostrano anche come **RelaxER** tenda a dare risultati non buoni in contesti in cui sono presenti molti valori nulli oppure in cui sono presenti attributi testuali contenenti stringhe molto lunghe (i.e. attributi descrittivi).
