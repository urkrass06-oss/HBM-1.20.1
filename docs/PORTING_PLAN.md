# Portierungsplan: HBM 1.7.10 → Forge 1.20.1

Stand: **19. Oktober 2026, ausschließlich Planung und statische Bestandsaufnahme**. Die in diesem Dokument beschriebenen Zielarchitekturen und Prüfungen sind noch nicht implementiert oder ausgeführt. Der aktuelle Änderungsumfang besteht aus README, diesem Plan und der [Feature-Matrix](FEATURE_MATRIX.md).

## 1. Ziel, Umfang und Referenzstand

Ziel ist eine möglichst vollständige Portierung des Originals auf Minecraft **1.20.1 / Forge 47.x / Java 17** mit gleicher Progression, denselben Systemen, Rezepten, Ressourcen, Maschinen, Gefahren, Waffen und möglichst gleicher Darstellung. Technische Anpassungen an Minecraft und Forge sind notwendig; neue Spielinhalte und neue Balanceentscheidungen sind nicht Teil des Ziels. Für technisch unvermeidbare Abweichungen werden später Ursache, betroffene Matrix-IDs und Auswirkungen dokumentiert.

| Referenzmerkmal | Verifizierter Wert / Originalbeleg |
| --- | --- |
| Original | <https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT> |
| Untersuchte Branchspitze | `master`, am 19.10.2026 ausgelesen und anschließend durch SHA fixiert |
| Commit | [`aee05a40f10fb7bb9b042b65eccaa449ecc1672d`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/commit/aee05a40f10fb7bb9b042b65eccaa449ecc1672d) |
| Commitdatum | 19.10.2026, 11:03:49 UTC (`13:03:49 +0200`) |
| Commitbetreff | `Merge pull request #3424 from Xpl0itR/fixes` |
| Mod-ID / Name | `hbm` / `Hbm's Nuclear Tech Mod`, `com/hbm/lib/RefStrings.java` |
| Buildversion | `mod_version=1.0.27`, `mod_build_number=5846` → `1.0.27_X5846`, `gradle.properties` und `build.gradle` |
| Laufzeitversion | `1.0.27 BETA (5846)`, `com/hbm/lib/RefStrings.java` |
| Originalplattform | Minecraft `1.7.10`, Forge `1.7.10-10.13.4.1614-1.7.10`, Java-Quell-/Zielversion `1.8`, `build.gradle` |
| Originalwerkzeuge | Gradle-Wrapper `4.4.1`; ForgeGradle-Fork `com.anatawa12.forge:ForgeGradle:1.2-1.0.+` (dynamisch, kein vollständig aufgelöster Dependency-Lock) |

Die Buildversion ist aus dem Quellstand abgeleitet. Ein Tag, eine veröffentlichte JAR oder ein reproduzierbarer Originalbuild wurden damit nicht verifiziert. Spätere Upstreamänderungen werden separat bewertet und verändern die Referenz nicht stillschweigend.

Verkürzte Originalpfade wie `main/MainRegistry.java` sind relativ zu [`src/main/java/com/hbm/`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/tree/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm). Pfade mit `com/`, `api/` oder `cofh/` beginnen unter `src/main/java/`; explizite Build-/Ressourcenpfade beginnen an der Repositorywurzel. Links sind auf den vollständigen Referenzcommit fixiert.

## 2. Methode und Grenzen der Bestandsaufnahme

Untersucht wurden der Git-Dateibaum, Build-/Metadaten, die zentralen Registrierungs- und Proxyklassen, API-/Systemklassen sowie die Klassen- und Ressourcenfamilien der Feature-Matrix. Gezählt wurden Dateien, keine registrierten Spielobjekte: eine Klasse kann viele Gegenstände oder Varianten registrieren; vorhandener Quellcode beweist noch keine Erreichbarkeit im Spiel.

Reproduzierbare statische Zählung in einem separaten Checkout des Originals:

```bash
git clone https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT.git hbm-original
cd hbm-original
git checkout --detach aee05a40f10fb7bb9b042b65eccaa449ecc1672d
git rev-parse HEAD
git ls-files 'src/main/java/*.java' | wc -l
git ls-files 'src/main/resources/*' | wc -l
git status --porcelain
```

Git-Pfadfilter erfassen hier auch Unterverzeichnisse. Die Zählung ergibt **3.484 Java-Dateien**: **3.409** unter `com.hbm`, **63** unter `api.hbm`, **12** unter `cofh.api` einschließlich `energy`; außerdem **7.508 Ressourcendateien**. Unter `assets/hbm` liegen 7.504 Dateien, darunter 6.004 PNGs, 517 OBJ-Modelle, 523 OGG-Dateien, 271 JSON-Dateien, 83 NBT-Dateien und 11 `.lang`-Dateien. Diese Zahlen sind Aufwandssignale, keine Vollständigkeitsquote eines Ports.

