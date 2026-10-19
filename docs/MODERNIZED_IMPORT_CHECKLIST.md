# Modernized: Herkunfts- und Lizenzcheckliste vor dem Import

Stand: **19. Oktober 2026 (UTC)**. Diese Checkliste bereitet einen späteren, gesonderten Import vor. **Es wird hier kein Spielquellcode oder Assetbestand übernommen und keine pauschale Rechtefreigabe erteilt.** Der technische Prüfstand steht im [Build-Bericht](MODERNIZED_BUILD_REPORT.md); die fachlichen Anforderungen bleiben in [Vergleich](MODERNIZED_COMPARISON.md), [Migrationsplan](MODERNIZED_MIGRATION.md) und [Feature-Matrix](FEATURE_MATRIX.md) erhalten.

## 1. Verbindliche Quellen

| Rolle | Repository / fester Commit | Behandlung |
| --- | --- | --- |
| Modernized (M) | [Raptor324/HBM-Modernized @ 0365cef5956016913095eeeb9366f26c601ca9a0](https://github.com/Raptor324/HBM-Modernized/tree/0365cef5956016913095eeeb9366f26c601ca9a0) | Ausschließlich Forge `1.20.1`, zunächst unverändert `hbm_m`; kein automatisches Update auf `main`. |
| Original (O) | [HbmMods/Hbm-s-Nuclear-Tech-GIT @ aee05a40f10fb7bb9b042b65eccaa449ecc1672d](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/tree/aee05a40f10fb7bb9b042b65eccaa449ecc1672d) | Fachliche Referenz; keine erneute vollständige Rechteprüfung in Phase 3. |
| Zielbasis (Z) | [urkrass06-oss/HBM-1.20.1 @ de4bb82c477fb36ad49eeacfd0a9e65abac668c1](https://github.com/urkrass06-oss/HBM-1.20.1/tree/de4bb82c477fb36ad49eeacfd0a9e65abac668c1) | `docs/original-porting-plan`, nach Merge von PR #3. Bestehende Foundation-Dateien und LGPL-Vermerke erhalten. |

## 2. Importakte je Datei oder belegbar homogener Gruppe

Vor dem Kopieren in das öffentliche Repository ausfüllen. Eine Gruppenfreigabe benötigt eine explizite Dateiliste und eine gemeinsame belegte Rechtebasis; Verzeichnisprefix oder Dateiendung allein genügt nicht.

| Pflichtfeld | Einzutragender Nachweis |
| --- | --- |
| Identität | Quellrepository, vollständiger Commit, Originalpfad, Git-Blob-ID **und** SHA256 der unveränderten Bytes. |
| Ursprungskette | Modernized-Datei → ursprüngliche HBM-/Drittquelle, sofern übernommen; Links zu Datei, Credits, Lizenz und gegebenenfalls Erlaubnis. |
| Rechteinhaber | Konkrete Autoren/Copyrightinhaber; Konverter-, Exporter- oder Generatorname ist kein Rechteinhabernachweis. |
| Lizenz | Genaue Fassung und tatsächlicher Versionsvorbehalt, Lizenztext, Dateivermerke, Ausnahmen und erforderliche Notices. Nicht aus einem Namen oder einer Maven-Gruppe erraten. |
| Ziel | Zielpfad, Code/Asset/Generator/Bibliothek, geplante Nutzung und gegebenenfalls zugehörige Feature-Matrix-ID. |
| Änderungen | Unveränderte Erstübernahme separat; danach Patch/Commit, Änderungsbeschreibung, Datum, Autor und resultierender Hash. |
| Abnahme | Prüfer, Datum, Belege und Status `offen`, `belegt`, `ausgeschlossen` oder `ersetzt`; Ersatzquelle ebenso dokumentieren. |
| Distribution | In Source/JAR eingebunden? Lizenz-/Notice-Zielpfad, zugehöriger vollständiger Source-Download, erforderliche Relink-/Buildinformationen. |

Kopiervorlage, **noch kein freigegebener Datensatz**:

```yaml
source_repository: https://github.com/Raptor324/HBM-Modernized
source_commit: 0365cef5956016913095eeeb9366f26c601ca9a0
source_path: TODO
git_blob: TODO
sha256: TODO
original_source_chain: TODO
copyright_and_authors: TODO
license_and_evidence: TODO
notices_to_preserve: TODO
target_path: TODO
changes_and_date: TODO
feature_ids: []
reviewer_and_date: TODO
review_status: offen
distribution_and_corresponding_source: TODO
```

Hashes aus dem unveränderten Git-Objekt gewinnen, bevor Präprozessor oder Datengenerator Dateien bearbeiten:

```bash
git -C "$M" rev-parse HEAD
git -C "$M" rev-parse 'HEAD:src/main/java/com/hbm_m/powerarmor/resist/DamageResistanceHandler.java'
git -C "$M" show 'HEAD:src/main/java/com/hbm_m/powerarmor/resist/DamageResistanceHandler.java' | sha256sum
git -C "$M" ls-tree -r HEAD
```

`M` bezeichnet den externen Modernized-Checkout. Für spätere Generatorausgaben zusätzlich Generator-/Buildpatch-Hash, Eingabemanifest, Abhängigkeiten, Befehle und Ausgabehash festhalten; ein Git-Blob am Ausgangscommit existiert für neu generierte Dateien nicht.

## 3. Zu prüfende Bestände

| Bestand am M-Pin | Festgestellte Herkunft / konkreter Prüfpunkt | Status vor Import |
| --- | --- | --- |
| `src/main/java/com/hbm_m/**` (1.326 Java-Dateien laut Vergleich) | M erklärt GPLv3. Originalherkunft und fremde Ausschnitte pro Datei verfolgen; `DamageResistanceHandler.java` enthält `@author hbm (ported to 1.20.1)`. „Rewritten from scratch“ ersetzt diese Prüfung nicht. | Offen, keine Massenfreigabe. |
| `build-logic/**`, aktive Gradle-/Stonecutter-Dateien, AT, Mixins, Generatoren | Teil des notwendigen Build-/Sourcebestands. M-Pin, Phase-3-Patch und Gradle-Werkzeugherkunft getrennt nachweisen; Plattformpräprozessor erhalten. | Technisch untersucht; Lizenz-/Noticepaket für eine Distribution noch zusammenstellen. |
| `src/main/resources/**` (6.720 Dateien laut Vergleich) | Darunter 4.869 PNG, 118 OGG, 252 OBJ; zusätzlich DAE/Animationen, Strukturen, JSON und Übersetzungen gesondert erfassen. Ein Root-Lizenztext belegt nicht automatisch die Ursprungskette aller Dateien. | Offen; ungeklärte Dateien bis zur Klärung ausschließen. |
| `assets/hbm_m/models/block/doors/cargo_door.obj` | Modellvermerk `Made By TheVitya2127` erhalten; ursprüngliche Lizenz/Erlaubnis, Texturen und Änderungen dazu belegen. | Offen. |
| SU-47-Modelle, weitere exportierte Modelle | ImageToStl-/Blender-/Exporterhinweise belegen keine Rechte am Ausgangsmodell. Zugehörige Texturen und Animationen einschließen. | Offen. |
| Audio und Musik | Einzelne Quellen, Rechteinhaber und Nutzungs-/Änderungsbedingungen prüfen; Original-Credits und abweichende Drittquellen verknüpfen. | Offen, keine ungeprüfte Übernahme aus O als Ersatz. |
| Handgeschriebene und generierte Sprache/Rezepte/Modelle/Tags/Loot/Worldgen | Eingabequelle und Generatorherkunft erfassen; die zwei bereits getrackten generierten Sprachdateien von neuen Datagenausgaben trennen. Generierung klärt keine Rechte an den Eingaben. | Offen. |
| Originaldateien mit Drittvermerken | Bei späterer direkter O-Übernahme insbesondere Team-CoFH-API, CC0-markierter TConstruct-Abschnitt und Minecraft-SMP-/Generatorheader aus dem Vergleich einzeln prüfen. | Offen, kein Gegenstand dieses Imports. |
| Foundation, `tools/`, Inventur, `LICENSE`, `LICENSE.LESSER`, `third_party_licenses/` | Bestehende LGPL-3.0-only-Dateivermerke und Forge-/Gradle-Herkunft beibehalten. Eigene Dateien nicht pauschal anderen Autoren zuschreiben. | Erhaltung in diesem PR geprüft; keine Lizenzumstellung. |

## 4. Konkrete Herkunftsanker aus Phase 3

Die folgenden Hashes wurden mit `git show HEAD:<Pfad>` am M-Pin berechnet. Sie sind Identitätsnachweise und **keine Einzeldateifreigaben**.

| M-Pfad | Git-Blob | SHA256 |
| --- | --- | --- |
| `LICENSE` | `f288702d2fa16d3cdf0035b15a9fcbc552cd88e7` | `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986` |
| `gradle.properties` (Autoren/Mitwirkende) | `e2fef5b05189d10e019a03e5fbe3d4066d62f06b` | `5cf712b66eda1143b3666ccadaf3e6edc0b0ac9b75f0839dbbc7f14239c19f91` |
| `src/main/java/com/hbm_m/powerarmor/resist/DamageResistanceHandler.java` | `1e462bb55b2d990770c2f25eff387a15c1a98b0e` | `6ae8d48ad6b3984cfceeae474b7e6f5a7c57de377b02c11c0598724a161eb90c` |
| `src/main/resources/assets/hbm_m/models/block/doors/cargo_door.obj` | `777ffa3453dfd9fc24bc3fe7eb05c25601e20415` | `7b393b1721cc5a354ae722dec7e8316b1a4a1064acf2f0ed253dd124c1d2ccac` |

Autoren/Credits aus M-README und `gradle.properties` sowie aus O-README/Properties und den jeweiligen Dateien übernehmen. Die FSF-Copyrightzeile des Lizenztextes bezeichnet dessen Urheber und ersetzt keine Modcredits.

## 5. Bibliotheken und Verpackung

Die Lizenzbelege unten wurden separat aus den konkreten Maven-Artefakten gelesen. Die tatsächlichen Einbettungen im erzeugten Mod-JAR wurden zusätzlich im [Build-Bericht](MODERNIZED_BUILD_REPORT.md#java-17--und-verpackungsprüfung) mit denselben Versionen und Hashes nachgewiesen; die Lizenz-/Sourcepflichten bleiben offen.

| Artefakt | Tatsächlich gelesener Lizenzbeleg | SHA256 des heruntergeladenen JARs | Offener Schritt |
| --- | --- | --- | --- |
| `dev.architectury:architectury-forge:9.2.14` | `META-INF/mods.toml`: `GNU LGPLv3` / `LGPL-3`, Autor `shedaniel`; POM ohne Lizenztext. Im JAR keine Datei mit License-/Copying-/Notice-Namen gefunden. | `47d5eca3d83aae1ac1d4a70116727715bd7ef4c077d228fee873065cbca94687` | Vollständige Lizenz-/Copyrightbeilage und exakt zuordenbaren Quellstand beschaffen; LGPL-Pflichten für die tatsächliche Einbettung erfüllen. |
| `com.moulberry:mixinconstraints:1.1.0` | Versioniertes Maven-POM erklärt MIT, Entwickler Moulberry, Mitwirkende rdh und IThundxr; JAR ohne eigene License-/Notice-Datei. | `67e1fca9cb518f8afb356105c7816587e02880c2acca3bbdb6e08c8e967fc1be` | Zugehörigen MIT-Text **mit** Copyrightzeilen aus zugeordnetem Sourcezustand beilegen; Source-JAR allein enthält keinen gesonderten Lizenztext. |

Quellen: [Architectury-Artefaktverzeichnis](https://maven.architectury.dev/dev/architectury/architectury-forge/9.2.14/), [MixinConstraints-POM](https://repo.maven.apache.org/maven2/com/moulberry/mixinconstraints/1.1.0/mixinconstraints-1.1.0.pom). MixinConstraints-Sources-JAR wurde ebenfalls geladen, SHA256 `c6e56a3269ce080278e9cd4983d6cac9512e7a287cbc9a8d72308b505b52fe0d`. Die abgefragten Versions-Tagnamen `9.2.14*` bzw. `*1.1.0*` lieferten keine Git-Refs; daraus wurde kein Sourcecommit erfunden.

- [x] Tatsächliche Jar-in-Jar-Metadaten, eingebettete Versionen und Hashes am Phase-3-Modartefakt abgeglichen: genau Architectury und MixinConstraints, keine weitere rekursive Einbettung. Bei jedem späteren Release erneut prüfen.
- [ ] Create/Flywheel als optionale Kompilierungsabhängigkeiten behandeln; kein unbeabsichtigtes Shading oder Mitliefern.
- [ ] JEI und Entwicklungsmods nicht pauschal zu Pflichtmods machen. Der Phase-3-Patch aktiviert zusätzliche Entwicklungs-Runtimemods nur mit `-Pmodernized.devRuntime=true`; dieses Profil braucht eigene Lizenz-/Laufzeittests.
- [ ] Buildplugins, Annotation-Prozessoren, Gradle und JDKs vom ausgelieferten Modinhalt unterscheiden; bei einer eigenen Werkzeugdistribution deren Bedingungen separat erfüllen.
- [ ] Minecraft-/Forge-Entwicklungsartefakte, remappte Abhängigkeitscaches und Testwelten aus Mod-/Sourcepaketen ausschließen; vollständiger zugehöriger **Mod**-Sourcebestand bleibt erforderlich.

## 6. Freigabekriterien vor öffentlichem Quellimport oder JAR-Release

- [ ] Jede vorgesehene Datei steht im Importmanifest mit nachvollziehbarem Status; offene Pflichtressourcen sind geklärt oder durch belegte Alternativen ersetzt.
- [ ] GPLv3-konforme Gesamtwerkkennzeichnung für das Modernized-Derivat festlegen. Die bisherige reine LGPL-Gesamtbeschreibung unverändert weiterzuverwenden reicht dafür nicht. Bestehende LGPL-Dateivermerke bleiben nachvollziehbar erhalten; keine pauschale Umlizenzierung behaupten.
- [ ] M-GPL- und O-/Foundation-GPL/LGPL-Texte, individuelle Notices und tatsächliche Autoren erhalten; Änderungsvermerke mit Datum ergänzen. Keine Linkingausnahme hinzuerfinden; konkretes Plattform-/Fremdmod-Verteilungsmodell prüfen.
- [ ] Eigenständiges Projekt/Derivat klar benennen; Originalautoren und Modernized-Mitwirkende nennen. Keine offizielle Zugehörigkeit oder Markenfreigabe behaupten.
- [ ] Passenden vollständigen Corresponding Source einschließlich aktiver Buildskripte, Patch, Präprozessor, Generatoren, benötigter Eingaben und Notices je Binärrelease bereitstellen. Ein Java-`sources.jar` reicht allein nicht automatisch.
- [ ] Deterministische Datengenerierung, reobfuskiertes Forge-Artefakt, Java-17-Bytecode/API-Prüfung einschließlich Einbettungen und minimalen Dedicated-Server-/Clienttest abnehmen. Build-/Datagen-/Startfehler bleiben ausdrücklich offen.
- [ ] Import und eigene Änderungen in getrennten Commits führen; Z-/M-/O-Pins, Abhängigkeitsmanifest, Testprotokolle und Artefakthashes dem Release zuordnen.

**Entscheidung für Phase 3:** Die Herkunftsanker und offenen Nachweise sind vorbereitet. Eine allgemeine Freigabe zum Code-/Assetimport oder zur Binärveröffentlichung ist damit nicht dokumentiert.
