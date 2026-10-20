# M-01: Energie- und Fluidlebensdauer

Basis: `997b15c9d60dd293e9c436663e90a95140ab13af`. Modernized bleibt bei
`0365cef5956016913095eeeb9366f26c601ca9a0`, Original bei
`aee05a40f10fb7bb9b042b65eccaa449ecc1672d`. Ziel ist ausschließlich
Minecraft 1.20.1 / Forge 47.4.23, Mod-JDK 17, Build-JDK 21 und Gradle 9.3.1.

`changes.patch` korrigiert sechs reproduzierte Fehler in fünf reservierten Dateien:

- Ein verbleibender Energieknoten behält sein Netz und kann erneut verbunden werden.
- Das Energienetz liest nur tickende Chunks und verhindert damit die normale
  Entladung nicht mehr durch ständig erneuerte Vanilla-Ladetickets.
- Wiederbelebte Drähte erhalten eine neue Capability; alte Referenzen bleiben ungültig.
- Ventile lösen ihre Netztopologie beim Entladen sofort.
- Der interne Tankfüllpfad erlaubt passende MK2-Transfers bei Druck 1–5 und hält
  Stofffilter und Kapazität ein. Forge-Container behalten die Druckprüfung für
  Umgebungsdruck. Ungültige Druckwerte werden intern nicht befüllt.
- Fluidpumpen melden Einfüllen und Entnehmen ihres Puffers zur Speicherung an.

Öffentliche Signaturen, HE-Einheiten, Registry-IDs, Rezepte, Menüs und
Paketformate bleiben erhalten. Keine zentrale Datei und kein Renderer wurde geändert.
Der zusätzlich gelieferte Paketaudit verweigert Testklassen einschließlich innerer
Klassen in Produktion sowie Änderungen außerhalb der fünf vorgesehenen Klassen
und ihrer eigenen inneren Klassen.

## Reproduktion

Alle Quellbäume, Caches, generierten Ressourcen, JARs und Welten bleiben extern.
`area.json` hält Basis- und Lieferhashes fest; `rights.json` prüft jede betroffene
Datei und den Kontext der kleinen GPLv3-Deltas. Das ist keine Freigabe des
gesamten Modernized-Bestands. Die neuen Tests und das Auditwerkzeug sind eigene
Beiträge unter LGPL-3.0-only.

Die serialisierte Bereichseinbindung ist als
[M-01-R-01](../requests/R-01-machines-tests.json) an R übergeben. Bis zu deren
Integration gilt die in `docs/PARALLEL_DEVELOPMENT.md` erlaubte gezielte Einbindung:

```bash
# Aus dem Zielrepository, mit neuen externen Verzeichnissen und vollständigen JDKs.
export HBM_CHECK_ROOT=/absolute/external/machines-unique
export HBM_JAVA21=/absolute/toolchains/jdk-21
export HBM_JAVA17=/absolute/toolchains/jdk-17
HBM_MACHINES="$PWD/tools/modernized/parallel/machines"
python3 tools/integrate_modernized.py "$HBM_CHECK_ROOT/modernized" --phase5
git -C "$HBM_CHECK_ROOT/modernized" apply --check "$HBM_MACHINES/changes.patch"
git -C "$HBM_CHECK_ROOT/modernized" apply "$HBM_MACHINES/changes.patch"
```

Zuerst G2 aus `docs/PARALLEL_DEVELOPMENT.md` vollständig ausführen: zweimal
`runData` mit Ressourcenvergleich, dann separat `build sourcesJar`, jedes Mal
`--gradle-arg=-Pdeps.forge=47.4.23`. Die Produktions-JAR auditieren, hashen und
separat sichern. Ein unabhängig reproduziertes unverändertes Phase-5-Paket hat
SHA256 `056beb76f3410d34aaf5553cfc5439e767c6b258e73edaa1366c66f05b6b77c3`.
Der zusätzliche Audit gegen dieses Paket lautet:

```bash
python3 "$HBM_MACHINES/evidence/audit_network_jar.py" \
  /absolute/external/baseline-production.jar \
  "$HBM_CHECK_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase5-dev+1.20.1-forge.jar"
```

Erst danach die genau eine neue Testdatei einbinden und das Testprofil starten:

```bash
install -D "$HBM_MACHINES/gametest/com/hbm/integration/machines/MachineNetworkTests.java" \
  "$HBM_CHECK_ROOT/modernized/integration/src/gametest/java/com/hbm/integration/machines/MachineNetworkTests.java"
python3 tools/modernized_build.py run "$HBM_CHECK_ROOT/modernized" runGameTestServer \
  --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
  --gradle-home "$HBM_CHECK_ROOT/gradle-home" --log-dir "$HBM_CHECK_ROOT/logs" \
  --gradle-arg=-Pdeps.forge=47.4.23 --gradle-arg=-Pmodernized.gameTests=true
```

In der Cloud gegebenenfalls den vorhandenen Truststore explizit über
`--trust-store /etc/ssl/certs/java/cacerts` verwenden. Proxy und TLS-Prüfung erhalten.
`HEAD` des externen Modernized-Baums bleibt am M-Pin; keine Overlays dort committen.

Erwartet werden **22 required Tests**: alle 14 unveränderten Basistests und die
acht Methoden aus `MachineNetworkTests`. G3 verlangt die tatsächliche
Ausführung und das Gesamtergebnis, nicht nur einen erfolgreichen Gradleaufruf.
Die vollständige Methodenliste steht im R-Request.

Der Entladetest nutzt entfernte Chunks außerhalb der GameTest-Arena.
Anfängliche Vanilla-Portaltickets sorgen für die Vorbereitung und laufen aus;
es gibt keinen `forcechunks`- oder `setChunkForced`-Aufruf. Der Test wartet auf
begonnenen Transfer und echte Entladung, prüft die alte Capability und verlangt
nach dem Laden eine neue BlockEntity, rekonstruierte Netze und unveränderte
20.000.000 HE / 18.000 mB. Fehlende Entladung ist ein Testfehler und kein Erfolg.
Die Arenen werden vor jedem Lauf zurückgesetzt, damit gespeicherte Restmengen
aus einem vorher gescheiterten Lauf nicht erneut als Input gezählt werden.

## Abnahmegrenzen

GameTests ersetzen weder zwei Produktionsclients noch Serverneustarts,
Singleplayer-Weltkopie oder den Original-Lauf. Die O-Verträge und ihre Grenzen
sind in [original-contracts.json ](original-contracts.json) dokumentiert;
es gibt keinen behaupteten Minecraft-1.7.10/JDK8-Messnachweis.

Offene zentrale Requests benötigen einen konkreten R-Integrationscommit.
Originalmessung und G8 nach den vier Bereichslieferungen bleiben eigene Gates.
Ein noch blockierter PR bleibt gemäß dem Entwicklungsvertrag ein Draft.