Die Matrix erfasst System- und Inhaltsfamilien. Die spätere Einzelinventur muss jede registrierte ID, Metadatenvariante, Rezeptdefinition, Fluidart, Entität und Ressource auf eine Matrix-ID abbilden. Noch ungeprüft sind insbesondere vollständige Laufzeitregistrierung, exakte numerische Vergleichswerte aller Systeme, reproduzierbare Builds und alle Asset-Einzellizenzen. Es wurden keine Builds, Client-/Serverstarts oder Spieltests ausgeführt.

## 3. Java-Paketstruktur

Gezählt wird jeweils der gesamte Teilbaum des unmittelbar unter `com.hbm` liegenden Pakets.

| Paket unter `com.hbm` | Java-Dateien | Hauptaufgabe |
| --- | ---: | --- |
| `blocks` | 628 | Blöcke, Maschinenhüllen, Multiblockteile, Bomben und Reaktorkomponenten |
| `render` | 599 | Block-, Item-, Entity- und TileEntity-Darstellung, Modelle und Shader |
| `inventory` | 505 | Container/GUI, Rezepte, Materialien, HBM-Fluids und Tanks |
| `items` | 452 | Bauteile, Brennstoffe, Werkzeuge, Rüstung und mehrere Waffensysteme |
| `tileentity` | 398 | Serverseitige Maschinenzustände, Transport, Reaktoren, Geschütze |
| `entity` | 185 | Lebewesen, Projektile, Fahrzeuge und logische Entitäten |
| `handler` | 137 | Ereignisse, Strahlung, Neutronen, Verschmutzung, Kompatibilität und NEI |
| `world` | 86 | Erze, Strukturen, Biome und Welt-/Providerlogik |
| `particle`, `util` | je 55 | Partikeleffekte und gemeinsame Hilfsfunktionen |
| `explosion` | 47 | Mehrere Explosionstypen und großflächige Weltveränderung |
| `wiaj` | 34 | Ingame-Präsentationen und animierte Erläuterungen |
| `packet` | 29 | Paketregistrierung und bidirektionale Synchronisation |
| `hazard` | 22 | Gefahrenregister, Typen, Modifikatoren und Transformationen |
| `config` | 19 | Globale und systemspezifische Konfiguration |
| `saveddata` | 18 | Weltpersistenz, unter anderem Satelliten und Einschlagsfolgen |
| `module` | 17 | Wiederverwendbare Maschinen- und Waffenbausteine |
| `crafting`, `interfaces`, `uninos` | je 16 | Crafting/Sonderrezepte, Schnittstellen, Transportnetzwerkbasis |
| `main` | 14 | Modstart, Proxies und zentrale Initialisierung |
| `commands` | 13 | Client-/Serverbefehle und Diagnosewerkzeuge |
| `creativetabs`, `itempool`, `sound` | je 9 | Kreativkategorien, Beutetabellen/Pools und Klangverwaltung |
| `animloader`, `lib`, `qmaw` | je 6 | Animationen, Konstanten und textuelle Ingame-Dokumentation |
| `extprop` | 2 | Zusätzliche Spieler-/Lebewesendaten |
| `potion` | 1 | Statuseffekte |

Zusätzlich enthält `api.hbm` eigene Energie-/Fluid-/Netzwerk- und weitere Integrationsschnittstellen. `cofh.api` einschließlich `cofh.api.energy` ist eingebundene Drittanbieter-API und muss getrennt hinsichtlich Herkunft und zukünftiger Notwendigkeit betrachtet werden. Die Paketstruktur des Originals bleibt die fachliche Orientierung; eine zukünftige Aufteilung nach Client, gemeinsamem Datenmodell und Serververhalten soll das Portieren erleichtern, ohne die Inhalte neu zu gestalten.

## 4. Technische Hauptsysteme und Migrationsentscheidungen

### 4.1 Start, Registrierung und Konfiguration

`com/hbm/main/MainRegistry.java` orchestriert FML-Lebenszyklus, statische Block-/Itemregistrierung, Materialien, Entitäten, TileEntities, Rezepte, Ereignisse, Weltgenerierung und Integrationen. `main/ClientProxy.java` und `main/ServerProxy.java` trennen Teile der Clientregistrierung. Zentrale Inhaltsquellen sind `blocks/ModBlocks.java`, `items/ModItems.java`, `tileentity/TileMappings.java` und `entity/EntityMappings.java`.

Es gibt zwei PreInit-Handler und eigene Missing-Mappings-/Tile-Altnamen-Behandlung. `main/ModEventHandler.java` verarbeitet Welt-/Server-Tickphasen einschließlich Netzwerkaktualisierung und Paketabschluss. Diese Reihenfolge ist Teil der Bestandsaufnahme. `lib/HbmWorld.java` registriert sowohl den älteren `HbmWorldGen` als auch `world/gen/NTMWorldGenerator`; die spätere Inventur muss beide Generierungspfade berücksichtigen.

