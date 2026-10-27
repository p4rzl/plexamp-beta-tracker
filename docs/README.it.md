# Plexamp Beta Tracker

**Aggiorna Plexamp dal canale beta ufficiale Android con Obtainium.**

[English](../README.md) · Italiano · [Release APK](https://github.com/p4rzl/plexamp-beta-tracker/releases) · [Download ufficiali](https://plexamp.plex.tv/downloads.html)

Questo progetto della community copia su GitHub Releases l'APK originale indicato dal manifest beta ufficiale di Plex. Il nome del file può cambiare a ogni aggiornamento: Obtainium seguirà le nuove release. **Non è un progetto ufficiale Plex** e non modifica né firma nuovamente l'app.

## Aggiunta rapida a Obtainium

1. Installa [Obtainium](https://github.com/ImranR98/Obtainium/releases) sul dispositivo Android.
2. Apri questa guida nel browser e premi il pulsante.
3. Controlla la configurazione importata, conferma ed esegui la ricerca degli aggiornamenti.
4. Premi **Installa**. Se Android lo richiede, autorizza Obtainium a installare app sconosciute e conferma l'installazione.

[![Aggiungi a Obtainium](../assets/add-to-obtainium.svg)](https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22tv.plex.labs.plexamp%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2Fp4rzl%2Fplexamp-beta-tracker%22%2C%22author%22%3A%22Plex%2C%20Inc.%20%28unofficial%20mirror%20by%20p4rzl%29%22%2C%22name%22%3A%22Plexamp%20Beta%22%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Atrue%2C%5C%22includeDrafts%5C%22%3Afalse%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5EPlexamp-.%2A%5C%5C%5C%5C.apk%24%5C%22%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%7D%22%7D)

Il pulsante abilita già le **prerelease** e il filtro APK. Usa il servizio di reindirizzamento documentato da Obtainium, che riceve la configurazione pubblica inclusa nel link. Richiede la conferma nell'app e non installa nulla automaticamente. Se il browser o il client GitHub lo blocca, usa la procedura manuale.

## Configurazione manuale

1. Apri Obtainium → **Aggiungi app**.
2. Incolla questo URL della repository, senza puntare a un singolo APK:

   ```text
   https://github.com/p4rzl/plexamp-beta-tracker
   ```

3. Abilita **Includi prerelease** nelle opzioni della sorgente GitHub.
4. Lascia disabilitati **Includi bozze** e **Verifica ultimo tag**.
5. Filtro opzionale per il nome dell'APK: `^Plexamp-.*\.apk$`.
6. Aggiungi l'app, cerca gli aggiornamenti e installa l'APK proposto. I nomi delle opzioni possono cambiare con lingua e versione di Obtainium.

La configurazione è disponibile anche in [obtainium.json](../obtainium.json): è una configurazione per una singola app, non un backup completo. Il campo `additionalSettings` contiene intenzionalmente una stringa JSON, come nel formato di esportazione di Obtainium.

## Come funzionano gli aggiornamenti

- Controllo ogni **due ore**, con possibili ritardi di GitHub e dell'intervallo di controllo di Obtainium.
- La fonte è il [manifest Android beta ufficiale](https://plexamp.plex.tv/mobile/android-update-beta.json), non il forum o la versione desktop.
- Tutte le release del mirror sono **prerelease**, anche quando il canale beta punta temporaneamente a una versione senza suffisso `-beta`.
- Viene copiata la versione corrente al momento del controllo: le versioni sostituite fra due controlli possono essere saltate.
- Il pacchetto è quello reale di Plexamp (`tv.plex.labs.plexamp`): non si installa affiancato a un'altra copia dello stesso pacchetto. Un aggiornamento richiede firme compatibili e un codice versione accettato da Android.
- Se la versione già installata dal Play Store è più recente, attendi una beta successiva. Disinstallare può eliminare dati e download locali.
- Restano validi i requisiti di Plex per account, server e funzionalità. Questo tracker non concede abbonamenti o accessi aggiuntivi.

## Verifiche e problemi comuni

Ogni nuova release include l'APK originale, `SHA256SUMS` e `upstream.json`. Prima della pubblicazione vengono verificati integrità ZIP, firma incorporata e corrispondenza di pacchetto/versione con il manifest. Il file non viene modificato. La validità della firma non verifica in modo indipendente l'identità di Plex: non è configurata una firma Plex verificata separatamente da usare come riferimento. Il checksum rileva differenze nei file, non prova l'identità del produttore.

| Problema | Soluzione |
| --- | --- |
| Nessuna release trovata | Abilita le prerelease e disabilita la verifica dell'ultimo tag. Controlla Releases e Actions. |
| Il pulsante non apre Obtainium | Apri il link nel browser Android con Obtainium installato o usa la configurazione manuale. |
| Android rifiuta l'aggiornamento | Controlla firma e codice della versione installata. Non cancellare subito i dati. |
| Limite richieste GitHub | Attendi il ripristino o configura un tuo token GitHub in Obtainium, senza condividerlo. |
| Mirror indietro | Controlla l'ultima esecuzione in Actions; puoi usare i download ufficiali nel frattempo. |

Per sviluppo, fork e dettagli tecnici consulta il [README inglese](../README.md#development-and-running-your-own-tracker). Per segnalare problemi [apri una issue](https://github.com/p4rzl/plexamp-beta-tracker/issues/new/choose) indicando errore, versioni coinvolte e link al workflow, senza token o dati personali.

## Licenza

Codice e documentazione del tracker: [MIT](../LICENSE). Gli APK, il nome Plexamp e i marchi appartengono ai rispettivi titolari e non sono coperti dalla licenza del tracker. Plexamp è software proprietario e rimane soggetto alle proprie condizioni.
