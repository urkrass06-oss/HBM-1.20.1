# HBM Modernized: Bestandsaufnahme für HBM Complete Port

Stand: **19. Oktober 2026 (UTC)**. Ziel bleibt das Verhalten von HBM 1.7.10 auf **Minecraft Forge 1.20.1**. Empfehlung: Modernizeds zusammenhängende Forge-Architektur als technische Basis verwenden und das vorhandene kleine Grundgerüst integrieren. Das spart voraussichtlich mehr Integrationsarbeit als einzelne eng gekoppelte Systeme herauszulösen. **Es gibt hier keinen Nachweis vollständiger Originalparität und keinen Code- oder Assetimport.** Die konkrete Umsetzung steht in [MODERNIZED_MIGRATION.md](MODERNIZED_MIGRATION.md).

Diese beiden Dokumente beschreiben die neue Strategie. Die Aussagen „Modernized ausschließlich als technische Referenz“ in der bisherigen README und im [PORTING_PLAN.md](PORTING_PLAN.md) sind damit als bisheriger Plan einzuordnen. Dessen Originalreferenz, Vollständigkeitsziel und Abnahmekriterien bleiben maßgeblich. Bestehende Dokumente, Lizenzangaben und Featurestatus werden durch diesen Dokumentations-PR nicht verändert; ihre Anpassung ist ein eigener Migrationsschritt.

## 1. Fixierte Quellen und tatsächlicher Zielstand