Ziel: kontrollierte Übertragung nach `DeferredRegister`/`RegistryObject`, Forge-Lebenszyklus und Client-Registrierungsevents. Statische Initialisierungsreihenfolgen werden explizite Abhängigkeiten. Legacy-Metadaten müssen einzeln zu BlockStates, getrennten IDs oder Item-NBT zugeordnet werden; numerische IDs und Metadaten sind kein moderner Registrierungsvertrag. Vorhandene Namen und die Mod-ID `hbm` sollen erhalten bleiben, soweit technisch möglich. Die Trennung logischer Seite und physischer Clientdistribution wird auf einem Dedicated Server geprüft. `ForgeConfigSpec` und serverseitig verbindliche Werte ersetzen die alte `Configuration`-Nutzung; Standardwerte und relevante Neustart-/Reloadregeln werden je Originaloption erfasst.

### 4.2 Maschinen, Multiblocks und Datenhaltung

`tileentity`, `module/machine`, `interfaces/IMultiblock.java`, `handler/MultiblockHandler.java`, `handler/MultiblockHandlerXR.java` und `tileentity/machine/TileEntityMultiblock.java` bilden Maschinenzustände, Teilblöcke, Orientierung und Verarbeitung ab. Inventare und GUI sind über `inventory/container` und `inventory/gui` gekoppelt. Persistente Welt- und Lebewesendaten liegen unter `saveddata` und `extprop`, etwa `extprop/HbmLivingProps.java`.

Ziel: BlockEntities mit seitengerechten Tickern, `AbstractContainerMenu`/Screens und klar versionierten NBT-Verträgen. Inventar-/Fluid-/Energie-Capabilities werden pro Seite angeboten und bei Entladen/Entfernen sauber invalidiert. Weltzustände erhalten `SavedData`, Entity-/Spielerzustände geeignete Forge-Capabilities einschließlich Tod, Klonen, Dimensionswechsel und Login. Multiblocks müssen Platzierung, Drehung, Teilabbau, Explosionsschaden und Chunkgrenzen ohne Duplikation oder Zustandsverlust behandeln. Das neue Speicherformat braucht eigene Versionsfelder; ein automatischer 1.7.10-Weltimport ist damit nicht zugesagt.

### 4.3 Transportnetze, Energie und Fluids

`api/hbm/energymk2/PowerNetMK2.java`, `api/hbm/fluidmk2/FluidNetMK2.java`, `com/hbm/uninos` sowie `inventory/fluid/FluidType.java` und `inventory/fluid/tank/FluidTank.java` zeigen ein eigenes Netzwerk- und Stoffmodell. HBM-Energie verwendet `long`-Werte; Fluidverhalten umfasst eigene Typen, Eigenschaften und Druckstufen.

Ziel: Originalverteilung, Einheiten, Kapazitäten, Druck- und Stoffregeln erhalten. Forge Energy und `IFluidHandler` werden bei Bedarf als begrenzte Außenadapter verwendet. HE wird nicht pauschal durch FE ersetzt; Konvertierung, Rundung, `int`-Grenzen und Überlauf werden ausdrücklich festgelegt. Die vorhandenen RF-Konverter sind asymmetrisch: standardmäßig **5 HE → 1 RF** in `tileentity/network/TileEntityConverterHeRf.java` und **2 RF → 5 HE** in `TileEntityConverterRfHe.java`, jeweils konfigurierbar. Entsprechend wird keine ungeprüfte Gleichsetzung von HBM-Fluidmengen mit Forge-mB angenommen. Netzwerkbildung, Auftrennung, Zusammenführung, Schleifen und Chunkentladung benötigen Tests zur Erhaltung von Energie, Stoffen und Inventaren unter Berücksichtigung beabsichtigter Verluste.

### 4.4 Rezepte, Materialien und Progression

`inventory/recipes`, `inventory/recipes/loader/SerializableRecipe.java`, `inventory/OreDictManager.java`, `inventory/material` und `crafting` enthalten Maschinenrezepte, konfigurierbare Rezepte, Materialien und Sondercrafting. Die alte OreDictionary-Verknüpfung und NEI-Anzeige beeinflussen Spielbarkeit und Modpackintegration.

Ziel: OreDictionary-Zuordnungen nachvollziehbar in Tags überführen; Rezepttypen und Serializer für HBM-Maschinen definieren. Datengetriebene Rezepte sind dort sinnvoll, wo sie die Originalparameter abbilden; dynamische Brennstoff-/NBT-/Prozessregeln bleiben explizit implementierte Logik. Zeit, Energie, Mengen, Nebenprodukte, Wahrscheinlichkeiten und Freischaltbedingungen bilden den Vergleichsvertrag. Für moderne Rezeptanzeige wird JEI als optionale Integration geplant; die maschinellen Regeln bleiben unabhängig davon vollständig.

