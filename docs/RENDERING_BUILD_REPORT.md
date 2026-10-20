# R-01/R-02: Bereichsloader und Forge-Produktionsbuild

Stand: **20.10.2026 (UTC)**. Implementierung auf `port/rendering`, ausgehend vom damaligen und weiterhin aktuellen `main` **`997b15c9d60dd293e9c436663e90a95140ab13af`**. R-01 wurde zuerst implementiert und separat committed, danach R-02; Folgecommits härten die tatsächlich geprüften Gates.

## Quell- und Prüfbindung

| Bestandteil | Tatsächlich verwendet |
| --- | --- |
| Gemeinsame Bereichsbasis | `997b15c9d60dd293e9c436663e90a95140ab13af` |
| Modernized M / HEAD des externen Baums | `0365cef5956016913095eeeb9366f26c601ca9a0` |
| Original O / unveränderter Referenzpin | `aee05a40f10fb7bb9b042b65eccaa449ecc1672d`; kein neuer O-Lauf |
| Produktionsvorbereitung und Buildwerkzeuge | `acffbfd370cc5167e4a241f85fb5a8875d2ca887` |
| Korrigierter JUnit-Auswerter und Kompatibilitätslauf | `c2fdf8a429be1886bae8b1411a8782a0240c058d` |
| Explizit gewählte Rendering-Lieferung | `1536b6eff7a0fbe2f1662108ce17424e69fe036b`; identische Payloads in beiden Profilen |
| Toolchains | Gradle 9.3.1 / vollständiges Temurin-JDK 21.0.12.1; Mod, Datagen und Server mit JDK 17.0.20.1 |
| Variante / Namespace | ausschließlich `1.20.1-forge` / `hbm_m` |

Alle Patch-/Basisoverlayhashes, Liefer-/Provenienzhashes, tatsächlich ausgeführten Befehle mit Forge-Override, Exitcodes und Hashes der externen Logs stehen in [results.json](integration/rendering/results.json). Die drei Basispatches, die 14 bisherigen GameTests, Root-Foundation, deren Workflow, Lizenztexte und bisherige Rechteentscheidung sind gegenüber der gemeinsamen Basis unverändert. Der historische Provenienzschlüssel `target_base` nennt den Werkzeugcommit; der eingefrorene gemeinsame main-SHA steht in jeder Lieferung unter `manifest.baseline.target_base`.

## Implementierung R-01

Der neue Loader liest nur ausdrücklich ausgewählte, volle Git-Commit-SHAs. `policy.json` verwaltet exakte externe Dateireservierungen für die vier Bereiche und friert O/M, Basispatches und Basisoverlays ein. Payloadhashes, Patchziele, Vor-/Nachbildhashes, neue Overlayziele, separate Testpakete, pro Datei dokumentierte Rechte und gehashte Textbelege werden geprüft. Neue Reservierungen benötigen eine zentrale Änderung; eine Bereichslieferung kann ihre Allowlist nicht selbst erweitern.

Abhängigkeiten nennen Bereich, Liefercommit und API-Version. Fehlende oder zyklische Abhängigkeiten werden abgewiesen; zentrale Rendering-Requestlieferungen stehen vor Fachlieferungen. Registry-Identitäten müssen eindeutig sein, bestehende literale IDs bleiben erhalten, literale Neuzugänge müssen zum gehashten zentralen Request passen. Dynamisch gebildete Registrierungen brauchen weiterhin inhaltliches Review und Laufzeittests.

Die vollständige Auswahl wird vor Veröffentlichung des Zielbaums validiert und anschließend in einem wegwerfbaren externen Stagingbaum angewendet: Phase 3 → 4 → 5 → zentrale Requests → Bereiche. Fehler hinterlassen kein angefordertes Ziel; vorhandene Ziele werden abgewiesen. M-HEAD bleibt der Pin. Die Provenienz erfasst alle **8.148** vorbereiteten Dateien einschließlich neuer Tests, Testvertrag und Laufzeitkonfiguration mit SHA256; upstream und ungeklärte Bestände bleiben als extern/nicht zur Veröffentlichung freigegeben markiert. Herkunftsakten der eigenen Payloads liegen in der Lieferung.