| Kürzel / Rolle | Repository und untersuchter Branch | Vollständiger Commit | Bedeutung |
| --- | --- | --- | --- |
| Z0 | `urkrass06-oss/HBM-1.20.1`, `main` | [`c8d2746172d9324eab8aa59ea39ac1daef9a4b19`][z0] | Nur `README.md`; kein Forge-Projekt auf `main`. |
| Z | Ziel, `docs/original-porting-plan` | [`d158d8305fd13322fd711772dbe533f7ee19aebf`][z] | Aktueller Entwicklungsstand mit Plan und integriertem Grundgerüst; Basis dieses PRs. |
| ZF | Ziel, `foundation/forge-1.20.1` | [`6e7bb13a3209aa31d734a9012f39e82614acc6b7`][zf] | Foundation-Stand, über [PR #2][pr2] in Z integriert. |
| M | `Raptor324/HBM-Modernized`, `main` | [`0365cef5956016913095eeeb9366f26c601ca9a0`][m] | Untersucht wird ausschließlich die Variante `1.20.1-forge`. |
| O | `HbmMods/Hbm-s-Nuclear-Tech-GIT`, `master` | [`aee05a40f10fb7bb9b042b65eccaa449ecc1672d`][o] | Verbindliche fachliche Originalreferenz, `1.0.27_X5846`. |

Zum Analysezeitpunkt ist [PR #1][pr1] von `docs/original-porting-plan` nach `main` noch offen. Deshalb wäre eine Analyse nur von `main` unvollständig. Der neue PR baut auf Z auf und enthält ausschließlich die beiden neuen Markdown-Dateien. Ein späterer Branchwechsel oder Upstream-Update erfordert einen neuen SHA-Eintrag und eine Differenzprüfung.

**Pfadkonvention:** `M:…` bezeichnet einen Pfad relativ zur [Modernized-Wurzel am fixierten Commit][m]; `O:…` entsprechend zur [Originalwurzel][o]. In Tabellen mit Java-Dateinamen ist `M:src/main/java/com/hbm_m/` die Wurzel, sofern kein anderer Präfix angegeben ist. Originalbelege und die 140 bestehenden Funktions-IDs stehen in [FEATURE_MATRIX.md](FEATURE_MATRIX.md), ergänzt durch [DATA_CONTRACTS.md](DATA_CONTRACTS.md). Rebirth wurde für diese Untersuchung nicht zusätzlich als Quellbasis ausgewertet.

### Methode und Aussagegrenzen

Ausgewertet wurden Git-Bäume, Buildskripte, Metadaten, Lizenztexte und Credits sowie Registrierungen, Einstiegspunkte und repräsentative Implementierungen. Bei Presse und ZIRNOX wurde zusätzlich die Block-zu-Tick-Anbindung gelesen. Geprüfte Gegenbeispiele umfassen leere Prozesse, generische Vanilla-Blöcke und auskommentierte Klassen. Kommentare wurden gegen den ausführbaren Code geprüft: Beispielsweise nennt MK5 Fallout noch als zukünftige Arbeit, obwohl `spawnFallout()` bereits eine registrierte `EntityFalloutRain` erzeugt. Der Kommentar allein wäre ein falscher Fehlbestandsbeleg.

Es erfolgten **kein vollständiges Audit aller Methoden, keine Laufzeitinventur, kein Originalvergleich im Spiel und keine individuelle Rechtefreigabe aller Assets**. Auch ein Upstream-README oder eine Datei namens „parity“ belegt keine bestandenen Tests. Die Inventur liefert keinen Fertigstellungsprozentsatz.

| Git-Dateibestand am jeweiligen Commit | Z | M | O |
| --- | ---: | ---: | ---: |
| `src/main/java/**/*.java` | 3 | 1.326 | 3.484 |
| Dateien unter `src/main/resources/` | 2 | 6.720 | 7.508 |
| PNG / OGG / OBJ unter `src/main/resources/` | 0 / 0 / 0 | 4.869 / 118 / 252 | 6.007 / 523 / 518 |
| Dateien unter `src/generated/resources/` | 0 | 2 (JSON-Sprachdateien `en_us`, `ru_ru`) | 0 |

Das sind **Dateizahlen**, keine registrierten Inhalte oder abgedeckten Originalfunktionen. Generierte Rezepte/Modelle fehlen im Git-Bestand teilweise absichtlich und entstehen erst durch Datengenerierung. Dekorative Blöcke dürfen legitimerweise generische `Block`-Instanzen sein; dieselbe Registrierung ersetzt bei einer Maschine jedoch keinen Prozess.

Strukturell besteht Z aus einem einzelnen Forge-Projekt mit `src/main/`, `docs/`, `tools/` und `third_party_licenses/`. M trennt gemeinsame Quellen unter `src/main/` von Variantenproperties unter `versions/`, eigenen Gradle-Konventionen unter `build-logic/`, erzeugten Ressourcen unter `src/generated/` und historischen ForgeGradle-Dateien unter `legacy/`. O ist ein einzelnes altes Forge-Projekt mit umfangreichen `com/hbm`-Systemen, öffentlichen `api/hbm`-Schnittstellen und mitgelieferter `cofh/api` neben den Ressourcen. Diese Unterschiede erklären, warum das Einfügen nur eines M-Javapakets in Z normalerweise nicht genügt.

## 2. Architektur, Plattform und Abhängigkeiten

| Merkmal | Z: bisheriges Grundgerüst | M: aktuelle Forge-Variante | O: Original |
| --- | --- | --- | --- |
| Minecraft / Forge | `1.20.1` / `47.4.10` | `1.20.1` / Buildziel `47.4.20`; Metadatenminimum `47.3.31` | `1.7.10` / `10.13.4.1614` |
| Java | Toolchain und `--release 17` | Java-Quell-/Zielkompatibilität **17** für 1.20.1; Gradle-Daemonkriterium **21**; kein gleichwertiger Beleg für API-/Bytecodekompatibilität sämtlicher erzeugter Klassen | Java-Quell-/Zielversion **8**, CI mit JDK 8 |
| Build | Gradle `8.8`, ForgeGradle `6.0.54`, Groovy | Gradle `9.3.1`, Stonecutter `0.8`, Kotlin DSL und eigener `build-logic`-Build; `net.neoforged.moddev.legacyforge` `2.0.120` für **Forge** | Gradle `4.4.1`, dynamischer ForgeGradle-Fork `com.anatawa12.forge:ForgeGradle:1.2-1.0.+` |
| Mappings | Mojang `official:1.20.1` | Zusätzlich Parchment `1.20.1:2023.09.03` | Alte Forge-/MCP-Umgebung; keine modernen Mojang-Namen |
| Mod-ID / Java | `hbm`, `com.hbm`, Einstieg `HbmPort` | `hbm_m`, `com.hbm_m`, `ForgeEntrypoint` → `MainRegistry.init()` | `hbm`, `com.hbm`, `main/MainRegistry` mit FML-Lebenszyklus und Proxies |
| Version | `0.1.0-dev` | Property `0.2.1-alpha`; Projektversion ergänzt Minecraft/Loader | `1.0.27_X5846`, Laufzeit `1.0.27 BETA (5846)` |
| Registrierungen | Leere Forge-`DeferredRegister` für Block und Item | Vorwiegend Architectury-`DeferredRegister`/`RegistrySupplier`; Forge-Registrierung für weitere Teile | `GameRegistry`, Mappingtabellen und statische Initialisierung |
| Weltzustand / Energie | Noch nicht implementiert | `SavedData`, BlockEntity-NBT, Forge-Capabilities; eigenes HE-Netz mit `long` | TileEntities, `WorldSavedData`, Extended Entity Properties; HE-MK2-/UniNodespace-Systeme |
| Fluids | Nur Spezifikationsentwurf | Minecraft-/Forge-Fluids und eigene Traits, Tanks, Druck-/MK2-Netze, Außenadapter | Eigene `FluidType`-Identitäten und MK2-Drucknetze; keine Gleichsetzung mit Forge-Fluids |
| Netzwerk | Noch keines; Datenvertrag schlägt `SimpleChannel` vor | Architectury `NetworkManager`, ResourceLocation-Paketkennungen, getrennte C2S-/S2C-Registrierung | Forge SimpleNetworkWrapper plus eigene NBT-Paketverarbeitung |
| Darstellung | Getrennte, noch leere Clientinitialisierung | Umfangreiche Clientrenderer, OBJ/DAE-Lader, VBO-/Instancingpfade, Mixins und Access Transformer | Proxies, OpenGL-/LWJGL-2-/Displaylistenpfade, eigene Modell-/Animationssysteme und AT |
| Konfiguration | Noch keine Spielfunktionskonfiguration | Eigener JSON-Speicher `HbmConfigStore`, Schema und eigener `ConfigScreen`; historischer Klassenname `ModClothConfig` | Viele Forge-/JSON-Konfigurationsklassen und maschinenspezifische Werte |

Belege: Z:[Build/Properties][z-build], [Metadaten][z-mods], [Java-Einstieg][z-entry]; M:[Settings][m-settings], [Forge-Build][m-build], [Versionsproperties][m-version], [Versionskatalog][m-catalog], [Buildkonvention][m-plugin], [Daemonkriterium][m-daemon], [Einstieg][m-entry], [Haupteinstieg][m-main], [Plattformadapter][m-platform], [Netzwerk][m-packets]; O:[Build][o-build], [Version/ID][o-ref].

### Wichtige Einzelheiten zur Modernized-Buildstruktur

- `settings.gradle.kts` aktiviert `1.20.1-forge` und `1.21.1-neoforge`. Weitere Fabric-/1.21.11-Verzeichnisse existieren, sind dort aber auskommentiert. Der Pluginname `legacyforge` macht das Forge-1.20.1-Artefakt nicht zu einem NeoForge-Mod.
- Stonecutter verarbeitet bedingte `//? if forge …`-Abschnitte. Gemeinsame Dateien können ansonsten gleichzeitig Quelltext verschiedener Loader enthalten. Einfaches Kopieren in das ForgeGradle-Grundgerüst überspringt diese Verarbeitung und die `PlatformHooks`-Abhängigkeiten.
- `legacy/forgegradle/` ist ein eigener historischer Buildbestand, nicht der aktive Build. Er darf nicht mit dem aktuellen Kotlin-Build verwechselt werden.
- `versions/1.20.1-forge/gradle.properties` enthält einen absoluten **Windows-JDK-21-Pfad**. Seine Wirkung ist kontextabhängig; er ist in jedem Fall vor einem plattformunabhängigen Basisbuild zu bereinigen. Zusätzlich verlangt `gradle/gradle-daemon-jvm.properties` JDK 21.
- Die vorhandenen CI-/Release-Workflows konfigurieren JDK 17 und ein installiertes Gradle 8.7, rufen aber den Wrapper 9.3.1 auf. Der Releaseworkflow führt `runData` vor dem Forge-Build aus; der allgemeine CI-Job nur `./gradlew build`. Diese Konfiguration ist kein Beleg eines aktuellen grünen Forge-Builds oder vollständiger generierter Ressourcen. Siehe [CI][m-ci] und [Releaseworkflow][m-release].

### Abhängigkeiten: unterschiedliche Rollen erhalten

| Rolle | Geprüfter M-Bestand | Konsequenz |
| --- | --- | --- |
| Kernlaufzeit / eingebettet | Architectury Forge `9.2.14` via `modImplementation` **und** `jarJar`; MixinConstraints `1.1.0` ebenfalls eingebettet | Metadaten, tatsächlichen JAR-Inhalt, transitive Abhängigkeiten und Lizenztexte prüfen. `mods.toml` verlangt Architectury, obwohl das Build-DSL es als optional beschreibt; die Ressourcenvorlage ist hier entscheidend. |
| Build / Codeerzeugung | Mixin-Processor `0.8.5`, Stonecutter/Postprocess, Kotlin/KSP und Fletching Table; weitere Plugins im Versionskatalog | Eigene Buildoberfläche mit zusätzlichen Artefakten; nicht alle Plugins sind Laufzeit-Mods. Versionen und Hashes beim Basisbuild sichern. |
| Optionale Integration | Create `6.0.8-289:slim`, Flywheel API `1.0.5` nur zur Kompilierung; Create-Metadaten `[6.0.8,6.1.0)` | Kernmod muss ohne beide startbar bleiben; Create-Anwesenheit separat testen. |
| Rezeptanzeige im Entwicklungsbuild | JEI über CurseMaven-Datei `7270446`, compile-only und runtime-only | Kein vollständiger Original-NEI-Ersatz nachgewiesen; Rezeptkategorien und Ausgabe-JAR unterscheiden. |
| Entwicklungs-Runtime | Embeddium, Oculus, ModernFix, Smooth Boot, Screenshot to Clipboard, Spark, Observable, Kotlin For Forge und Jade | Diese `modRuntimeOnly`-Einträge nicht pauschal zu verpflichtenden Nutzermods oder mitzuliefernden Bestandteilen erklären. Unverändertes Server-Startprofil kann damit andere Probleme haben als das Kernmod. |
| README-Altangabe | README fordert Cloth Config; aktiver Forge-Build deklariert es nicht, `ModClothConfig` beschreibt den Wechsel zu eigenem JSON/GUI | Keine Cloth-Pflicht allein aus der README ableiten. Minimalinstallation anhand Build, Bytecode, Metadaten und Laufzeit bestimmen. |

Z hat außer Minecraft/Forge keine zusätzlichen Gameplay-Abhängigkeiten. O deklariert CodeChickenCore/CodeChickenLib/NEI als `implementation`, InventoryTweaks, OpenComputers und AE2 als `compileOnly`; diese 1.7.10-Koordinaten sind keine nutzbaren 1.20.1-Abhängigkeiten. Mitgelieferte `cofh/api`-Quellen benötigen eine separate Herkunftsprüfung. Die Lizenzprüfung der eingebetteten M-Bibliotheken ist noch offen; deren Lizenzen werden hier nicht ohne Artefaktprüfung behauptet.

## 3. Lizenzen, Urheber und Assets

### Festgestellte Erklärungen

| Bestand | Beleg | Konsequenz für eine spätere Übernahme |
| --- | --- | --- |
| O | [README, Abschnitt License][o-readme] erklärt **GNU LGPL Version 3**; [LICENSE][o-license] enthält GPLv3, [LICENSE.LESSER][o-lesser] die ergänzenden LGPLv3-Bedingungen | Beide Texte zusammen lesen. GPL-Basistext allein bedeutet hier nicht, dass das Original pauschal GPL-only wäre. Kein pauschales „or later“ aus Musterformulierungen am Ende einer Lizenzdatei ableiten. |
| Z / ZF | README und eigene Java-/Python-Header nennen **LGPL-3.0-only**; eigene Forge-/Gradle-Fremdtexte in `third_party_licenses/` | Diese Herkunft und Einzelvermerke erhalten; das kombinierte Modernized-Derivat kann nicht unverändert nur als LGPL-Gesamtwerk angekündigt werden. |
| M | [LICENSE][m-license]: **GPLv3**; [gradle.properties][m-properties]: `mod.license=GNU General Public License v3.0` | Kopieren und Ändern ist unter den Lizenzbedingungen grundsätzlich vorgesehen. Auch die Übernahme einzelner GPL-Systeme beseitigt die Copyleft-Frage nicht. Für ein zusammenhängendes abgeleitetes Modwerk ist eine GPLv3-konforme Veröffentlichung zu planen. |

Die GPLv3-Kombination mit LGPLv3-Bestand ist grundsätzlich ein möglicher Weg; LGPLv3 enthält zusätzliche Erlaubnisse zum GPLv3-Basistext. Das ist **keine Erlaubnis, fremden Code pauschal umzuschreiben oder alle Einzelbestandteile als selbst verfasst auszugeben**. Bei einer Übernahme müssen Gesamtwerkkennzeichnung, GPL-/LGPL-Herkunft und zulässige Behandlung der jeweiligen Dateien zusammenpassen. Unverändert weiterverwendete LGPL-Dateien behalten ihre Vermerke. Eine reine LGPL-Kennzeichnung für eingefügten Modernized-GPL-Code wäre unzureichend. Eine alternative Lizenz benötigt eine entsprechende Rechtebasis; die ist hier nicht belegt.

Im geprüften M-Root-Lizenztext wurde keine besondere Minecraft-/Forge-Linkingausnahme gefunden. Die genaue Einordnung der Verbindung mit diesen Plattformen und anderen Fremdmods bleibt deshalb Teil der Prüfung des konkreten Verteilungsmodells. Dieser Befund behauptet weder eine bereits festgestellte Unzulässigkeit noch eine pauschale Freigabe der Gesamtdistribution.

**Vor Weitergabe von Quelltext/JAR zu erfüllen:**

1. Copyright-, Lizenz- und Gewährleistungshinweise erhalten; relevante Lizenztexte mitliefern. Die FSF-Copyrightzeile auf dem Lizenztext bezeichnet dessen Urheber, nicht den Autor sämtlicher Moddateien.
2. Eigenständiges Derivat deutlich benennen, Original und Modernized mit Autoren und Commitquellen nennen und Änderungen samt Datum kenntlich machen (GPLv3 §§4–5). Keine offizielle Zugehörigkeit oder Markenfreigabe aus der Codelizenz ableiten.
3. Für ein ausgeliefertes kombiniertes GPL-Werk die entsprechenden GPLv3-Bedingungen einhalten; bei Binary-Downloads einen eindeutig zugeordneten vollständigen „Corresponding Source“-Stand einschließlich benötigter Buildskripte, Generatoren und Vermerke zugänglich machen (GPLv3 §§1, 6). Ein `sources.jar` nur mit Java-Dateien reicht dafür nicht automatisch.
4. Fremdbibliotheken und Assets separat inventarisieren; ihre jeweils geltenden Bedingungen bleiben bestehen. Abhängigkeiten zwischen Modcode und Minecraft-/Forge-/Bibliotheks-APIs samt Verteilungsmodell prüfen; diese Dokumentation erklärt Minecraft oder Fremdmods nicht automatisch zu GPL-Material und kopiert sie nicht in das Projekt.

Dieser PR übernimmt nur Analyse-/Planungstext und ändert keine Lizenzdatei. Es wird keine bereits durchgeführte Lizenzumstellung behauptet.

### Konkrete Copyright- und Herkunftspunkte

- O:[`gradle.properties`][o-properties] enthält umfangreiche namentliche Credits für Code, Texturen, Modelle, Sounds und Übersetzungen. Diese Liste und ursprüngliche Dateivermerke nicht auf „HbmMods“ reduzieren.
- M:[README][m-readme] nennt The Bobcat und Raptor324; `gradle.properties` nennt RaptorDev, TRFFuchs, razchexlitiel, HyperiO und weitere Mitwirkende. [`DamageResistanceHandler`][m-resist] enthält `@author hbm (ported to 1.20.1)`. Die README-Aussage „rewritten from scratch“ ersetzt deshalb keine Herkunftsprüfung einzelner Dateien.
- M:[`cargo_door.obj`][m-cargo] enthält `Made By TheVitya2127`; die SU-47-Modelle enthalten einen ImageToStl-Konverterhinweis. Ein Konverter-/Blenderheader ist kein ausreichender Nachweis über die Rechte am zugrunde liegenden Modell.
- O:[`cofh/api/package-info.java`][o-cofh] nennt Team CoFH, aber in den untersuchten Dateien steht keine eigene ausdrückliche Lizenzfreigabe. [`IToolAreaAbility.java`][o-ability] kennzeichnet einen TConstruct-Abschnitt als CC0; [`ModelCrab.java`][o-crab] trägt einen Minecraft-SMP-Copyright-/Generatorheader. Diese unterschiedlichen Hinweise müssen am jeweiligen Übernahmebestand erhalten und geklärt werden.

**Assets:** In M wurde außer dem Root-`LICENSE` kein separates Lizenz-/Creditsmanifest gefunden; unter `src/main/resources/` kein zusätzliches `.txt`-/`.md`-Rechtemanifest. Das ist eine offene Nachweislücke, kein Beweis, dass sämtliche Assets unzulässig wären. Modelle, Texturen, Audio, Animationen, Übersetzungen und Strukturen benötigen pro Datei oder belegbar homogener Gruppe: Quelle, SHA/Blobhash, Urheber, konkrete Lizenz, Vermerke, Änderungen und Prüfergebnis. Unklare Bestände bis zur Klärung nicht in einen veröffentlichten Port übernehmen; nachvollziehbar ersetzen oder nachweisbare Nutzungserlaubnis beschaffen. Ein fehlender Sound in M ist zudem kein automatischer Lizenzbeleg für eine Kopie aus O.

## 4. Originalfunktionen und tatsächlicher Modernized-Bestand

Die folgenden Befunde ergänzen die bestehenden Original-IDs, **ohne deren Portstatus zu ändern**:

- **S**: Systemquellcode und Registrierungs-/Initialisierungspfad belegt; Originalparität und Funktion im Spiel offen.
- **T**: Konkreter Teilbestand, vereinfachter Ablauf oder Platzhalter belegt; die ganze Originalfamilie ist damit nicht vorhanden.
- **N**: In den untersuchten zentralen Registern, Einstiegspunkten und passenden Klassenfamilien kein ausführbares Gegenstück nachgewiesen. Namen/Assets können trotzdem vorhanden sein.
- **U**: Nicht ausreichend im Detail geprüft; keine Aussage über Vollständigkeit.

S bedeutet ausdrücklich weder „fertig“ noch „getestet“. Bei gemischten Gruppen gilt die Einschränkung in der Befundspalte. Z registriert noch keine dieser Spielfunktionen.

### Grundlagen, Netze und Industrie

| Original-IDs / Familie | M-Befund | Quellbeleg und verbleibende Arbeit |
| --- | --- | --- |
| BASE-001–004, BASE-008, BASE-011: Start, Kataloge, Inventare, Daten | S/T | [Einstieg][m-entry], [MainRegistry][m-main], [ModBlocks][m-blocks], [ModItems][m-items], [ModBlockEntities][m-be], `blockentity/BaseMachineBlockEntity.java`. Große Kataloge und moderne Speicherpfade; viele registrierte Maschinen dennoch ohne Fachprozess. Vollständige Varianten-/NBT-Zuordnung offen. |
| BASE-005: Multiblocks | S/T | `multiblock/MultiblockStructureHelper.java`, `MultiblockPlacement.java`, Rollen und Universalteile. [`MultiblockStructureStubs.singleController()`][m-multistub] ist ausdrücklich ein Ersatz für echte Strukturen; pro Maschine Geometrie, Anschlüsse und Abbau prüfen. |
| BASE-006: Konfiguration | S/T | [ModClothConfig][m-config], `config/HbmConfigStore.java`, `config/schema/`, `client/gui/ConfigScreen.java`. Eigene moderne Konfiguration vorhanden; sämtliche Originaloptionen/Defaults und deren Synchronisation nicht abgeglichen. |
| BASE-007: Nachrichten | S | [ModPacketHandler][m-packets] bindet C2S und getrennte Clientempfänger ein. Keine 1.7.10-Protokollkompatibilität; Autoritäts- und Größenprüfung siehe Risiken. |
| BASE-009–010, BASE-012: Rezepte, Tags und Lader | S/T | [ModRecipes][m-recipes], [DataGenerators][m-datagen], `datagen/recipes/`, `inventory/recipes/` und `data/forge/tags/`. Mischung aus JSON, Java-Listen und Generierung; keine vollständige Originalrezept- oder Survivalprüfung. |
| BASE-013–014: Loot, Erfolge, Statistik | T/U | Loot-/Advancementdateien und Struktur-Lootprozessor vorhanden; Original-Itempools, Sondertrigger und Stats nicht vollständig geprüft. Zwei vorhandene Advancementdateien belegen keine Abdeckung aller Originalerfolge. |
| NET-001–003: HE-Netz, Kabel, Batterien, Konverter | S/T | [EnergyNetworkManager][m-energy], `api/energy/EnergyNetwork.java`, `WireBlockEntity`, `MachineBatteryBlockEntity`. Eigenes `long`-HE-System vorhanden; Konverter-/Verteilungsverhalten weicht ab bzw. ist offen, siehe §5. |
| NET-004–006: Fluidtypen, Leitungen, Tanks | S/T | [FluidNet][m-fluidnet], [FluidTank][m-tank], `inventory/fluid/ModFluids.java`, `FluidDuctBlockEntity`, `FluidValveBlockEntity`, `FluidPumpBlockEntity`, Außenadapter. Druck- und Traitlogik vorhanden; vollständige Stoff-/Druckabbildung offen. [Upstream-Prüfmatrix][m-fluidtests] hat nur offene Checkboxen. |
| NET-007–012: Förderbänder, Krane, Pneumatik, Drohnen, Funk, Telex | T/N | `conveyor*`, `drone*`, `radio_telex` etc. werden in [ModBlocks][m-blocks] teilweise als generische `Block` registriert. Kein Nachweis der zugehörigen vollständigen Logistik-/Steuerprozesse. Nicht anhand gleicher Namen abhaken. |
| NET-013: Lager und Zugriffsschutz | S/T | `blockentity/crates/` und [BlockEntity-Register][m-be]. Mehrere Kistenfamilien vorhanden; gesamtes Originalsortiment, Kapazitäten, Rechte und Automatisierung offen. |
| IND-001–003, IND-007–008, IND-017: Presse, Shredder, Öfen, Montage, Löten, Amboss | S/T | `MachinePressBlockEntity`, `MachineShredderBlockEntity`, `BlastFurnaceBlockEntity`, `MachineAssemblerBlockEntity`, `MachineAdvancedAssemblerBlockEntity`, `MachineSolderingStationBlockEntity`, `MachineArcWelderBlockEntity`, `AnvilBlockEntity`; [Register][m-be]/[Rezepte][m-recipes]. Presse hat gelesene Tickanbindung. E-Presse und übrige Originalvarianten nicht dadurch abgedeckt. |
| IND-004–006: Lichtbogen, Drehrohrofen, Gießerei, Stranggießen | S/T | Lichtbogenofen, Tiegel, Kanäle und Becken besitzen Klassen/Registrierungen; `rotary_furnace` ist generischer Block. Stranggießer und alle Gießverfahren separat prüfen. |
| IND-009–011: Autofertigung, Holz, Bergbau | T/U | `MachineMiningDrillBlockEntity` ist vorhanden; `sawmill` und weitere Namen sind generische Blöcke. Kein Vollnachweis von Autosaw, Mining-Laser, Pump- und Fabrikvarianten. |
| IND-012–016: Wärme, Dampf, Generatoren, Solar | S/T | Holzverbrenner, Kessel, Solarboiler, Spiegel, Turbinen und Kondensation besitzen Teilimplementierungen; z. B. `MachineIndustrialTurbineBlockEntity.processTurbine()`. Andere Generatornamen sind Platzhalter; kein geschlossener Originalenergiepfad verifiziert. |
| IND-018: Supercomputer | N | Kein entsprechender ausführbarer Prozess in den untersuchten Maschinenregistern/-klassen nachgewiesen. |

### Chemie und Kerntechnik

| Original-IDs / Familie | M-Befund | Quellbeleg und verbleibende Arbeit |
| --- | --- | --- |
| CHEM-001: Chemieanlage/-fabrik | S/T | `MachineChemicalPlantBlockEntity` nutzt Prozessmodule/Rezepte; [`MachineChemicalFactoryBlockEntity`][m-factory] initialisiert nur Netz/Speicherzustand und hat kein Menü/Prozess. Beide dürfen nicht gleich bewertet werden. |
| CHEM-002: Mischer/Kristallisation | S | `MachineMixerBlockEntity`, `MachineCrystallizerBlockEntity` und zugehörige Rezeptklassen vorhanden; Mengen, Mehrfachausgaben und Laufzeit offen. |
| CHEM-003: Elektrolyse/Radiolyse/Deuterium | T | `electrolyser`, `radiolysis` generische Blöcke; `MachineDeuteriumTowerBlockEntity` nur Grundgerüst. Kein verifizierter Prozesspfad. |
| CHEM-004: Ölgewinnung/Fracking | S/T | `OilDrillBaseBlockEntity`, `MachineDerrickBlockEntity.onSuck()`, `MachineFrackingTowerBlockEntity`; Pumpjack hat lediglich Fortschrittsgerüst. Lagerstätten, Ertrag und Erschöpfung einzeln vergleichen. |
| CHEM-005: Raffinerie/Fraktionierung/Vakuum | S/T | `MachineRefineryBlockEntity.refine()` vorhanden; `MachineFractionTowerBlockEntity` läuft nur über Fortschrittszustand, Vakuumdestillation ist Gerüst. |
| CHEM-006–008: Cracking, Reforming, Pyrolyse, Abgas | T/U | Cracking/Fackel haben Fortschrittsgerüste; Hydrotreater, katalytischer Reformer und Liquefactor nur Netz-/Speichergerüst. Keine vollständige Stoffbilanz oder Umweltwirkung nachgewiesen. |
| CHEM-009: Zentrifugen/Anreicherung | S/T | `MachineCentrifugeBlockEntity`, `MachineGasCentrifugeBlockEntity`, `recipe/CentrifugeRecipes.java`; sämtliche UF6-/PuF6- und Upgradefälle offen. |
| CHEM-010: PUREX/Abfallzerfall | N/U | Kein vollständiger ausführbarer Originalkreislauf nachgewiesen; vorhandene Material-/Fluidnamen genügen nicht. |
| CHEM-011: SILEX/Bestrahlung/Ausgasung | T | `MachineSilexBlockEntity` und `MachineFelBlockEntity` haben Fortschrittsgerüste, keinen belegten SILEX-Fachprozess. RBMK-Outgasser ist gesonderter Teilbestand. |
| CHEM-012: Beschleuniger/Zyklotron | S/T | `MachineCyclotronBlockEntity.canProcess()` und `recipe/CyclotronRecipes.java` vorhanden; kein damit belegter Teilchenbeschleuniger oder vollständiger Transmutationskatalog. |
| NUC-001: Brennstoffe/Neutronen | S/T | RBMK-Brennstoffitems, `handler/rbmk/`, ZIRNOX-Fuelpfade; gemeinsame Regeln aller Originalreaktoren nicht verifiziert. |
| NUC-002: Forschungs-/Brutreaktor | T | `reactor_small` generischer Block; [`MachineBreederBlockEntity.canProcess()`][m-breeder] endet immer mit `false`, `processItem()` ist leer. Sichtbares Menü und Tanks bedeuten hier keinen Brutprozess. |
| NUC-003–004: Graphitpile/Pile-MK2 | N | Kein ausführbares Gegenstück in den untersuchten Kerntechnikregistern/-klassen nachgewiesen. |
| NUC-005: ZIRNOX | S/T | [`MachineZirnoxBlockEntity`][m-zirnox], [Block/Ticker][m-zirnoxblock], Rod-/Kühlmittel-/Hitze-/Drucklogik und zerstörter Zustand vorhanden. Messwerte, Rezepte und Unfallfolgen nicht gegen O geprüft. |
| NUC-006: PWR | T | `pwr*`-Komponenten in [ModBlocks][m-blocks] als generische Blöcke; keine variable PWR-Kernsimulation nachgewiesen. |
| NUC-007: Watz | T | [`MachineWatzPowerplantBlockEntity`][m-watz] registriert, tickt aber nur Netzinitialisierung/`setChanged()`, ohne Reaktorprozess; `createMenu()` liefert `null`. |
| NUC-008–011: RBMK | S/T | [RBMK-BlockEntities][m-rbmk], Brennstäbe, Neutronenwelt, Konsole, Regelung/Kühlung/Outgasser und Loader registriert. `RBMKColumnBlockEntity.spawnDebris()` ist leer; Rod enthält Corium-TODO; Autoloader ohne eigenes Menü. Simulation und Unfallketten nicht vollständig. |
| NUC-012–013: Torusfusion/ICF | T/N | `fusion_component*` u. a. generische Blöcke; keine vollständige Torus-/ICF-Simulation nachgewiesen. |
| NUC-014: DFC/Core | T | `MachineCoreEmitterBlockEntity`, Injector und Receiver sind Netz-/Speichergerüste ohne Strahl-/Core-Fachprozess. |
| NUC-015–016: RTG/Strahlungsgenerator/Plasmaschmiede | T/N | Material-/Blocknamen wie `radgen`, RTG-Pellets vorhanden; kein damit belegter Wärme-/Umwandlungsprozess. |
| NUC-017: Reaktorunfälle | T | ZIRNOX-Debris und zerstörter Block vorhanden, RBMK-Schadenspfad unvollständig. Jede Reaktorfamilie benötigt eigene Abnahme. |

### Umwelt, Waffen, Welt und Oberflächen

| Original-IDs / Familie | M-Befund | Quellbeleg und verbleibende Arbeit |
| --- | --- | --- |
| ENV-001: Chunkstrahlung | S/T | [`ChunkRadiationManager.getProxy()`][m-radmanager] wählt Simple. [`ChunkRadiationHandlerPRISM.java`][m-prism] enthält nur auskommentierten Platzhaltercode. PRISM ist keine verfügbare Alternative; O bietet es konfigurationsabhängig an. |
| ENV-002, ENV-004, ENV-006: Dosis/Gefahren/Messung | S/T | `radiation/PlayerHandler`, `hazard/`, `event/HazardEventHandler`, Hazmat-/Geiger-/Decon-Klassen; vollständige Originalgefahren, Filter, Messwerte und Lebenszyklen offen. |
| ENV-003, ENV-005: Verschmutzung/Gase | T/U | Fluid-Traits und Verschmutzungskoeffizienten vorhanden; daraus folgt kein vollständiger Ersatz von O:`src/main/java/com/hbm/handler/pollution/PollutionHandler.java` und sämtlichen Welt-/Gesundheitsfolgen. |
| ENV-007: Fallout/Biome | S/T | [`EntityFalloutRain`][m-fallout], Kraterbiome und MK5-Aufruf vorhanden. Langzeiteffekte, Laufzeit und Intensitäten nicht verifiziert. |
| BOMB-001–005: Explosionen/Nuklear-/Spezialbomben | S/T | [`EntityNukeExplosionMK5`][m-mk5], MK3, `explosion/`, Fat-Man-/Prototype-BlockEntities und Bombenklassen vorhanden. Umfang aller Zünder/Nutzlasten und Originalalgorithmen offen; laufende Explosionen sind kein belegter Neustart-Roundtrip. |
| BOMB-006–007: Konventionell/Granaten | S/T | Landmine und Granaten-/Luftangriff-Entities registriert; modulare Originalfüllungen/-zünder und gesamter Sprengstoffkatalog nicht verifiziert. |
| BOMB-008–009: Schusswaffen/Munition | T/N | Turret-Projektile vorhanden; diverse `gun_*` in [ModItems][m-items] sind einfache `Item`. Kein gleichwertiges Sedna-Waffen-/Animations-/Nachladesystem nachgewiesen. |
| BOMB-010–013: Raketen/Start/Radar/Geschütze | S/T | [Entityregister][m-entities], Launchpads, MissileAssembly, Radar, mehrere Turrets. Flug-/Chunkloading-, Ziel-, Abwehr- und Nutzlastfälle einzeln prüfen. |
| BOMB-014–015: Satelliten/Soyuz/Lambda | S/T | [`Satellite.register()`][m-satellite] registriert ausschließlich `SatelliteHorizons`/Gerald; Soyuz und Kapsel vorhanden. Andere Satellitentypen und Lambda sind nicht dadurch implementiert. |
| BOMB-016: Kraftfeld/Tesla/Teleportation | N/U | Kein vollständiger ausführbarer Originalsystempfad in den untersuchten Registern nachgewiesen. |
| BOMB-017: TOM/Schwarze Löcher | S/T | TOM-, Black-Hole-, Vortex-/Quasar-Entities und Registrierung vorhanden; Wirkungsgrenzen und langfristige Weltfolgen offen. |
| WORLD-001–002: Erze/Schichten/Öl/Weltgen | S/T | [`ModWorldGen`][m-worldgen], Bedrock-/Ölfeatures und Datapackeinträge vorhanden. Höhenbereich, Häufigkeit, Biombedingungen und Gesamtkatalog gegen O offen. |
| WORLD-003–005: Spezialvorkommen/Strukturen | T/U | NBT-Strukturen, Structure-/Structure-Set-JSON und Prozessoren vorhanden; z. B. `bunker.json`. Kein Nachweis aller Originalbunker, Silos, Meteoriten oder NBT-/Jigsaw-Werkzeuge. |
| WORLD-006–008: Dungeons/Krater/Glyphidwelten | T/N | Krater-/Falloutteile vorhanden; keine vollständigen prozeduralen Originaldungeons oder Glyphid-Nester nachgewiesen. |
| MOB-001–005: Kreaturen/KI/Bosse | S/T/N | [ModEntities][m-entities] registriert Nolo und fünf Creepervarianten. Glyphid-, FBI-/Boss-, Vogel- und übriger Originalkatalog damit nicht vorhanden. Spawn-/KI-Verhalten der vorhandenen Mobs ungeprüft. |
| MOB-006–007: Minecarts/Züge | T/N | `rail_*` teils generische Blöcke; keine vollständigen Originalfahrzeuge/-züge nachgewiesen. |
| MOB-008: Effekt-/Logikentities | S/T | Mehrere Familien in [ModEntities][m-entities]; keine vollständige 1:1-Abbildung der Original-Mappingtabelle. |
| PLAYER-001–004: Schutz/Rüstung/Jetpacks/Werkzeuge | S/T | `powerarmor/`, `armormod/`, Hazmat und Werkzeugklassen vorhanden; Jetpack-Komponenten teils einfache Items. Originalfilter, Fähigkeiten, Kosten und vollständige Rüstungssätze offen. |
| PLAYER-005–006: Scanner/Verbrauchsgüter | S/T/U | Öl-/Tiefenerzscanner, Geiger sowie Item-/Effektbestand vorhanden; gesamter Originalkatalog und Wirkungen offen. |
| PLAYER-007–008: Türen/Deko/Licht/Audioobjekte | S/T/U | Umfangreiches Tür-/Modellsystem; Sirenen-/Tape-/Recorder- und übrige Originalinteraktionen nicht vollständig geprüft. |
| PLAYER-009–010: Anleitung/Bobmazon/Spezialinhalte | N/U | Kein vollständiger WI-AJ-/Guide- oder Bobmazon-Ersatz nachgewiesen; vorhandene UI-/Itemnamen nicht als Abdeckung werten. |
| CLIENT-001–003, CLIENT-007: Menüs/Modelle/Animation/Assets | S/T | `inventory/menu/`, `inventory/gui/`, `client/loader/`, `client/model/`, `client/render/`, [Renderingbeschreibung][m-renderdoc]. Einige Maschinen liefern kein Menü; Modellbestand und originale Animationen/Sprachschlüssel nicht vollständig abgeglichen. |
| CLIENT-004–006: Partikel/Audio/HUD/Eingabe | S/T | Partikelregister, Sounds, Overlay-/Keybind-/Powerarmorpfade vorhanden. Nur 118 OGG gegenüber 523 in O; keine Vollständigkeitsquote daraus ableiten. |
| CLIENT-008–009: Befehle/Diagnosen/Online-Helfer | T/U | Strahlungsbefehle, Diagnose-/Konfigurationsoberflächen und HTTP-Helfer vorhanden; Originalbefehle, Lade-/Onlinefunktionen und Offlineverhalten offen. |
| COMPAT-001–002: APIs/IMC/NEI | S/T/U | Eigene APIs und `compat/jei/` vorhanden. Binäre oder fachliche Kompatibilität mit alten HBM-APIs/IMC/NEI nicht zugesichert. |
| COMPAT-003–004, COMPAT-006: AE2/OC/Energy Control/Microblocks/Inventar | N/U | Keine gleichwertigen aktiven Integrationen in den untersuchten Einstiegspunkten und Buildabhängigkeiten nachgewiesen. Verfügbarkeit der 1.20.1-Partner bleibt separat zu klären. |
| COMPAT-005, COMPAT-007: Energieadapter/weitere Integrationen | S/T/U | FE-Adapter und Create-Kompatibilität vorhanden. Create ist ein technischer Zusatz; kein Ersatz für fehlende Originalsysteme oder maßgebliche Originalbalance. |

Die ID-Gruppen decken die **140 Zeilen** der bisherigen Feature-Matrix thematisch ab. Sie sind keine Einzelinventur sämtlicher Items, Rezepte oder Varianten. Der nächste Schritt muss diese Gruppen auf tatsächlich erreichbare Einzelinhalte herunterbrechen, einschließlich Platzhalter, Konfigurationszweige und nur per Befehl erreichbarer Inhalte.

## 5. Konkrete technische Risiken

| Priorität / Risiko | Quellbeleg und praktische Auswirkung | Erforderlicher Nachweis |
| --- | --- | --- |
| Hoch: nicht reproduzierter Basisbuild | JDK-21-Daemonkriterium, Windowspfad, widersprüchliche CI-/Wrapperstände und fehlende eingecheckte Datagen-Ausgaben | Separater Basisbuild nach M0/M1 im Migrationsplan. Java-17-Laufzeit auch für eingebettete/Kotlin-Klassen prüfen. |
| Hoch: doppelte Energienetzticks | [MainRegistry][m-main] ruft auf `SERVER_POST` den Overworldmanager auf; [`EnergyNetworkTickHandler`][m-energytick] tickt auf Forge-Level-END denselben Manager. Statisch sind zwei Aufrufpfade belegt. | Instrumentierter Zähler je Welt/Tick; tatsächliche Mehrfachausführung und Einfluss auf HE/Durchsatz messen. Genau eine fachliche Tickzuständigkeit herstellen. |
| Hoch: HE-/FE-Bedeutung | [`HbmForgeWrapper`][m-fewrapper] füllt/entnimmt denselben Puffer ohne Originalraten; O hat **5 HE → 1 RF** und **2 RF → 5 HE** als getrennte Defaults. `LongEnergyWrapper` gibt LOW-Bits als `int` aus; oberhalb `Integer.MAX_VALUE` können Anzeigen negative Werte ergeben. | Originalkonverter als fachliche Spezifikation, explizite FE-Abbildung; Grenzwert-, Simulations-, Restmengen- und Bilanztests. Keine pauschale HE=FE-Gleichsetzung. |
| Hoch: Paketgrenzen und Autorität | [`RBMKConsoleControlPacket.decode()`][m-rbmkpacket] allokiert `new int[len]` aus einem gelesenen `int` ohne dortige Längengrenze. `handle()` leitet nach Blocktypprüfung weiter, ohne dort Menü-/Distanzprüfung; `handleControl` erhält keinen Spielerbezug. | Begrenzung vor Allokation, gültige Aktionen/Indices/Zahlen, berechtigter Menü-/Welt-/Reichweitenbezug; negative und übergroße Eingaben ablehnen. Kein behaupteter Laufzeitexploit; konkrete Review-/Testpflicht. |
| Hoch: IDs/NBT/Netzwerknamen | M nutzt `hbm_m`, Z/O `hbm`; harte Strings auch in Eventannotationen, Assets, JSON, NBT-/SavedData- und Paketnamen | Vollständige Registry-/Ressourcen-/Speichermappingtabelle, atomarer Namensraumwechsel und Save-Roundtrip. Ein Suchen/Ersetzen allein reicht nicht. |
| Hoch: scheinbar vorhandene Fachprozesse | Watz/Core/Fabrik sind BE-Gerüste; Breeder verarbeitet nichts; PWR/Fusion/Förderbänder enthalten generische Blöcke | Jede „übernommene“ Maschine über Prozess/Rezepte/Erreichbarkeit testen; kein automatisches Hochsetzen der Matrix. |
| Hoch: Reaktoren/Explosionen | RBMK-Schadensstubs, MK5-NBT speichert hier nur Alter; Original bietet selbst keinen belegten vollständigen MK5-Neustart-Roundtrip | Originalverhalten einschließlich Grenzen messen; Crash/Restart/Chunkentladung spezifizieren. Neue Wiederaufnahme nicht stillschweigend als Originaltreue ausgeben. |
| Mittel: Fluidabbildung und Lebensdauer | Eigene Original-FluidType-IDs werden in M auf moderne Fluids/Traits abgebildet; Adapter für drucklose Forge-Fluids. Änderung von Stoff/Druck kann Tankinhalt beeinflussen | Druckstufen 0–5, inkompatible Medien, Rundung, Netzaufbau/-abbau, Entladung und Capability-Invalidierung prüfen. |
| Mittel: Render-/Mixin-/Serverkopplung | Großes Clientpaket, erforderliche Mixins und optionale Create-/Rendererpfade | Dedicated Server ohne Clientmods und Client auf JDK17; fehlende Modelle, Reload, Grafiktreiber und optionale Mods getrennt prüfen. |
| Mittel: veränderte Spielgestaltung | M beschreibt sich als „reimagining“; eigene Perks, Netzwerkprioritäten, Konfiguration und zusätzliche Integrationen | Originalwerte und Progression sind Maßstab. Abweichungen dokumentieren; technische Optimierung darf keine unbemerkte Balanceänderung sein. |

Die Risiken sind bewusst von bestätigten Defekten und offenen Laufzeitfragen unterschieden. Ein vorhandener `return null` allein wurde nicht als Fehler gewertet: Eine Turbine ohne GUI kann das beabsichtigen; ein Watz ohne Prozess bleibt unabhängig davon unvollständig.

## 6. Durchgeführte Prüfungen und Reproduktion

| Prüfung am 19.10.2026 | Ergebnis / Grenze |
| --- | --- |
| Git-Bäume/SHAs, Zielbranches und PR-Beziehungen | Z0/Z/ZF/M/O wie oben fixiert; separate Analysecheckouts außerhalb des Zielbaums. |
| Statische Inventurtests des Zielprojekts | **12 Tests bestanden**, einschließlich Integration gegen O. Keine neuen Spielmechaniktests und keine Spielfunktionen damit abgenommen. |
| `inventory_original.py --check` | Erfolgreich; bestehendes JSON unverändert, SHA256 `d392db7291b9bf0b29089f1829eb987fa3a6ebd6c01ceff90781f70a7699c2fb`. |
| M: `./gradlew --no-daemon :1.20.1-forge:build` | Erster Versuch scheitert am Distributiondownload, da der Java-Wrapper den Umgebungsproxy nicht automatisch verwendet. Nach expliziter HTTP-/HTTPS-Proxykonfiguration lädt Gradle 9.3.1 erfolgreich. |
| M: Build mit Proxy, Linux x86_64 / OpenJDK `21.0.12.1` | **Vor der Projektkompilierung fehlgeschlagen:** `Unable to download toolchain … languageVersion=21 … No defined toolchain download url for LINUX on x86_64 architecture.` Auch mit explizitem `JAVA_HOME` und Installationspfad kein erfolgreicher Lauf. Keine Quellen geändert. Das ist ein beobachteter Setupblocker, kein Beweis, dass M generell nicht kompiliert. |
| Java-/Forge-Build des Zielgrundgerüsts | In diesem reinen Dokumentationspaket nicht erneut ausgeführt; der frühere Prüfstand in `DEVELOPMENT.md` ist historische Evidenz für Z, nicht für M. |
| Modernized-/Original-Spieltests, Multiplayer, Leistung, Einzelassetrechte | **Nicht ausgeführt / nicht abgeschlossen.** Erforderliche Abnahmefälle im Migrationsplan. |

Reproduktion in getrennten Checkouts; Zweignamen nicht als langfristige Pins verwenden:

```bash
# In einem separaten Analyseverzeichnis; keine Fremdquellen in das Ziel kopieren.
git clone --filter=blob:none --no-checkout https://github.com/Raptor324/HBM-Modernized.git modernized
git -C modernized checkout --detach 0365cef5956016913095eeeb9366f26c601ca9a0
git clone --filter=blob:none --no-checkout https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT.git original
git -C original checkout --detach aee05a40f10fb7bb9b042b65eccaa449ecc1672d
git -C modernized rev-parse HEAD
git -C original rev-parse HEAD
git -C modernized ls-tree -r --name-only HEAD
git -C original ls-tree -r --name-only HEAD

# Aus dem Zielprojekt, mit taskbezogenem Pfad zum separaten Originalcheckout:
HBM_ORIGINAL_SOURCE=/pfad/zum/original python3 -m unittest discover -s tools -p 'test_inventory_original.py' -v
python3 tools/inventory_original.py --source /pfad/zum/original --check

# In modernized; kann die oben beschriebenen Setupblocker reproduzieren:
./gradlew --no-daemon :1.20.1-forge:build
```

Die Auswertung verwendete für Java und Ressourcen ausschließlich den Git-Dateibaum am jeweiligen SHA, nicht lokal erzeugte Builddateien. Für eine erneute Zählung die Pfadpräfixe/Suffixe aus §1 auf `git ls-tree -r --name-only <SHA>` anwenden. Toolchain-, Download- und Laufzeittests benötigen eine korrekt konfigurierte Umgebung. Die neue Strategie ist damit fachlich begründet, aber die technische Basis noch nicht als releasefähig abgenommen.

## Quellverweise

[z0]: https://github.com/urkrass06-oss/HBM-1.20.1/tree/c8d2746172d9324eab8aa59ea39ac1daef9a4b19
[z]: https://github.com/urkrass06-oss/HBM-1.20.1/tree/d158d8305fd13322fd711772dbe533f7ee19aebf
[zf]: https://github.com/urkrass06-oss/HBM-1.20.1/tree/6e7bb13a3209aa31d734a9012f39e82614acc6b7
[pr1]: https://github.com/urkrass06-oss/HBM-1.20.1/pull/1
[pr2]: https://github.com/urkrass06-oss/HBM-1.20.1/pull/2
[z-build]: https://github.com/urkrass06-oss/HBM-1.20.1/blob/d158d8305fd13322fd711772dbe533f7ee19aebf/build.gradle
[z-mods]: https://github.com/urkrass06-oss/HBM-1.20.1/blob/d158d8305fd13322fd711772dbe533f7ee19aebf/src/main/resources/META-INF/mods.toml
[z-entry]: https://github.com/urkrass06-oss/HBM-1.20.1/blob/d158d8305fd13322fd711772dbe533f7ee19aebf/src/main/java/com/hbm/HbmPort.java
[m]: https://github.com/Raptor324/HBM-Modernized/tree/0365cef5956016913095eeeb9366f26c601ca9a0
[m-license]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/LICENSE
[m-readme]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/README.md
[m-properties]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/gradle.properties
[m-settings]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/settings.gradle.kts
[m-build]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/build.forge.gradle.kts
[m-version]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/versions/1.20.1-forge/gradle.properties
[m-catalog]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/gradle/libs.versions.toml
[m-plugin]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/build-logic/src/main/kotlin/ModPlatformPlugin.kt
[m-daemon]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/gradle/gradle-daemon-jvm.properties
[m-ci]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/.github/workflows/ci.yml
[m-release]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/.github/workflows/gradle.yml
[m-entry]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/main/ForgeEntrypoint.java
[m-main]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/main/MainRegistry.java
[m-platform]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/platform/PlatformHooks.java
[m-blocks]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/block/ModBlocks.java
[m-items]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/item/ModItems.java
[m-be]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/blockentity/ModBlockEntities.java
[m-entities]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/entity/ModEntities.java
[m-recipes]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/recipe/ModRecipes.java
[m-datagen]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/datagen/DataGenerators.java
[m-config]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/config/ModClothConfig.java
[m-packets]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/network/ModPacketHandler.java
[m-energy]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/api/energy/EnergyNetworkManager.java
[m-energytick]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/api/energy/EnergyNetworkTickHandler.java
[m-fewrapper]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/api/energy/HbmForgeWrapper.java
[m-fluidnet]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/api/fluids/FluidNet.java
[m-tank]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/inventory/fluid/tank/FluidTank.java
[m-fluidtests]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/docs/fluid-pipe-parity-test-matrix.md
[m-multistub]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/multiblock/MultiblockStructureStubs.java
[m-factory]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/blockentity/machines/MachineChemicalFactoryBlockEntity.java
[m-breeder]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/blockentity/machines/MachineBreederBlockEntity.java
[m-watz]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/blockentity/machines/MachineWatzPowerplantBlockEntity.java
[m-zirnox]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/blockentity/machines/MachineZirnoxBlockEntity.java
[m-zirnoxblock]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/block/machines/MachineZirnoxBlock.java
[m-rbmk]: https://github.com/Raptor324/HBM-Modernized/tree/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/blockentity/machines/rbmk
[m-rbmkpacket]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/network/RBMKConsoleControlPacket.java
[m-radmanager]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/radiation/ChunkRadiationManager.java
[m-prism]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/radiation/ChunkRadiationHandlerPRISM.java
[m-mk5]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/entity/logic/EntityNukeExplosionMK5.java
[m-fallout]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/entity/effect/EntityFalloutRain.java
[m-satellite]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/satellite/Satellite.java
[m-worldgen]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/worldgen/ModWorldGen.java
[m-renderdoc]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/docs/systems/rendering_system_new.md
[m-resist]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/powerarmor/resist/DamageResistanceHandler.java
[m-cargo]: https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/resources/assets/hbm_m/models/block/doors/cargo_door.obj
[o]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/tree/aee05a40f10fb7bb9b042b65eccaa449ecc1672d
[o-readme]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/README.md
[o-license]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/LICENSE
[o-lesser]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/LICENSE.LESSER
[o-build]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/build.gradle
[o-ref]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/lib/RefStrings.java
[o-properties]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/gradle.properties
[o-cofh]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/cofh/api/package-info.java
[o-ability]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/handler/ability/IToolAreaAbility.java
[o-crab]: https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/render/model/ModelCrab.java