`SerializableRecipe.java` unterscheidet Java-Defaults, lokale JSON-Overrides und erzeugte Vorlagen; `main/ModEventHandler.java` enthält optionalen Rezeptabgleich beim Login. Override-Priorität, Vorlagenerzeugung, `/reloadrecipes` und der standardmäßig ausgeschaltete Serverabgleich werden ausdrücklich inventarisiert und auf moderne Reload-/Synchronisationsmechanismen abgebildet. Eine bloße Umstellung auf Rezept-Serializer erfüllt diesen Vertrag noch nicht.

### 4.5 Netzwerk und Autorität

`packet/PacketDispatcher.java` und `packet/toclient`/`packet/toserver` verwenden die alte FML-Netzwerkschicht über einen eigenen Netty-Codec in `main/NetworkHandler.java`. `handler/threading/PacketThreading.java` organisiert Paketvorbereitung und Flush-/Warteregeln. Neben festen Nachrichtentypen gibt es generische Synchronisationspfade; die Zahl der Java-Dateien ist daher keine Zahl aller übertragenen Operationen.

Ziel: Forge-1.20.1-`SimpleChannel` mit Protokollversion, eindeutigen Nachrichten, expliziter Richtung und Verarbeitung auf dem zuständigen Hauptthread. Der Server entscheidet über Inventaränderungen, Waffen, Energie und Weltfolgen. Jede Clientanfrage prüft Berechtigung, Menü-/Objektbezug, Distanz, Dimension und Wertebereiche. Tracking, Chunk-Sichtbarkeit, Erstzustand und Delta-Updates werden getrennt beschrieben. Große Weltfolgen dürfen keine unbeschränkten NBT-/Effektpakete erzeugen.

### 4.6 Strahlung, Umwelt, Reaktoren und Explosionen

Strahlung ist ein eigenständiges System mit mehreren Implementierungen unter `handler/radiation`, zentralem `ChunkRadiationManager`, `hazard` und Lebeweseneffekten. `handler/neutron` und `handler/pollution` ergänzen Neutronen und Umweltlast. Reaktorfamilien unter `tileentity/machine` und Unterpaketen haben unterschiedliche Simulationsmodelle. `explosion` und logische Entitäten organisieren großflächige Schäden, Fallout und Folgeeffekte.

Ziel: unterstützte Strahlungsmodi und deren Konfiguration getrennt erfassen. Quellen, Abschirmung, Verteilung, Dosis, Schutz und Zerfall werden mit Originalmessungen verglichen. Reaktoren werden familienweise portiert: zuerst Grundlagen und Brennstoffkreisläufe, dann Wärme-/Neutronen-/Kühlmittelmodell, Steuerung und schließlich Unfälle. Keine gemeinsame Ersatzsimulation darf Unterschiede zwischen Reaktorfamilien verwischen.