**52/52 reproduzierbare Werkzeugtests bestanden.** Eigene Miniaturfixtures prüfen falsche Pins/Basishashes/Payloadhashes, fremde Dateien, Traversal, Symlinks, manipulierte Patchheader, unzulässige Patcharten, Overlaykollisionen, doppelte Ziele/Registry-IDs, bestehende und entfernte IDs, fehlende/zyklische/falsch versionierte Abhängigkeiten, ungeklärte Rechte und bestehende Ziele. Zwei unabhängige gültige Deltas sind in umgekehrter Auswahlreihenfolge bytegleich; ein gültiger zentraler Registryrequest ist ebenfalls geprüft. Paket-/Reporttests weisen u. a. neueren eingebetteten Bytecode, Testlecks, geänderte Ressourcen, Nulltests, Ersatz-IDs, Skips und falsche Forge-Versionen ab.

## Produktionsprofil und Kompatibilität R-02

| Prüfung | production / 47.4.23 | compatibility / 47.4.20 |
| --- | --- | --- |
| Frischer externer Checkout | bestanden | bestanden |
| Zwei getrennte Datagenaufrufe | Exit 0 / bytegleich | Exit 0 / bytegleich |
| Datagenmanifest | 7.952 Dateien | 7.952 Dateien |
| Separates `build sourcesJar` | Exit 0 | Exit 0 |
| Paket, Java 17, Jar-in-Jar, ein Einstieg | bestanden | bestanden |
| Zwei Produktionsserverstarts, Save/Stop | 2/2 bestanden | 2/2 bestanden |
| Required GameTests | **16/16: unveränderte 14 + 2 neue** | **16/16: unveränderte 14 + 2 neue** |

Beide Datagenmanifeste haben SHA256 **`cc5e858c1c85e6f409141d2a1eaa558731001551b3cabb1182d307a7893c2700`**, nach jedem Wiederholungslauf explizit verglichen. Alle vier Gradleaufrufe pro Profil führen denselben expliziten `-Pdeps.forge=VERSION`-Override. Widersprüchliche Overrides, kombinierte Datagen-/Buildaufrufe und Produktionspackaging mit aktiviertem Testprofil werden abgewiesen. Der bisherige 47.4.20-Pin in den externen Gradleproperties bleibt erhalten. CI führt beide Profile als getrennte Matrixjobs aus.

Die Produktions-JAR wurde jeweils vor dem Testprofil auditiert und in ein separates externes Artefaktverzeichnis gesichert. Sie enthält **16.856 Einträge**, **1.915 Klassen im äußeren Mod-JAR mit Major 61**, genau `com/hbm/HbmPort.class` als `@Mod`-Einstieg, keine Minecraft-/Forge-Plattformklassen und keine bisherigen oder neuen Bereichstestklassen/-strukturen/-verträge. Architectury 9.2.14 enthält 1× Major 52 / 381× Major 60; MixinConstraints 1.1.0 enthält 21× Major 61. Die rekursive Prüfung ist mit Java 17 kompatibel.

| Profil / Build-Forge | JAR-Bytes | Tatsächlich getesteter Produktions-JAR-SHA256 |
| --- | --- | --- |
| production / 47.4.23 | 44925653 | `17ceab39ededbda4e7896e351cd1349b01382d68f12b686543a0e2b0803d4c99` |
| compatibility / 47.4.20 | 44925653 | `17ceab39ededbda4e7896e351cd1349b01382d68f12b686543a0e2b0803d4c99` |

Die separat gegen beide Forge-Versionen gebauten Produktions-JARs sind hier bytegleich; die ausgewählten Versionen werden durch Buildbefehle, Entwicklungsartefakte und Runtime-Logs belegt.

Alle 7.952 generierten Ressourcenpfade sind vorhanden. **7.828** stimmen bytegenau mit Datagen überein. **124** bestehende Main-Ressourcen haben gemäß unveränderter `DuplicatesStrategy.EXCLUDE` Vorrang; sämtliche JAR-Bytes entsprechen dort exakt der vorhandenen Main-Datei. 48 Unterschiede betreffen nur JSON-Darstellung, 76 sind inhaltlich verschieden. Der erste strengere Audit wies diese Abweichungen ab; der Fehlbeleg bleibt extern erhalten. [resource-overrides.json](../tools/modernized/resource-overrides.json) erfasst ausschließlich die geprüften bestehenden Hashpaare. Zusätzliche oder geänderte Abweichungen scheitern weiterhin. Es wurden keine Assets ersetzt, entfernt oder als visuell korrekt freigegeben.

