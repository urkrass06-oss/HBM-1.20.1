# HBM Complete Port – Phase 4: Modernized-Integration

Tests und technische Integration: **19. Oktober 2026 (UTC)**; Abschlussprüfung: **20. Oktober 2026**. Tatsächlich ausgeführte Prüfungen und Artefakthashes: [BUILD_STATUS.md](BUILD_STATUS.md). Offene Abnahmen: [REMAINING_ISSUES.md](REMAINING_ISSUES.md).

## Ausgangsstand und Integrationsentscheidung

`origin/main` stand bei Beginn auf **`c8d2746172d9324eab8aa59ea39ac1daef9a4b19`** und enthielt nur die initiale README. Die angeforderten Phase-3-Dokumente fehlen dort. Die PRs #2, #3 und #4 sind in `docs/original-porting-plan` zusammengeführt; PR #1 gegen `main` ist noch offen. Die vollständige Arbeitsbasis ist **`811b6e822d56a94ed47ae7ec25be032e33a7bf80`**, Phase-3-Implementierung **`02de10d754c5d19d0c96496a757ab5414e91c228`**. Keine fremde Branchspitze und kein vorhandener Entwicklungsbranch wurden überschrieben oder automatisch gemergt.

Gelesen wurden [MODERNIZED_BUILD_REPORT.md](MODERNIZED_BUILD_REPORT.md), [MODERNIZED_IMPORT_CHECKLIST.md](MODERNIZED_IMPORT_CHECKLIST.md) und [MODERNIZED_MIGRATION.md](MODERNIZED_MIGRATION.md). Modernized bleibt exakt auf **[`0365cef5956016913095eeeb9366f26c601ca9a0`](https://github.com/Raptor324/HBM-Modernized/tree/0365cef5956016913095eeeb9366f26c601ca9a0)**. Die unveränderte fachliche Originalreferenz ist **[`aee05a40f10fb7bb9b042b65eccaa449ecc1672d`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/tree/aee05a40f10fb7bb9b042b65eccaa449ecc1672d)**.

**Die vollständige Integration erfolgt gemäß der ausdrücklich vorgesehenen Rückfallregel ausschließlich im temporären externen Checkout.** Einzelne Modell-/Audiorechte und die vollständige Herkunftskette des Spielquellbestands sind weiterhin offen. Öffentlich übernommen werden nur drei geprüfte Lizenztexte; Spielquellen, Assets, JARs, Minecraft-Dateien, JDKs und Testwelten werden nicht hochgeladen. Das ist eine technisch ausgeführte lokale Integration mit reproduzierbaren Skripten, kein freigegebener Vendorimport oder Release.

## Aufbau und Änderungen

| Bestandteil | Behandlung |
| --- | --- |
| Phase-3-Korrekturen | [forge-1.20.1.patch](../tools/modernized/forge-1.20.1.patch) unverändert angewendet: Forge-only, portable JDK-Auswahl, `--release 17`, entfernte `mavenLocal`-Auflösung, optionale Entwicklungsmods, deterministische Datagenmodellteile, Lizenzbeilage und korrekte Mixin-Seiten. |
| Aktive Plattform | Minecraft **1.20.1**, Forge **47.4.20**, Mod-ID **`hbm_m`**; Gradle **9.3.1** auf vollständigem JDK **21**, Mod-/Minecraftlaufzeit JDK **17**. Keine Namespace-Migration in dieser Phase. |
| Eigene Integration | [phase4-integration.patch](../tools/modernized/phase4-integration.patch): Modernized-`ForgeEntrypoint` wird eine explizite `initialize(IEventBus)`-Methode ohne zweite `@Mod`-Annotation; Build nimmt das getrennte Foundation-Overlay auf. |
| Foundation-Anbindung | Die vorhandenen drei `com.hbm`-Dateien werden ins externe `integration/src/main/java` kopiert. Nur dort wird `HbmPort` an Modernized und `RefStrings.MODID` angebunden. Bestehende Root-Dateien bleiben bytegleich; leere Foundation-Register werden nicht zusätzlich angemeldet. Modernizeds vorhandene Clientzuständigkeiten bleiben erhalten. |
| Metadaten und Hinweise | Experimentalversion `0.2.1-phase4-dev`, Port-Projektlinks, GPLv3-Gesamtkennzeichnung, bestehende Autoren/Mitwirkende und LGPL-Dateivermerke erhalten. Änderungs-/Credittext vom 19.10.2026 und geprüfte Lizenztexte liegen allen erzeugten Archiven bei. |
| GameTests | Eigenes Profil `-Pmodernized.gameTests=true`, drei Integrationstests und selbst erzeugte leere NBT-Teststruktur. Kein übernommenes fremdes Testasset. Der normale Build bindet dieses Profil nicht ein. |
| Beobachteter Ressourcenfehler | Forge-Adapter `PortPaintings` registriert die bereits referenzierte Variante `hbm_m:bober1` mit 64×48 Pixeln. Die vorhandene Datendatei allein registriert unter 1.20.1 keine PaintingVariant. Texturen, Tag und ID bleiben erhalten; der Registrierungstest prüft die tatsächliche `minecraft:placeable`-Zuordnung. |
| Bestehendes Projekt | Root-ForgeGradle-/Gradle-8.8-Foundation, Dokumente, Inventur, Lizenztexte und vollständige 140-Familien-Feature-Matrix bleiben erhalten. Root-JAR und Modernized-JAR sind verschiedene Artefakte. |

Die externe Struktur ist unter [modernized/README.md](../modernized/README.md) beschrieben. [integrate_modernized.py](../tools/integrate_modernized.py) erstellt ausschließlich neue externe Verzeichnisse, prüft beide Patches vor der Anwendung, verifiziert den offiziellen Wrapper und erzeugt `integration/provenance.json`. Dort stehen pro Upstreamdatei Git-Blob und SHA256 der unveränderten Bytes, dazu Patch-/Overlayhashes. Nicht geklärte Dateien sind ausdrücklich als `not-cleared-external-only` erfasst. Ein neuer Upstreamcommit wird nicht automatisch übernommen.

Der geprüfte korrigierte Checkout ist `/workspace/scratch/modernized-phase4/integrated`; sein Herkunftsmanifest umfasst **8.132 Upstreamdateien**. Der vorherige Checkout `modernized` und die vorbereiteten Reproduktionscheckouts bleiben außerhalb des Zielrepositorys. Die drei importierten Lizenztexte sind in einem eigenen Commit von den Integrationsanpassungen getrennt.

## Herkunfts- und Lizenzprüfung

Das [Importmanifest](integration/import-manifest.json) nennt Quellcommit, Pfad, Blob, SHA256, unveränderten Zielpfad und konkrete Begründung für die drei importierten Texte. Die Root-Lizenzen werden nicht ersetzt. Die [Rechteprüfung](integration/rights-review.json) hält die übrigen geprüften Anker und Bibliotheksvergleiche fest.

- **Modernized-GPLv3-Text:** unveränderte Kopie aus dem M-Pin; die ausdrückliche Erlaubnis zur Weitergabe des Lizenzdokuments belegt diese Textübernahme. Daraus folgt keine Assetfreigabe.
- **MixinConstraints 1.1.0:** Maven-Sources-JAR gegen **`07544882c2473ac282976f290b023c28d12c539b`** verglichen: alle **19 Java-Dateien bytegleich**. MIT-Lizenz mit **`Copyright (c) 2023 Moulberry`** unverändert übernommen und der externen Archivbeilage hinzugefügt. Keine Bibliotheksbinärdatei hochgeladen.
- **Architectury 9.2.14:** offizielles Sources-JAR SHA256 **`702f097752fff4644c27fc043ef698a6f2073cb74ab513bf53864d0f1a888ac5`** beschafft. Gegen 1.20-Commit **`22caa2810877d03f0653cbcd0e1ea0114fcf6dd0`** stimmen **141 Java-Dateien** bytegleich überein, **69** unterscheiden sich. Dieser Vergleich beweist keinen exakten Release-Gitstand; Mapping-/Buildunterschiede bleiben zu untersuchen. Der LGPLv3-Text kann als Lizenzdokument unverändert übernommen werden. Eine vollständige Freigabe der Bibliotheksdistribution wird nicht behauptet.
- **Assets:** erneut **6.720** Ressourcen, darunter **4.869 PNG**, **118 OGG**, **252 OBJ**. `cargo_door.obj` nennt **TheVitya2127**; keine individuelle Lizenz/Erlaubnis in den untersuchten Belegen gefunden. SU-47 nennt **ImageToStl.com**, einen Exporter, ohne belegten Rechteinhaber des Eingabemodells. Audio und Musik bleiben einzeln zu klären. Ungeprüfte Originalassets sind kein zulässiger pauschaler Ersatz.
- **Spielcode:** unter anderem `DamageResistanceHandler.java` mit `@author hbm (ported to 1.20.1)` erneut geprüft. GPL-Roottext, Original-LGPL, individuelle Fremdausschnitte und vollständige Ursprungskette müssen für einen öffentlichen Codeimport weiterhin zusammengeführt werden. Keine Massenfreigabe durch Dateiendung oder Verzeichnispräfix.

Die externe Modgesamtintegration ist GPLv3; bestehende Foundation-/Werkzeugdateien behalten LGPL-3.0-only. Für eine spätere Binärdistribution sind vollständiger Corresponding Source einschließlich Buildlogik, Präprozessor, Generatoren und Eingaben, Bibliotheksnachweise und sämtliche Einzelvermerke erforderlich. Ein `sources.jar` allein schließt das nicht ab.

## Reproduktion

Aus dem Checkout dieses PRs, mit vollständigen JDKs 21/17, Git, Python 3.10+, `curl` für den Forge-Installer und einem neuen externen Verzeichnis:

```bash
export HBM_PHASE4_ROOT=/workspace/scratch/modernized-phase4-neu
export JAVA21_HOME=/path/to/jdk-21
export JAVA17_HOME=/path/to/jdk-17
python3 tools/integrate_modernized.py "$HBM_PHASE4_ROOT/modernized"
python3 tools/modernized_build.py run "$HBM_PHASE4_ROOT/modernized" runData \
  --gradle-home "$HBM_PHASE4_ROOT/gradle-home" --log-dir "$HBM_PHASE4_ROOT/logs"
python3 tools/audit_modernized.py resources "$HBM_PHASE4_ROOT/modernized/src/generated/resources" \
  --output "$HBM_PHASE4_ROOT/datagen-1.sha256"
python3 tools/modernized_build.py run "$HBM_PHASE4_ROOT/modernized" runData \
  --gradle-home "$HBM_PHASE4_ROOT/gradle-home" --log-dir "$HBM_PHASE4_ROOT/logs"
python3 tools/audit_modernized.py resources "$HBM_PHASE4_ROOT/modernized/src/generated/resources" \
  --compare "$HBM_PHASE4_ROOT/datagen-1.sha256"
python3 tools/modernized_build.py run "$HBM_PHASE4_ROOT/modernized" build sourcesJar \
  --gradle-home "$HBM_PHASE4_ROOT/gradle-home" --log-dir "$HBM_PHASE4_ROOT/logs"
python3 tools/audit_modernized.py jar \
  "$HBM_PHASE4_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase4-dev+1.20.1-forge.jar"
python3 tools/test_modernized_server.py \
  "$HBM_PHASE4_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase4-dev+1.20.1-forge.jar" \
  "$HBM_PHASE4_ROOT/server" --java17-home "$JAVA17_HOME" --accept-eula
python3 tools/modernized_build.py run "$HBM_PHASE4_ROOT/modernized" runGameTestServer \
  --gradle-home "$HBM_PHASE4_ROOT/gradle-home" --log-dir "$HBM_PHASE4_ROOT/logs" \
  --gradle-arg=-Pmodernized.gameTests=true
```

Die tatsächlich verwendeten JDK-URLs und SHA256 aus Phase 3 gelten unverändert: Temurin **21.0.12.1+1** und **17.0.20.1+1** ([Downloadtabelle](MODERNIZED_BUILD_REPORT.md#downloads-und-prüfsummen)). In dieser Cloudumgebung erhält jeder `modernized_build.py run` und Servertest zusätzlich **`--trust-store /etc/ssl/certs/java/cacerts`**. HTTP(S)-Proxyvariablen bleiben erhalten; TLS-Prüfung bleibt aktiv. Andere Umgebungen verwenden ihren gültigen Truststore oder den JDK-Standard. Cache und Logs müssen außerhalb des Zielrepositorys liegen.

Der Serverhelfer verlangt die für diese Aufgabe ausdrücklich autorisierte EULA-Annahme als CLI-Flag, schreibt `eula=true` ausschließlich in das neue isolierte Testverzeichnis, bindet an **127.0.0.1**, deaktiviert RCON/Query und führt Start, Beobachtung, Speichern, Stoppen und Neustart aus. Kein bestehender Server oder Spielstand wird benutzt. Der genaue Testausgang steht separat im Buildstatus.

In der Cloud scheitert Minecrafts Yggdrasil-Public-Key-Abfrage mit `Connection refused`; die Authlib-Verbindung verwendet nicht die durchgereichten Proxyproperties. Im ausdrücklich lokalen Offline-Test kann zusätzlich `--allow-offline-auth-failure` gesetzt werden. Dann wird ausschließlich die exakt benannte Yggdrasil-Schlüsselfehlermeldung getrennt als Umgebungsfehler erfasst; sie verschwindet nicht aus dem Log oder Ergebnis. Andere `ERROR`-/`FATAL`-Zeilen bleiben Testfehler. Das ist kein Nachweis authentifizierten Mehrspielers.

Der erste Installerdownload über Python `urllib` scheiterte mit HTTP 403. Derselbe offizielle URL war über den in Phase 3 bewährten `curl`-Aufruf mit normaler Proxy-/TLS-Konfiguration erreichbar (HTTP 200, korrekter Installer-SHA256). Der Serverhelfer verwendet deshalb diesen Downloadweg; keine Zertifikats- oder Hashprüfung wurde deaktiviert. Der erste vollständige Serverstart erreichte bereits `Done`, wurde wegen des Gemäldetags und der separat aufgeführten Schlüsselabfrage aber ausdrücklich als fehlerhafter Prüflauf erfasst.

[modernized-integration.yml](../.github/workflows/modernized-integration.yml) beschreibt denselben separaten Build-/Server-/GameTestablauf. Der Workflow lädt keine Quell-/Asset-/JAR-Artefakte hoch. Seine Existenz ist kein Beleg eines bereits bestandenen GitHub-Actions-Laufs. Upstream-Publishworkflows werden nicht aktiviert.

### Clientprüfung reproduzieren

Mit einer funktionierenden grafischen Umgebung `runClient` über denselben Buildhelfer starten. Tatsächlich wurde ein Xorg-Dummy-Display mit `DISPLAY=:99 LIBGL_ALWAYS_SOFTWARE=true ALSOFT_DRIVERS=null` verwendet, zusätzlich `--gradle-arg=-Dorg.gradle.jvmargs=-Xmx1G`. Der Client selbst lief mit Java 17 und den unveränderten Upstream-Clientheapvorgaben. Der Debugstart verwendete keine optionalen Entwicklungsmods.

Im Hauptmenü Singleplayer wählen, eine kreative Superflat-Welt `Phase4IntegrationSmoke` mit Seed `42012001` und aktivierten Cheats erzeugen. Tatsächlich ausgeführt wurden `/setblock ~ ~ ~3 hbm_m:machine_battery` und `/tp @s ~ ~ ~ 0 20`; der Block lag bei `(-4,-60,6)`, der Spieler bei `(-3.5,-60,3.5)`. Die sichtbare Batterie wurde mit Rechtsklick geöffnet, das Inventarmenü beobachtet, anschließend die Welt über „Save and Quit to Title“ gespeichert und der Client über „Quit Game“ regulär beendet (Exit 0).

Dies ist eine konkrete minimale Bedienprüfung des Entwicklungsclients. Asset-/Modell-/KeyMappingfehler bleiben in [BUILD_STATUS.md](BUILD_STATUS.md) und [REMAINING_ISSUES.md](REMAINING_ISSUES.md) offen. Screenshots verbleiben ausschließlich im externen Testverzeichnis; öffentliche Belege enthalten Textlogs, Beobachtungen und Hashes. Es wurde kein öffentliches Assetpaket und kein fertiges Release erzeugt.