Aktive und lediglich vorhandene Varianten sind zu unterscheiden: [`ChunkRadiationManager.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/handler/radiation/ChunkRadiationManager.java#L15) verwendet standardmäßig **Simple**; [`RadiationConfig.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/config/RadiationConfig.java#L54) schaltet **PRISM** nur auf Wunsch ein, Standardwert `false`. PRISM hat alte Annahmen von Y=0…255 und 16 Sections, die an moderne Bauhöhen angepasst werden müssen. Weitere Handler im Paket sind kein Beleg zusätzlicher aktiver Spielmodi.

Großexplosionen brauchen einen kontrollierten Arbeitsplan über Ticks und ein ausdrücklich definiertes Verhalten bei Chunkentladung und Serverneustart. Im aktiven [`EntityNukeExplosionMK5.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/entity/logic/EntityNukeExplosionMK5.java#L74)-Pfad wird `ExplosionNukeRayBatched` verwendet; die Auswahl der vorhandenen Parallelengine ist auskommentiert. Die Klasse speichert nur `ticksExisted`, daher ist eine vollständige Wiederaufnahme laufender MK5-Explosionen keine belegte Originalgarantie. Neustart-/Abbruchverhalten wird zunächst vermessen und spezifiziert, ohne inaktive Engines stillschweigend zu aktivieren. Wenn Berechnungen ausgelagert werden, dürfen sie ausschließlich auf geeigneten Datenkopien arbeiten; Zugriffe und Änderungen an der Welt erfolgen auf dem Serverthread. Der Umfang der Zerstörung und die Nachwirkungen bleiben Teil der Originaltreue. Optimierungen müssen gegenüber dem Original auf Radius, Materialien, Abschirmung und Zeitschritte geprüft werden.

### 4.7 Welt, Entitäten und Clientdarstellung

`world` enthält Erze, geologische Schichten, Strukturen, Biome und `WorldProviderNTM.java`; `entity` umfasst Projektile, Lebewesen und logische Systeme. `render`, `particle`, `sound`, `animloader`, `qmaw` und `wiaj` bilden die sicht- und hörbare Präsentation sowie Ingame-Hilfe ab. Die vielen OBJ-Modelle und Waffenanimationen machen die Clientportierung zu einem eigenen erheblichen Arbeitspaket.

Ziel: konfigurierte/platzierte Features, Biome-Modifier, Struktur-/Template- und Lootsysteme passend zu 1.20.1. Die Weltuntergrenze, Höhenbereiche, neue Vanilla-Biome und Chunkgenerierung verlangen eine dokumentierte Zuordnung der Originalverteilung; gleiche Seeds liefern nicht automatisch gleiche Welten. Einschlagsfolgen und Himmelseffekte müssen über geeignete moderne Hooks nachgebildet werden, ohne ungeprüft den Overworld-Provider zu ersetzen. Entitäten benötigen moderne Daten-Synchronisation, Spawn-/Trackingregeln, Attribute und Schadensarten; Chunkloading wird gesondert portiert.

Legacy-TESR, direkte OpenGL-Aufrufe und alte Itemrenderer werden nach BlockEntity-/Entity-Renderern, Model-/RenderType-/Buffer- und Shader-Schnittstellen übertragen. Für OBJ-Modelle und Animationen wird ein gemeinsamer Lade-/Renderpfad erprobt, bevor alle Assets konvertiert werden. GUI, HUD, F1-Präsentationen, Handbuch, Audio und Übersetzungen werden jeweils zusammen mit ihrer Funktionsfamilie abgenommen. `.lang` wird nach JSON überführt; Schlüssel, Platzhalter, Formatierung und Originaltexte bleiben nachvollziehbar. `util/AchievementHandler.java`, `util/StatHelper.java` und die Erfolgsregistrierung in `MainRegistry` benötigen eine Zuordnung zu modernen Advancements und Statistiken mit gleichen Auslösern, ohne neue Progressionssperren.

### 4.8 Access Transformer, Eingriffe und Integrationen

`build.gradle` deklariert `FMLAT: HBM_at.cfg`; `src/main/resources/META-INF/HBM_at.cfg` öffnet unter anderem Entity-, KeyBinding-, Rendering-, Container- und Weltfelder. Im untersuchten `src/main` wurde kein eigener `IFMLLoadingPlugin`/`IClassTransformer`- oder ASM-Coremod-Einstieg gefunden. Access Transformer und Reflexion sind trotzdem relevante Eingriffe und dürfen nicht als Beleg einer unverändert übertragbaren API gelten.

Ziel: jeden Eingriff einzeln modernen Events/APIs zuordnen und nur verbleibende Notwendigkeiten gezielt lösen. Alte Workarounds für 1.7.10 werden auf ihr eigentliches Nutzerverhalten geprüft; beispielsweise werden Renderdistanzlimits nicht blind auf die moderne Plattform übertragen. Verhaltensrelevante Abweichungen erhalten einen Eintrag in der Matrix.

`build.gradle` bindet CodeChickenCore/Lib und NEI sowie compile-only InventoryTweaks, OpenComputers und AE2 ein; weitere Kopplungen liegen unter `handler` und `util`. Integrationen werden nach verfügbaren 1.20.1-APIs bewertet und optional isoliert. Fehlende Gegenstücke werden als offen ausgewiesen und zählen nicht als erledigte Parität. Basisspiel und Dedicated Server müssen ohne optionale Mods starten. Die Verfügbarkeit alter Integrationen wird nicht zugesichert.

`handler/HTTPHandler.java` ruft Versionsinformationen, Tipps und Soyuz-Daten aus externen Quellen ab; `inventory/gui/LoadingScreenRendererNT.java` gestaltet die Ladeanzeige. Diese Originalfunktionen werden einschließlich Konfiguration und Offlineverhalten erfasst. Eine spätere Versionsprüfung für den Port darf nicht ungeprüft den 1.7.10-Upstream als eigenen Versionsstand behandeln.

## 5. Entwicklungsphasen und Abhängigkeiten

Die Matrix verwendet die folgenden Phasen. Jede Familie umfasst Serverlogik, Speichern, Bedienung und notwendige Clientdarstellung; P7 verschiebt diese Teile nicht pauschal ans Projektende.

| Phase | Inhalt und Reihenfolge | Überprüfbares Ergebnis / Abschlussbedingung |
| --- | --- | --- |
| **P0 Referenz und Inventur** | Commit und Lizenzlage festhalten; Matrix anlegen; anschließend Laufzeitregistrierung, Varianten, Assets und Messfälle einzeln erfassen. | Der vorliegende PR liefert die statische Grundlage. P0 bleibt bis zur ID-genauen Inventur und funktionierenden Referenzumgebung unvollständig. |
| **P1 Forge-Grundgerüst und Datenvertrag** | Passendes 1.20.1-MDK mit konkreter Forge-47.x-/ForgeGradle-/Wrapper-Version festlegen; Java 17, Registries, Seitenaufteilung, Konfiguration, Ressourcenlayout, NBT-/ID-Verträge und später CI einrichten. | Client und Dedicated Server starten; kleines technisches Registrierungs-/Speicherszenario funktioniert. Noch keine breite Inhaltsmigration. |
| **P2 Basissysteme und Netze** | Persistenz, Pakete, Inventare, Menüs, BlockEntity-Basis, Multiblocks, Energie-/Fluidnetze und Chunk-Lebenszyklus; erste vertikale Strecke aus Originalgenerator, Leitung, Speicher und Verbraucher. | Energie-/Stoffbilanz sowie Speichern/Neuladen und Multiplayerbedienung bestehen; ein vollständiger Originalablauf ist vergleichbar. |
| **P3 Industrie und Chemie** | Materialien/Tags, Grundcrafting, Rezepte, Brennstoffe, Prozessmaschinen, Rohstoffgewinnung, Öl-/Chemieketten und Automatisierung entlang der Originalprogression. | Ausgewählte vollständige Produktionsketten stimmen in Ein-/Ausgaben, Zeiten, Kosten und Nebenprodukten; danach systematische Familienabdeckung. |
| **P4 Reaktoren und Umwelt** | Gefahren, Strahlung, Neutronen, Verschmutzung, Brennstoffkreisläufe; Reaktorfamilien und Thermik; Unfall- und Langzeitfolgen. Benötigte Explosionsbausteine aus P5 werden vor den jeweiligen Unfalltests bereitgestellt. | Jede Reaktorfamilie besteht Normalbetrieb, Regelung, Ausfall, Neustart und Unfallvergleich; Strahlung und Schutzmaßnahmen stimmen innerhalb dokumentierter Toleranzen. |
| **P5 Waffen und Explosionen** | Sprengstoffe, Bomben, große Explosionen, Raketen/Starttechnik, Geschütze, Waffen-/Munitionssysteme und zugehörige Effekte; Satellitenfunktionen dort, wo ihre Start-/Waffentechnik benötigt wird. | Serverautorisierte Benutzung, Flug/Tracking, Chunkwechsel, Schadensbilder, Fallout sowie spezifiziertes Neustart-/Abbruchverhalten lang laufender Effekte sind geprüft. |
| **P6 Welt, Lebewesen und übrige Inhalte** | Vollständige Geologie/Erzverteilung, Strukturen und Loot, Biome, Weltfolgen, Mobs/Bosse, Ausrüstung, Werkzeuge, Verbrauchsgüter und weitere Inhaltsfamilien. Weltgenerierungsbasis und benötigte Rohstoffe werden schon vor P3 bereitgestellt. | Neue Testwelten erlauben die komplette Originalprogression; Spawn-, Loot- und Umweltverhalten sind belegt. |
| **P7 Vollständigkeit und Freigabe** | Verbleibende Darstellung, Bedienung, Audio/Animation, Übersetzung, Handbuch, optionale Integrationen sowie vollständige Paritäts-, Stabilitäts- und Leistungsprüfung. | Keine ungeklärten Original-IDs; Matrix hat Nachweise je abgeschlossenem Eintrag; Release enthält Herkunft, Lizenztexte, Quellcode und dokumentierte Abweichungen. |

Abhängigkeiten: **P0 → P1 → P2 → P3**; **P4** benötigt P2/P3 und Unfallbausteine aus P5; **P5** benötigt P2 und die jeweiligen Industrieprodukte; **P6** liefert seine Weltbasis früh, die vollständigen Inhalte später; **P7** schließt alle Familien ab. Rendering, Rezepte und Lokalisierung laufen innerhalb jeder Familie mit. Phasen sind fachliche Arbeitspakete, keine Zusage fester Termine oder gleicher Aufwände.

## 6. Originaltreue und Prüfstrategie

1. **Referenz erfassen:** Original unter fixiertem Commit mit festgehaltenen Konfigurationen, separater Java-8-Umgebung und dokumentierten Abhängigkeiten starten. Testaufbauten, Seeds, Eingaben, NBT-Zustände, Messwerte, Bilder und relevante Geräusche aufzeichnen. Der alte dynamische ForgeGradle-Bezug muss für reproduzierbare Vergleiche aufgelöst und protokolliert werden, ohne den Referenzquellcode zu verändern.
2. **IDs und Daten abgleichen:** Alte IDs und Metadatenvarianten nach Ziel-ID/BlockState/NBT und Matrix-ID abbilden; Rezepte, Mengen, Laufzeiten, Fluid-/Brennstoffdaten, Loot, Konfiguration und Übersetzungsschlüssel gegenüberstellen. Nicht erreichbare oder veraltete Originaldefinitionen nachweisen und ausdrücklich kennzeichnen.
3. **Verhalten vergleichen:** Pro Matrixzeile reproduzierbare Eingaben und beobachtbare Ergebnisse festhalten. Deterministische Prozesswerte sollen exakt übereinstimmen. Numerische Simulationen und Zufallsverhalten erhalten begründete, vorab festgelegte Toleranzen bzw. statistische Stichproben; keine pauschale Toleranz für alle Systeme.
4. **Gezielt testen:** Später geeignete Java-Tests für Mathematik, Einheiten, Rezept- und Simulationsregeln; Forge-GameTests für relevante Welt-/Blockinteraktionen; echte Client- und Dedicated-Servertests für Rendering, Menüs, Netzwerk und Integration. Visuelle Vergleiche ergänzen funktionale Messwerte.
5. **Grenzfälle prüfen:** Speichern/Neustart, Chunkgrenzen und Entladen, mehrfache Netzzusammenführung, Multiblockzerstörung, Tod/Respawn, Dimensionswechsel und mehrere Spieler. Für Maschinen und Transporte müssen Duplikation sowie unbeabsichtigter Energie-/Stoffverlust ausgeschlossen werden; originale Verluste bleiben Teil des Vergleichsvertrags.
6. **Last messen:** Repräsentative Industrie-, Reaktor-, Netzwerk- und Explosionswelten mit festen Konfigurationen verwenden. Tickzeit, Speicher, Paketmenge und Wiederaufnahmezeiten auf dokumentierter Hardware messen. Grenzwerte erst anhand der Baseline festlegen; Optimierungen dürfen die Physik und Spielbalance nicht stillschweigend verändern.

Für spätere Implementierungs-PRs gilt: eine überschaubare Funktionsfamilie, betroffene Matrix-IDs, Originalbelege, Änderungsgrund, Testnachweis und bekannte Abweichungen. Die Statusfolge ist **Nicht begonnen → In Arbeit → Implementiert → Verifiziert**. Ein Eintrag wird erst **Verifiziert**, wenn Serververhalten, Speichern, Bedienung/Darstellung und Originalvergleich nachgewiesen sind. Ein kompilierendes Grundgerüst oder vorhandene Texturen erfüllen dies nicht.

Der Planungs-PR selbst wird ausschließlich auf Quellenbezüge, konsistente Versions-/Phasenangaben, Markdown-Verweise, Matrixstruktur und den dokumentarischen Diff geprüft. Er behauptet keine Laufzeitvalidierung.

## 7. Risiken, Entscheidungen und offene Arbeit

| Risiko / offener Punkt | Vorgehen |
| --- | --- |
| Große Funktions- und Assetmenge; versteckte Legacyvarianten | ID-genaue Inventur in P0 fortführen; keine Fortschrittsquote aus Dateizahlen ableiten. |
| Alte statische Initialisierung und Querverweise | Registrierungsreihenfolge und Abhängigkeiten vor der familienweisen Migration aufzeichnen. |
| Veränderte Weltgrenzen und Generierungs-APIs | Höhen-/Biomezuordnung dokumentieren; Rohstoffzugang und Häufigkeiten vergleichen. |
| HE-/Fluidmodell passt nicht direkt in Forge-Capabilities | Eigenes Domänenmodell erhalten und Außenadapter mit geprüften Einheiten und Grenzen bauen. |
| Lang laufende Weltfolgen und Chunkloading | Hauptthreadregeln, Datenlebensdauer, Speicherung und Wiederaufnahme früh entwerfen und messen. |
| Rendering, Waffenanimationen und Modelle | Gemeinsamen modernen Lade-/Renderpfad mit repräsentativen Originalassets erproben. |
| Netzwerk- und Inventarfehler | Autorität und Paketgrenzen definieren; Multiplayer und ungültige Anfragen gezielt prüfen. |
| Historische Buildabhängigkeiten | Aufgelöste Referenzumgebung protokollieren; Java 8 und 17 strikt getrennt halten. |
| Fehlende moderne Gegenstücke für optionale Integrationen | Verfügbarkeit prüfen, Integrationen isolieren und unbelegte Parität offen lassen. |
| Quell- und Assetlizenzen unterschiedlicher Herkunft | Herkunft je übernommener Datei erfassen; notwendige Vermerke und Lizenztexte mitführen. |
| Direkter Import alter Spielstände | Kein zugesicherter Teil dieses Plans. Falls später gewünscht: eigenen Konverter mit ID-, Metadaten-, NBT- und Weltgenerierungsanalyse planen. |

Vor Beginn der jeweiligen Umsetzung werden insbesondere die konkrete Forge-/MDK-Version, die vollständige Variantenabbildung, Capability-/Paketverträge, Verhalten alter Integrationen und Einzelherkunft der Assets geklärt. Diese technischen Entscheidungen können innerhalb des beschriebenen Ziels getroffen werden; sie erweitern den Funktionsumfang nicht.

## 8. Technische Referenzprojekte und Lizenzhinweise

Das Original bleibt alleinige fachliche Referenz. Für Rebirth und Modernized werden getrennte Notizen zur technischen Fragestellung geführt; beobachtete Lösungen müssen gegen den Originalvertrag geprüft werden. Es wird in diesem PR kein Code aus diesen Projekten übernommen.

| Technische Referenz | Am 19.10.2026 geprüfter Commit | Einordnung |
| --- | --- | --- |
| [10MeV/HBM-NTM-Rebirth](https://github.com/10MeV/HBM-NTM-Rebirth) | [`1ad19f8f178394d32b681de2d9fe2c255c25a286`](https://github.com/10MeV/HBM-NTM-Rebirth/commit/1ad19f8f178394d32b681de2d9fe2c255c25a286) | Minecraft 1.20.1 / Forge 47.2.32 laut `gradle.properties`; README nennt eigene Erweiterungen und Balance. Java-21-Toolchain mit Ziel-Bytecode 17 ist eine projektspezifische Wahl. |
| [Raptor324/HBM-Modernized](https://github.com/Raptor324/HBM-Modernized) | [`0365cef5956016913095eeeb9366f26c601ca9a0`](https://github.com/Raptor324/HBM-Modernized/commit/0365cef5956016913095eeeb9366f26c601ca9a0) | Mehrversionsprojekt; ausschließlich `1.20.1-forge` betrachten. `versions/1.20.1-forge/gradle.properties` nennt Forge 47.4.20. Der NeoForge-Zweig definiert kein Ziel dieses Ports. |

Konkrete verifizierte Lesepunkte sind Rebirths [Datengenerator](https://github.com/10MeV/HBM-NTM-Rebirth/blob/1ad19f8f178394d32b681de2d9fe2c255c25a286/src/main/java/com/hbm/ntm/datagen/HbmDataGenerators.java) und [Batterie-Capability-Provider](https://github.com/10MeV/HBM-NTM-Rebirth/blob/1ad19f8f178394d32b681de2d9fe2c255c25a286/src/main/java/com/hbm/ntm/energy/HbmBatteryItemCapabilityProvider.java) sowie Modernizeds [EnergyNetworkManager](https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/api/energy/EnergyNetworkManager.java) und [ChunkRadiation](https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/src/main/java/com/hbm_m/capability/ChunkRadiation.java). Die Pfade und Buildangaben wurden geprüft; ihre Implementierungen wurden nicht im Detail auditiert und belegen keine Originalparität. Bei späterer Nutzung werden Fragestellung, Referenzcommit, Originalvertrag und eigene technische Entscheidung festgehalten.

Rebirth bezeichnet sein Gesamtwerk in der [README](https://github.com/10MeV/HBM-NTM-Rebirth/blob/1ad19f8f178394d32b681de2d9fe2c255c25a286/README.md) als `GPL-3.0-only` und erhält Hinweise für Originalteile. Modernized führt [GPLv3](https://github.com/Raptor324/HBM-Modernized/blob/0365cef5956016913095eeeb9366f26c601ca9a0/LICENSE). Diese Befunde sind vor jeder späteren Codeübernahme zu berücksichtigen; es wird hier keine abweichende Lizenz für das Original oder dieses Planungsprojekt festgelegt.

Das Original erklärt [LGPL Version 3](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/README.md#license). Die Dateien [`LICENSE`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/LICENSE) (GPLv3-Basistext) und [`LICENSE.LESSER`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/LICENSE.LESSER) (LGPLv3-Zusatzbedingungen) sind zusammen zu lesen. Bei einer späteren Übernahme sind Originalvermerke, Änderungen, passende Lizenztexte und Pflichten zur Bereitstellung des entsprechenden Quellcodes zu berücksichtigen. Die eingebundene CoFH-API enthält im [`package-info.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/cofh/api/package-info.java) einen Team-CoFH-Copyrightvermerk, aber in den untersuchten Dateien keinen separaten ausdrücklichen Lizenztext. Außerdem enthält `handler/ability/IToolAreaAbility.java` einen als CC0 bezeichneten TConstruct-Abschnitt und `render/model/ModelCrab.java` einen fremden Modell-/Generatorheader. Diese Hinweise sind Ausgangspunkte für eine Herkunftsprüfung, keine abgeschlossene Lizenzfreigabe. Für Bibliotheken, Modelle, Texturen, Audio und Animationen ist die individuelle Herkunft noch zu inventarisieren; das Vorhandensein im Repository ersetzt diese Prüfung nicht. Eine technische Referenz begründet keine Übernahmeberechtigung und keine automatische Umlizenzierung.
