# HBM für Minecraft Forge 1.20.1

Ziel ist eine möglichst vollständige, originalgetreue Portierung von [Hbm's Nuclear Tech Mod für Minecraft 1.7.10](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT) auf **Minecraft 1.20.1 mit Forge**. Maßgeblich sind Inhalt, Spielmechanik, Progression, Rezepte, Simulation und Darstellung des Originals. Neue Funktionen haben gegenüber Originaltreue keine Priorität.

**Stand: technisches Grundgerüst in Entwicklung.** Das Projekt enthält einen Forge-Mod-Einstieg mit leeren Block-/Item-Registern und getrennter Clientinitialisierung. Es enthält noch keine portierten Spielfunktionen und ist keine spielbare HBM-Portierung. Die Originalquellen werden separat und unverändert untersucht; die erste maschinenlesbare Inventur erfasst die Entity- und TileEntity-Mappingtabellen.

## Verbindliche Originalreferenz

| Merkmal | Geprüfter Stand |
| --- | --- |
| Repository / Branch | `HbmMods/Hbm-s-Nuclear-Tech-GIT` / `master` zum Analysezeitpunkt |
| Commit | [`aee05a40f10fb7bb9b042b65eccaa449ecc1672d`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/commit/aee05a40f10fb7bb9b042b65eccaa449ecc1672d) |
| Analyse | 19. Oktober 2026 (UTC) |
| Modversion | `1.0.27_X5846`; Laufzeitkennung `1.0.27 BETA (5846)` |
| Originalplattform | Minecraft `1.7.10`, Forge `10.13.4.1614`, Java `8` |
| Zielplattform | Minecraft `1.20.1`, Forge `47.x`, Java `17` |

Die Version stammt aus [`gradle.properties`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/gradle.properties) und [`RefStrings.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/lib/RefStrings.java). Der Commit ist die Referenz; die Branchspitze und spätere Releases können abweichen. Es wird kein bestimmtes veröffentlichtes Release-Artefakt als identisch behauptet.

## Dokumentation

- [Portierungsplan](docs/PORTING_PLAN.md): Quellinventur, Paketstruktur, technische Migration, Phasen, Risiken und Abnahme.
- [Feature-Matrix](docs/FEATURE_MATRIX.md): belegte Originalsysteme, Abhängigkeiten, Portstatus und Prüfkriterien. Alle Spielfunktionen beginnen mit **Nicht begonnen**.
- [Entwicklung und Validierung](docs/DEVELOPMENT.md): festgelegte Werkzeuge, Build, Entwicklungsstarts und belegter Prüfstand.
- [Datenverträge](docs/DATA_CONTRACTS.md): Spezifikationsentwurf für IDs, Speicherformate, Einheiten und Netzwerk; noch keine implementierten Verträge.
- [Registrierungsinventar](docs/inventory/registrations.json): aus dem fixierten Original erzeugter statischer Teilbestand mit Quellankern und Grenzen.

## Voraussetzungen

Benötigt werden **JDK 17**, Git und eine Internetverbindung für die Buildabhängigkeiten; eine Java-IDE ist optional. Der Build verwendet **Forge 47.4.10**, **ForgeGradle 6.0.54** und den mit SHA256 abgesicherten **Gradle-8.8-Wrapper**. Ein separat installiertes Gradle wird nicht benötigt. Python 3.10 oder neuer wird nur für das Inventurwerkzeug benötigt.

```bash
./gradlew build
./gradlew runClient
./gradlew runServer
```

Unter Windows heißen die entsprechenden Aufrufe `gradlew.bat build`, `gradlew.bat runClient` und `gradlew.bat runServer`. Der Serverstart verwendet `run-server/`; vor dem eigenen Betrieb ist dort die Minecraft-EULA zu lesen und anzunehmen. Entwicklungswelten und lokale Einstellungen sind von Git ausgeschlossen. Genauere Hinweise und der tatsächliche Teststand stehen in [DEVELOPMENT.md](docs/DEVELOPMENT.md).

Für spätere Vergleichstests wird eine getrennte Originalinstallation mit **JDK 8**, Minecraft 1.7.10 und Forge 10.13.4.1614 benötigt. Der Originalstand verwendet Gradle 4.4.1 und einen dynamischen ForgeGradle-1.2-Fork. Ein Originalbuild wurde in dieser Planungsphase nicht ausgeführt. Beide Entwicklungsumgebungen und Testwelten bleiben getrennt. Eine direkte Übernahme von 1.7.10-Spielständen wird nicht zugesichert; ein möglicher Konverter wäre ein separat zu planendes Vorhaben.

## Technische Referenzen

[HBM Rebirth](https://github.com/10MeV/HBM-NTM-Rebirth) und [HBM Modernized](https://github.com/Raptor324/HBM-Modernized) dienen ausschließlich zum Verständnis moderner Forge-Techniken. Ihre Erweiterungen, Balanceänderungen oder ausgelassenen Originalfunktionen definieren den Umfang dieses Ports nicht. Geprüfte Referenzcommits und Regeln zur Quellenherkunft stehen im [Portierungsplan](docs/PORTING_PLAN.md).

## Lizenz und Herkunft

Das Original erklärt in seiner [README](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/README.md#license) **GNU LGPL Version 3**. [`LICENSE`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/LICENSE) enthält den GPLv3-Basistext, [`LICENSE.LESSER`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/LICENSE.LESSER) die LGPLv3-Zusatzbedingungen; beide gehören zusammen. Urheber- und Lizenzvermerke des Originals und seiner Mitwirkenden sind bei einer Übernahme zu erhalten.

Die neu geschriebenen Java-Grundgerüstdateien und Python-Inventurwerkzeuge stehen unter **LGPL-3.0-only**; die zugehörigen Texte liegen als [LICENSE](LICENSE) und [LICENSE.LESSER](LICENSE.LESSER) unverändert aus dem fixierten Original bei. Original-Spiellogik und Spielassets wurden noch nicht übernommen. Buildwerkzeuge haben eigene Bedingungen: Die Forge-MDK- und Gradle-Lizenz-/Urhebertexte liegen getrennt unter [third_party_licenses](third_party_licenses/). Die Herkunft ist in [DEVELOPMENT.md](docs/DEVELOPMENT.md) dokumentiert.

Vor späterer Übernahme und Veröffentlichung sind Quellherkunft, Änderungen und Pflichten zur Bereitstellung des entsprechenden Quellcodes zu dokumentieren. Ein Java-`sources.jar` allein enthält nicht automatisch Buildskripte und alle benötigten Vermerke; veröffentlichte Versionen benötigen einen passenden vollständigen Quellstand. Mitgelieferte Drittanbieter-APIs und einzelne Assets benötigen eine eigene Herkunftsprüfung: Die CoFH-API enthält Team-CoFH-Copyrightvermerke, aber in den untersuchten Dateien keinen separaten ausdrücklichen Lizenztext. Auch Rebirth und Modernized haben eigene Lizenzbedingungen; eine technische Referenz ist keine pauschale Freigabe zur Code- oder Assetübernahme.

Dies ist ein eigenständiges Portierungsvorhaben; eine offizielle Zugehörigkeit zum Originalprojekt wird nicht behauptet. Originalautor und Mitwirkende sind über die oben verlinkten Originalquellen und deren Credits nachgewiesen.