## Laufzeit und exakte Tests

| Forge | Start | Bis `Done` | Beobachtung | Save | Exit | Unerwartete ERROR/FATAL |
| --- | --- | --- | --- | --- | --- | --- |
| 47.4.23 | 1 | 70.731 s | 30 s | bestätigt | 0 | 0 |
| 47.4.23 | 2 | 32.756 s | 30 s | bestätigt | 0 | 0 |
| 47.4.20 | 1 | 71.595 s | 30 s | bestätigt | 0 | 0 |
| 47.4.20 | 2 | 35.401 s | 30 s | bestätigt | 0 | 0 |

Die Produktions-JAR-Hashes stimmen zwischen Build, gesicherter Datei und Serverergebnis überein. Tests sind ausschließlich an Loopback gebunden, Offlineauthentifizierung, Seed 42012001, Heap 3.072 MB. Der bekannte exakt benannte Yggdrasil-Public-Key-Fehler bleibt separat protokolliert; er ist die einzige zugelassene Umgebungsabweichung. Keine Aussage über Onlineauthentifizierung oder persistenten Fachzustand neuer M/N/W-Inhalte.

Die zwei eigenen Rendering-Tests prüfen einen alleinigen Modcontainer/Delegateneinstieg sowie den loadergenerierten Registryvertrag. Hier sind **0 neue fachliche Registrierungen** deklariert. Die bisherigen 14 Tests wurden unverändert ausgeführt. JUnit-IDs und Quellidentitäten stehen vollständig im Ergebnismanifest. Der erste Berichtsparser erwartete entgegen Forges `@PrefixGameTestTemplate(false)` Klassenpräfixe und wies den tatsächlich bereits erfolgreichen 16er-Lauf ab. Nur der Auswerter wurde korrigiert, der ursprüngliche Fehlerbeleg erhalten und derselbe vollständige JUnit-Bericht danach erfolgreich validiert. Ein neuer Miniaturtest prüft genau diesen Fall; der Kompatibilitätslauf verwendet den korrigierten Auswerter von Beginn an.

## Reproduktion und Grenzen

Werkzeugtests:

```bash
python3 -m unittest discover -s tools -p 'test_modernized_*.py' -v
```

Produktionsaufrufe verwenden `--profile production`, Kompatibilitätsaufrufe `--profile compatibility`. Je Profil einen **neuen externen** Checkout, getrennte Logs/Serverwelt und explizit die obige Rendering-Lieferung wählen:

```bash
python3 tools/integrate_modernized.py "$HBM_CHECK_ROOT/modernized" --phase5 \
  --delivery rendering@1536b6eff7a0fbe2f1662108ce17424e69fe036b
```

Danach zweimal separat `runData` über `modernized_build.py run … --profile …`, beide Ressourcenmanifeste mit `audit_modernized.py resources` vergleichen, separat `build sourcesJar`, JAR mit `--generated-source` und `--provenance` auditieren, die gesicherte JAR über `test_modernized_server.py` zweimal starten, zuletzt `runGameTestServer` und `audit_modernized.py gametests` mit XML/Log/Forge prüfen. Vollständige Befehle einschließlich expliziter JDKs und TLS-Truststore: [Ergebnismanifest](integration/rendering/results.json); automatisierte gleiche Reihenfolge: [Workflow](../.github/workflows/modernized-integration.yml).

Modernized-Vollbaum, generierte Ressourcen, Bibliotheks-/Source-/Evaluations-JARs und Welten verbleiben außerhalb öffentlicher Worktrees. Öffentlich sind nur eigene Werkzeuge/Tests und geprüfte Textmetadaten. Keine CI-Artefakt-, Source-, Asset-, Screenshot-, Welt- oder JAR-Uploads. Die [bisherige Rechteentscheidung](integration/rights-review.json), GPL-/LGPL-/MIT-Notices und der Releaseblocker bleiben bestehen.

Die bekannten **66 Javadocfehler/100 Warnungen** werden von Upstream weiterhin toleriert; `build` Exit 0 ist kein bestandener Javadocnachweis. Keine fachlichen M/N/W-Lieferungen, Client-/Renderingabnahme, neuen Originalmessungen, Zwei-Client-, Normalchunkreload- oder zweistündigen G8-Lasttests in R-01/R-02 behauptet. Diese bleiben den nachfolgenden Aufträgen vorbehalten.
