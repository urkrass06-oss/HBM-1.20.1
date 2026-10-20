# Prüfbelege zur Phase-4-Integration

Die Tests liefen am **19. Oktober 2026 (UTC)**; Dokumente und Hashbezüge wurden am **20. Oktober** abschließend geprüft. [BUILD_STATUS.md](../BUILD_STATUS.md) erklärt Ergebnisse und Grenzen, [INTEGRATION_REPORT.md](../INTEGRATION_REPORT.md) Herkunft und Reproduktion, [REMAINING_ISSUES.md](../REMAINING_ISSUES.md) die offenen Abnahmen.

- [commands.jsonl](commands.jsonl): sieben tatsächlich abgeschlossene Gradle-Aufrufe mit UTC, vollständigen Argumenten, JDK-/Checkoutpfaden, Lognamen und Exitcodes. Der lokale Logbasename entspricht jeweils der Datei unter `transcripts/`. Erfolgreiche Prozesse allein bedeuten keine erfolgreiche Asset-/Javadocprüfung.
- [transcripts.sha256](transcripts.sha256): SHA256 aller 37 archivierten Textbelege. Prüfung aus diesem Ordner: `sha256sum --check transcripts.sha256`.
- [import-manifest.json](import-manifest.json): genau drei unverändert übernommene Lizenztexte mit Quellcommit, Blob, SHA256 und Begründung. Keine allgemeine Spielquell-/Assetfreigabe.
- [rights-review.json](rights-review.json): konkrete Herkunftsanker, offene Assetfragen und Bibliotheks-Sourcevergleiche.
- [client-asset-findings.json](client-asset-findings.json): statische Nachprüfung der im Client beobachteten Fehler; nur Dateinamen/Hashes, keine übernommenen Assetbytes.
- [client-screenshot-hashes.json](client-screenshot-hashes.json): Identität lokaler Diagnosebilder. Die Bilder selbst bleiben extern; sie sind kein öffentliches Assetpaket.
- [downloads.sha256](downloads.sha256): erneut geprüfte Hashes der tatsächlich verwendeten JDK-Archive, des Wrapper-JARs und des Forge-Installers. Diese Binärdateien werden nicht mitgeliefert.
- [install-log-hashes.json](install-log-hashes.json): vollständige lokale Installerlogs mit SHA256 und Zeilenbereichen der ausdrücklich gekennzeichneten öffentlichen Auszüge. Die sehr langen pro-Klasse-Patchlisten bleiben im externen Testverzeichnis; Build-/Testlogs sind vollständig archiviert.

Wichtige Belege unter `transcripts/`:

| Dateien | Aussage |
| --- | --- |
| `20261019T212549079667Z-runData.log`, `20261019T213436314206Z-runData.log` | Datagen-Erstlauf und Wiederholung; vollständige Ausgaben. |
| `datagen-snapshot-*.log`, `datagen-integrated.log` | 7.952 geprüfte Ressourcen; identisches Inhaltsmanifest einschließlich frischem korrigiertem Checkout. |
| `20261019T213513721604Z-build-sourcesJar.log`, `20261019T214039858106Z-build-sourcesJar.log` | Builds vor und nach der Gemäldekorrektur, einschließlich der tolerierten Javadocfehler. |
| `jar-audit-integrated.log`, `packaging-final.json` | Rekursive Java-17-Prüfung, Einbettungen, ein HBM-Mod-Einstieg und endgültige JAR-Hashes. |
| `server-test.log` | Fehlversuch des Installerdownloads über urllib (HTTP 403); anschließend durch den geprüften curl-Download ersetzt. |
| `server-before-painting-fix-*` | Erster vollständiger Serverlauf mit fehlendem Gemäldetag; trotz `Done` als fehlerhaft erfasst. |
| `server-final-result.json`, `server-final-server-*.log`, `server-final-server-*.json` | Korrigierter Produktionsserver: beide Starts, Beobachtungen, Speichern, Exitcodes und sichtbare Umgebungsfehlermeldung. Bindung an den endgültigen JAR-Hash. |
| `20261019T214145521603Z-runGameTestServer.log` | 3/3 GameTests bestanden; Startmeldungen und Einschränkungen bleiben sichtbar. |
| `20261019T214654294924Z-runClient.log`, `client-observations.jsonl`, `xorg.log` | Ausgeführter Entwicklungsclient, UI-/Batteriebeobachtung, Grafikbackend und offene Clientfehler. |
| `inventory-tests.log`, `inventory-check.log` | Zwölf Original-Inventurtests bestanden, vorhandener Export unverändert verifiziert. |
| `prepare-*.log`, `reject-*.log`, `server-initial-threads*.txt` | Vorbereitungen, absichtlich abgewiesene Zielpfade und Diagnosen der langsamen initialen Spawn-Vorbereitung. |

Die Rohlogs werden nicht umformatiert; ihre ursprünglichen Warnungen, Fehler und Zeilen bleiben erhalten. Das Befehlsjournal umfasst die Gradle-Aufrufe; es wird nicht als lückenlose Aufzeichnung jedes interaktiven Shell-/UI-Schritts ausgegeben. Dieser Ordner enthält weder Mod-/Source-JARs noch Minecraft-Dateien, JDKs, Welten, EULA-Dateien oder fremde Spielassets.
