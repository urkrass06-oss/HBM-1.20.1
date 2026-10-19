# Entwicklung und Validierung des Grundgerüsts

Dieses Arbeitspaket beginnt die technischen Grundlagen aus P1 und ergänzt die statische P0-Inventur. Es implementiert keine Originalmaschinen, Gegenstände, Weltgenerierung oder Simulation. P0 und P1 sind noch nicht vollständig abgeschlossen; die [Feature-Matrix](FEATURE_MATRIX.md) erfasst den Unterschied zwischen technischem Einstieg und portiertem Originalinhalt.

## Festgelegte Werkzeuge und Herkunft

| Bestandteil | Festgelegter Stand | Quelle |
| --- | --- | --- |
| Minecraft / Java | `1.20.1` / JDK `17` | Gradle-Toolchain und Java-Bytecodeziel 17 |
| Forge | `47.4.10`, am 19.10.2026 als `1.20.1-recommended` gemeldet | [Offizielle Promotions](https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json), [MDK](https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.4.10/forge-1.20.1-47.4.10-mdk.zip) |
| ForgeGradle | `6.0.54` ohne dynamischen Versionsbereich | [Forge-Maven](https://maven.minecraftforge.net/net/minecraftforge/gradle/ForgeGradle/6.0.54/) |
| Gradle | `8.8` | [Distribution](https://services.gradle.org/distributions/gradle-8.8-bin.zip), [SHA256](https://services.gradle.org/distributions/gradle-8.8-bin.zip.sha256) |
| Wrapper-Bootstrap und Startskripte | Offizieller Gradle-Tag `v8.8.0` | [Wrapper-JAR](https://github.com/gradle/gradle/blob/v8.8.0/gradle/wrapper/gradle-wrapper.jar), [Prüfsummen](https://gradle.org/release-checksums/) |
| Mappings | Mojang `official`, `1.20.1` | ForgeGradle-Konfiguration; keine zusätzlichen Parchment-/NeoForge-Abhängigkeiten |

Die SHA256 der Distribution lautet `a4b4158601f8636cdeeab09bd76afb640030bb5b144aafe261a5e8af027dc612`, die der Wrapper-JAR `cb0da6751c2b753a16ac168bb354870ebb1e162e9083f116729cec9c781156b8`. Der Wrapper prüft den Distributionsdownload. Das MDK benennt ebenfalls Gradle 8.8, sein beigelegtes Bootstrap-JAR stimmte jedoch nicht mit dem offiziellen 8.8-JAR überein; deshalb werden JAR und Startskripte gemeinsam aus dem offiziellen Gradle-Tag verwendet. Das ist eine technische Herkunftsentscheidung, keine Änderung des Originals.

Die direkten Werkzeugversionen sind fixiert. Ein vollständiger Lock sämtlicher transitiver Buildartefakte und ein Nachweis bitidentischer Builds sind damit noch nicht erbracht.

## Build und Entwicklungsstarts

1. Ein JDK 17 installieren und `JAVA_HOME` darauf richten; `java -version` und `javac -version` müssen Java 17 anzeigen.
2. Repository auschecken und `./gradlew build` ausführen. Unter Windows `gradlew.bat build` verwenden. Gradle lädt die benötigten Werkzeuge und Bibliotheken; der erste Lauf benötigt deutlich länger als Folgeläufe.
3. Eigene Mod-JAR und Java-Quell-JAR liegen nach erfolgreichem Build unter `build/libs/`. Die Modversion `0.1.0-dev` bezeichnet ausschließlich das neue Grundgerüst und ist keine Versionsbehauptung über das 1.7.10-Original.
4. `./gradlew runClient` startet den Entwicklungsklienten in `run-client/`; `./gradlew runServer` den Dedicated Server mit `--nogui` in `run-server/`. Beide Verzeichnisse sind von Git ausgeschlossen. Beim eigenen Serverbetrieb ist die dort erzeugte Minecraft-EULA zu lesen und zu bestätigen.

Die Runtime-Metadaten begrenzen Minecraft auf `1.20.1`, Forge auf `[47.4.10,48)` und JavaFML auf `[47,48)`. Das sind Ladegrenzen; tatsächlich getestet wird zunächst die festgelegte Forge-Version. Ein paralleles Laden des Originals oder eines anderen Mods mit der Mod-ID `hbm` ist nicht vorgesehen.

Der gemeinsame Einstieg `com.hbm.HbmPort` registriert nur leere `DeferredRegister`-Wurzeln. Physisch clientabhängige Initialisierung liegt in `com.hbm.client.ClientSetup` mit `Dist.CLIENT`. Ein Dedicated Server darf diese Klasse nicht ausführen. Eigene Originalkonfiguration, BlockEntities, Menüs, Netzwerknachrichten und Inhalte folgen in späteren Arbeitspaketen. Der [Datenvertrag](DATA_CONTRACTS.md) beschreibt die geplanten Regeln, ohne sie als implementiert auszugeben.

## Statische Originalinventur

Das Werkzeug arbeitet ausschließlich lesend auf einem getrennten Checkout des Originalcommits. Es startet oder kompiliert das Original nicht. Ein anderer Commit oder veränderte relevante Original-Java-Dateien müssen vor der Erzeugung zurückgewiesen werden.

```bash
git init /tmp/hbm-original
git -C /tmp/hbm-original remote add origin https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT.git
git -C /tmp/hbm-original fetch --depth 1 origin aee05a40f10fb7bb9b042b65eccaa449ecc1672d
git -C /tmp/hbm-original checkout --detach FETCH_HEAD
python3 tools/inventory_original.py --source /tmp/hbm-original
python3 tools/inventory_original.py --source /tmp/hbm-original --check
HBM_ORIGINAL_SOURCE=/tmp/hbm-original python3 -m unittest discover -s tools -p 'test_inventory_original.py' -v
```

`--check` vergleicht den erwarteten JSON-Bestand ohne ihn zu verändern. Die Ausgabe dokumentiert Quellcommit, Dateiprüfsummen, Aufrufargumente und Quellzeilen sowie die Grenzen statischer Auflösung. Der Teilbestand deckt die Entity-/Mob- und TileEntity-Mappingtabellen und deren Registrierungsanbindung ab. Blocks, Items, Fluidarten, Rezepte, Assets und die tatsächliche Laufzeit-/Survivalerreichbarkeit bleiben weitere P0-Arbeit. Ein Exporteintrag ist keine Portimplementierung und keine Zusage eines konvertierten 1.7.10-Spielstands.

Der aktuelle Export enthält 121 Nicht-Mob- und 29 Mob-Deklarationen, fünf Spawnregeln und 378 Tile-Deklarationen mit insgesamt 379 Namen. Darunter sind ein bedingter OpenComputers-Eintrag und ein historischer Kabelalias. Zwei unterschiedliche Entity-Deklarationen verwenden `entity_cloud_rainbow`; der Export bewahrt diesen Konflikt, statt ihn als gewollten Alias umzudeuten. Lokale Entity-Nummern sind lediglich aus dem einmaligen Registrierungsablauf abgeleitete Sollwerte; wirksame globale IDs und Laufzeitkonfliktbehandlung werden nicht behauptet. Der Extraktor liest Git-Blobs aus dem fixierten Commit und prüft zuvor den Java-Arbeitsbaum, damit lokale Zeilenenden oder Änderungen den belegten Bestand nicht stillschweigend verändern.

## Automatisierte Prüfungen

Der GitHub-Workflow führt mit JDK 17 den Gradle-Build und die Inventurprüfungen gegen den fixierten Originalcommit aus. Aktionen sind auf vollständige Commit-SHAs fixiert; der Workflow erhält nur lesenden Repositoryzugriff und keine Projektgeheimnisse. Er verwendet keine öffentlichen Buildcache-/Artefaktuploads für Minecraft-Dateien, Mappingdaten, dekompilierte Quellen oder Entwicklungswelten. Der Wrapper-Bootstrap wird vor seiner Ausführung gegen die festgelegte Prüfsumme geprüft.

Dieser Buildjob ersetzt keine Client-/Server- oder Originalvergleichstests. Eigene spätere Veröffentlichungen müssen Mod-JAR, Lizenzhinweise und passenden vollständigen Quellstand nachvollziehbar zuordnen. Das Java-Quell-JAR ist eine Ergänzung, kein Ersatz für diesen Quellstand.

## Lizenzdateien und Grenzen

`LICENSE` und `LICENSE.LESSER` sind unverändert aus dem fixierten Original übernommen; neue Java-Dateien nennen `LGPL-3.0-only`. Das Forge-MDK liefert eigene LGPL-2.1-/Fremdvermerke unter `third_party_licenses/FORGE_MDK_LICENSE.txt` und `FORGE_MDK_CREDITS.txt`. Gradles Apache-2.0-Lizenz und NOTICE stehen separat unter `third_party_licenses/GRADLE_LICENSE.txt` und `GRADLE_NOTICE.txt`; die Header der Wrapper-Skripte bleiben erhalten. Diese Texte lizenzieren die jeweiligen Bestandteile und werden nicht pauschal auf alle Projektdateien übertragen.

Die Mappings und Minecraft-/Forge-Entwicklungsdateien sind benötigte lokale Buildabhängigkeiten und werden nicht in dieses Repository oder öffentliche CI-Artefakte kopiert. Modelle, Texturen und Sounds des Originals wurden noch nicht übernommen. Deren individuelle Herkunftsprüfung bleibt P0-Arbeit.

## Prüfstand dieses Arbeitspakets

Lokal geprüft am 19.10.2026 unter Linux x86_64 mit Eclipse Temurin **17.0.20.1+1**:

| Prüfung | Ergebnis |
| --- | --- |
| `./gradlew --no-daemon build sourcesJar` | Erfolgreich; Mod-JAR und Java-Quell-JAR erzeugt. Der Gradle-Testtask hat noch keine Java-Testquellen und ist kein Spielfunktionstest. |
| Paketinhalt | Genau drei eigene Java-Klassen mit Classfile-Version 61, ausgefüllte Mod-Metadaten, Packformat 15 und beide Lizenztexte. Keine Minecraft-/Forge-Klassen oder Originalquellen in den eigenen JARs. |
| Python-Inventurtests | Zwölf Tests bestanden: Parsergrenzen/Fehlerfälle und Integration gegen den fixierten externen Originalcheckout. |
| Inventur `--check` | Bytegenau erfolgreich; JSON-SHA256 `d392db7291b9bf0b29089f1829eb987fa3a6ebd6c01ceff90781f70a7699c2fb`. |
| Dedicated Server | `runServer` erreicht die Startbereitschaft, führt die gemeinsame Modinitialisierung und keine Clientinitialisierung aus; `stop` beendet ihn mit gespeicherter Testwelt und Exit-Code 0. Konsoleneingaben werden vom Gradle-Entwicklungsstart weitergeleitet. |
| Entwicklungsklient | `runClient` erreicht mit geladenem Mod und Clientinitialisierung das visuell geprüfte Hauptmenü. Test unter Xvfb/Mesa-llvmpipe mit OpenGL 4.5 und Audio ohne Ausgabegerät; reguläres Schließen beendet ihn mit Exit-Code 0. |
| Originalintegrität und Quellenprüfung | Separater Originalcheckout weiterhin auf dem Referenzcommit und unverändert; Wrapper-SHA, Lizenzkopien, Dokumentationsverweise und Diff geprüft. |

Die Laufzeitprüfungen betreffen das **Entwicklungsgrundgerüst**, keine Originalparität und keinen Produktionsbetrieb. Die Server-Testwelt war ausschließlich lokal mit Loopbackbindung und ohne Onlineauthentifizierung eingerichtet; ihre Einstellungen, EULA-Datei und Welt werden nicht versioniert. Im Clienttest waren externe Authentifizierungs-/Versionsabfragen in der Cloudumgebung nicht erreichbar; sie verhinderten den lokalen Menüstart nicht. Authentifiziertes Multiplayer-Spiel, reale Audioausgabe, Windows und andere Grafiktreiber wurden nicht geprüft.

P1 bleibt offen: Ein eigenes persistentes Registrierungs-/Speicherszenario, konkrete per-Typ-Datenverträge und benötigte Originalkonfiguration fehlen noch. P0 benötigt weiterhin die übrigen Registrierungsarten, Einzelvarianten, die lauffähige Java-8-Referenz sowie Originalmesswerte und Assetherkunft. Die vorhandenen Prüfungen ersetzen diese offenen Schritte nicht.
