# Übernahmestrategie: Modernized als Basis von HBM Complete Port

Stand: **19. Oktober 2026 (UTC)**. Dieser Plan beschreibt spätere Implementierungs-PRs. **In diesem PR werden nur dieser Plan und [MODERNIZED_COMPARISON.md](MODERNIZED_COMPARISON.md) hinzugefügt.** Es werden keine vorhandenen Dateien gelöscht, keine Quellcode-/Assetbestände importiert, keine Lizenzdeklarationen geändert und keine Originalfunktionen als fertig markiert.

## 1. Entscheidung und Zielarchitektur

**Empfehlung: Modernizeds Forge-1.20.1-Variante als zusammenhängende technische Basis übernehmen; das bisherige Grundgerüst und seine Inventur-/Abnahmearbeit darin integrieren.** Die Originalreferenz bleibt die fachliche Spezifikation. Modernizeds eigene Balance, zusätzliche Inhalte und unfertige Platzhalter werden dadurch nicht zum Maßstab des Ports.

| Ansatz | Vorteil | Aufwand / Grenze | Bewertung |
| --- | --- | --- | --- |
| Zusammenhängende Modernized-Basis | Registrierungen, Maschinenbasis, Multiblocks, HE-/Fluidnetze, Rezepte, GUI, Netzwerk und Renderer bleiben zusammen. Fehlende Originalfunktionen können auf vorhandenen Verträgen aufbauen. | GPLv3-konforme Kombination, Build-/JDK-Bereinigung, Namensraumabbildung und viele Paritätskorrekturen erforderlich. Keine Freigabe aller Assets allein durch einen Root-Lizenztext. | **Bevorzugt**, sobald der Basisbuild und die Herkunft des benötigten Bestands geklärt sind. |
| Einzelne Systeme in das aktuelle ForgeGradle-Gerüst kopieren | Kleinerer anfänglicher Import, theoretisch weniger fremde Buildtechnik | Ein „einzelnes“ System hängt oft an Architectury, PlatformHooks, Modregistern, NBT, Paketen, Menüs und Rendering. Diese Schnittstellen müssten wiederholt nachgebaut werden. GPL-Pflichten verschwinden durch kleine Kopien nicht. | Rückfalloption für nachweislich isolierbare Teile, falls M0/M1 die zusammenhängende Basis ausschließen. |
| Weiterhin komplette Neuentwicklung | Direkte Kontrolle aller Verträge | Verwirft den größten Teil vorhandener Modernisierung und verschiebt Spielfunktionen; drei vorhandene Java-Klassen sind keine große Investition in ein konkurrierendes Framework. | Nicht die neue Standardstrategie. Nur nachgewiesene Lücken oder notwendige Ersatzteile eigenständig portieren. |

Das ist eine Entscheidung für eine **Architekturgrundlage**, keine Behauptung, das ganze Original sei in Modernized vorhanden. Konkrete Gegenbeispiele sind Breeder, Watz/Core, PRISM, PWR/Fusion und Teile der Logistik. Ein erfolgreicher Forge-Start allein beendet deshalb keinen Funktionsblock.

### Verbindliche Ausgangsstände

| Rolle | Commit |
| --- | --- |
| Aktives Ziel, `docs/original-porting-plan` | [`d158d8305fd13322fd711772dbe533f7ee19aebf`](https://github.com/urkrass06-oss/HBM-1.20.1/tree/d158d8305fd13322fd711772dbe533f7ee19aebf) |
| Modernized, ausschließlich `1.20.1-forge` | [`0365cef5956016913095eeeb9366f26c601ca9a0`](https://github.com/Raptor324/HBM-Modernized/tree/0365cef5956016913095eeeb9366f26c601ca9a0) |
| Original, fachlicher Referenzstand | [`aee05a40f10fb7bb9b042b65eccaa449ecc1672d`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/tree/aee05a40f10fb7bb9b042b65eccaa449ecc1672d) |

Die vollständige Quellenliste einschließlich `main` und Foundation-Vorläufer steht im [Vergleich, §1](MODERNIZED_COMPARISON.md#1-fixierte-quellen-und-tatsächlicher-zielstand). Ein neuer Upstreamstand ersetzt diese Pins nicht stillschweigend. Release-JARs gelten erst als Referenz, wenn sie einem geprüften Quellstand zugeordnet sind.

### Festlegungen für die Integration

1. **Produktplattform:** Minecraft `1.20.1`, Forge zunächst exakt **47.4.20**, Minecraft-JVM **Java 17**. Der ursprüngliche Pin 47.4.10 wird nicht parallel als gleichwertig getestet behauptet. Das Zurückgehen auf 47.4.10 wäre eine spätere geprüfte Kompatibilitätsentscheidung.
2. **Build-JVM getrennt behandeln:** Modernizeds Gradle-9.3.1-Daemon zunächst mit JDK **21** reproduzieren; Quell-/Ziel-/API-Kompatibilität für die Modlaufzeit auf Java 17 erzwingen und am fertigen Artefakt testen. Nicht pauschal das ganze Zielprojekt auf eine Java-21-Laufzeit umstellen.
3. **Buildtechnik zunächst erhalten:** Stonecutter/ModDev/Architectury und deren Verarbeitungsreihenfolge übernehmen. Nur Forge 1.20.1 in der Integrationsvariante aktiv bauen. NeoForge-/Fabric-Dateien können als inaktive Upstreamquellen erhalten bleiben; ein Mehrloader-Release ist kein Ziel dieses Ports. Keine sofortige Rückportierung der Modernized-Buildlogik auf ForgeGradle 6.
4. **Genau ein aktiver Mod-Einstieg:** Endgültige Mod-ID und öffentlicher Namensraum **`hbm`** gemäß bisherigem Projektvertrag. Zunächst unverändert `hbm_m` im isolierten Upstream-Nachweis, dann ein atomarer Wechsel vor unterstützten Spielständen. Java-Pakete `com.hbm_m` zunächst erhalten, um unnötige Upstreamkonflikte zu vermeiden; Paketname und Registry-ID sind verschiedene Dinge.
5. **Bestehendes Gerüst integrieren:** `HbmPort` später als einzigen Forge-Einstieg verwenden und die bestehende Modernized-Initialisierung über eine explizite Methode mit dem Mod-Eventbus einbinden. Die zweite `@Mod`-Annotation von `ForgeEntrypoint` in der Integrationsvariante deaktivieren. `ClientSetup` in die eine physisch clientseitige Initialisierung einordnen; leere `ModRegistries` nicht zu einem zweiten konkurrierenden Inhaltskatalog ausbauen. Dateien erhalten und gezielt anpassen, keine parallelen Modinstanzen erzeugen.
6. **Daten-/Netzarchitektur:** Eigene HE-Mengen als `long` und Original-Fluiddruck erhalten. Architectury-Netzwerk zunächst beibehalten und absichern. Die bisherige Planung eines `SimpleChannel` ist noch keine Implementierung; sie wird im Datenvertrag auf den tatsächlichen Transport angepasst, statt fertige Paketpfade allein wegen des alten Entwurfs neu zu schreiben. Nachrichtenautorisierung, Speicherformat und fachliches Originalverhalten bleiben davon unabhängige Anforderungen.
7. **Keine Weltimportzusage:** Weder ein Original-1.7.10-Spielstand noch eine Modernized-`hbm_m`-Welt wird durch den Namenswechsel automatisch kompatibel. Vorherige Testwelten getrennt halten. Ein Konverter wäre ein eigenes Vorhaben; Missing-Mappings allein übersetzt weder Metadaten noch NBT oder Weltformate.

## 2. Was aus dem bisherigen Projekt erhalten bleibt

| Bestand in Z | Behandlung |
| --- | --- |
| `docs/FEATURE_MATRIX.md` mit 140 Originalfamilien | Fachlicher Umfang und Abnahmekriterien bleiben. Zusätzlich Herkunft/Modernized-Befund pro Einzelinhalt ergänzen; kein Massenstatuswechsel auf „Implementiert“. |
| `docs/PORTING_PLAN.md`, README | In einem späteren Integrations-PR die überholte Aussage „nur technische Referenz“ und Plattform-/Buildhinweise anpassen; ursprüngliche Bestandsaufnahme nachvollziehbar lassen. |
| `docs/DATA_CONTRACTS.md` | Originaleinheiten, ID-/NBT-Regeln und Serverautorität bleiben. Technische Vorschläge wie SimpleChannel gegen tatsächliche M-Verträge prüfen und versioniert fortschreiben. |
| `docs/DEVELOPMENT.md` | Historischen Z-Teststand erhalten; neuen M-Basisbuild und neue Startbefehle getrennt ergänzen. Frühere Z-Tests sind keine M-Tests. |
| `docs/inventory/registrations.json`, `tools/inventory_original.py`, `tools/test_inventory_original.py` | Unverändert weiterverwenden und später um weitere Inventurarten erweitern. Vorhandener Export und zwölf Tests sind weiterhin nutzbar. |
| Drei Java-Dateien unter `src/main/java/com/hbm/` | Für die Einstieg-/Clientintegration verwenden. Bis dahin im getrennten Foundation-Build erhalten; keine doppelte Kompilierung oder doppelte Registrierung. |
| Root-ForgeGradle-/Gradle-8.8-Dateien und CI | Als nachvollziehbaren Foundation-Build behalten. Aktiven Modernized-Build zunächst getrennt betreiben; CI gezielt um dessen Befehle ergänzen. Keine zwei Wrapper-/Pluginversionen unkontrolliert im selben Build mischen. |
| `LICENSE`, `LICENSE.LESSER`, `third_party_licenses/`, eigene SPDX-Header | Herkunft erhalten; bei Codeübernahme GPLv3-Gesamtkennzeichnung und zusätzliche Drittanbieterhinweise ergänzen. Alte Einzelvermerke nicht durch neue Autorennamen ersetzen. |

## 3. Gestufte Umsetzung mit überprüfbaren Ergebnissen

Die Reihenfolge richtet sich nach Abhängigkeiten. M0 und M1 sind Voraussetzung des Imports; M2/M3 können danach eng aufeinander folgen. Die Bezeichnungen sind Migrationsarbeitspakete, keine behaupteten Fertigstellungsstufen der alten Feature-Matrix.

### M0 – Herkunft, Lizenzkonzept und Ausgangsarchiv

**Nächster kleiner PR vor einem öffentlichen Quellimport:**

- Provenienztabelle für Code, benötigte Assets und eingebettete Bibliotheken anlegen. Mindestfelder: Herkunftsrepository, vollständiger Commit, Originalpfad, Blob-/SHA256-Hash, Urheber/Notice, konkrete Lizenzbasis, Zielpfad, Änderungen mit Datum, Matrix-ID und Rechteprüfstatus.
- Besonders Modell-/Audioherkunft, fremde API-/Modellheader und Modernized-Dateien mit Originalautorenvermerk prüfen. Unklare Bestände als offen führen und beim späteren Import ausschließen oder durch nachweisbar zulässige Ressourcen ersetzen. Benötigte unklare Assets sind ein konkreter Blocker des betroffenen Imports, keine fingierte Freigabe.
- GPLv3-Konzept für das abgeleitete Gesamtwerk dokumentieren. Für jedes ausgelieferte Fremdartefakt Lizenz/Notices tatsächlich aus dem fixierten Artefakt bzw. dessen Quelle erfassen; die Lizenzen von Architectury, MixinConstraints oder Grafikmods nicht aus dem Namen erraten.
- Mod-/Downloadbeschreibung, Credits und vollständige Quellbereitstellung vorbereiten. `mod_license=LGPL-3.0-only` darf nicht unverändert eine Modernized-GPL-Gesamtdistribution beschreiben. LGPL-Herkunftstexte behalten; keine pauschale Umlizenzierung aller Altdateien behaupten.
- Z/O/M-Pins, aktuelle Branchbeziehung und zulässige Übernahmepfade festhalten. Upstream wird vorerst nur in separaten Analysecheckouts gelesen; keine ungeprüften Fremdassets in den öffentlichen Zielbranch kopieren.

**Abnahme:** Für jeden geplanten Importpfad gibt es eine begründete Rechtebasis und die notwendigen Vermerke. Unklare Fälle sind ausgeschlossen oder vor dem betroffenen Import geklärt. Falls ein benötigter Bestandteil nicht GPL-kompatibel übernommen werden darf, diesen Bestandteil ersetzen oder den Umfang des Basisimports überarbeiten; die gesamte Originalfamilie bleibt trotzdem im Zielumfang offen.

### M1 – Reproduzierbaren Forge-Basisbuild herstellen

Zunächst in einem separaten Modernized-Checkout exakt am M-Pin arbeiten; Änderungen an der Buildkonfiguration als kleine dokumentierte Patches führen. Keine Spielmechanik gleichzeitig ändern.

1. Den in der [Bestandsaufnahme, §6](MODERNIZED_COMPARISON.md#6-durchgeführte-prüfungen-und-reproduktion) belegten JDK-21-Daemon-/Downloadblocker beheben: JDK-Erkennung/Provisionierung, Daemonkriterien und Proxy-/CA-Konfiguration getrennt prüfen. Das bisherige Scheitern vor der Kompilierung ist kein grüner Build und auch kein belegter Quellcode-Kompilierfehler.
2. Absolute Entwicklerpfade entfernen bzw. durch portable Toolchainvorgaben ersetzen. JDK21 für den Build und JDK17 für den Runtime-Test gezielt bereitstellen. Gradle-Wrapper und direkte Pluginversionen pinnen, Distribution/Wrapper per Prüfsummen prüfen und aufgelöste Abhängigkeiten dokumentieren.
3. Nur `1.20.1-forge` als Integrationsziel aktivieren, Loaderpräprozessor und Access Transformer erhalten. Das aktive M-Settingsfile aktiviert derzeit auch NeoForge; ein unqualifiziertes `build` ist deshalb kein ausreichender Forge-Nachweis.
4. Reihenfolge explizit testen: `:1.20.1-forge:runData`, danach `:1.20.1-forge:build` und `:1.20.1-forge:sourcesJar`. Ein zweiter Datagenlauf darf ohne Quelländerung keine unerklärten Ressourcendifferenzen erzeugen. Generierte Ausgabe und Handdateien getrennt inventarisieren; Registryverweise/Serializer/Modelle validieren.
5. Eine minimale Client- und Dedicated-Server-Runtime ohne Entwicklungsclientmods herstellen. Entwicklungs-`modRuntimeOnly`-Hilfen von Nutzervoraussetzungen trennen. Reobfuskiertes Forge-JAR, Jar-in-Jar-Metadaten, Lizenzbeilage und Sourcepaket kontrollieren.
6. Neue CI mit JDK21-Build und JDK17-Artefakttest vorbereiten; keine Quell-/Minecraft-Entwicklungsbestände pauschal öffentlich als Buildartefakt hochladen. Keine Upstream-Publishjobs/Projekt-IDs/Accounts ungeprüft aktivieren.

**Abnahme:** Sauberer Checkout auf Linux, dokumentierte Befehle und aufgelöste Versionen, erfolgreicher Build/Datagen, Java-17-kompatibles Artefakt, Dedicated-Server-Start sowie Client-Hauptmenü und Testwelt. Windowspfade sind entfernt; ein Windows-Build wird separat gemessen und nicht aus Linux abgeleitet. Die Prüfungen erfolgen unter noch unverändertem `hbm_m`, ohne Paritäts- oder Spielstandzusage.

### M2 – Kontrollierter Basisimport und Foundation-Anbindung

Erst nach M0/M1 einen **eigenen Implementierungs-PR** von einem festgehaltenen Ziel-SHA eröffnen. Falls PR #1 zwischenzeitlich gemergt wurde, zuerst seinen resultierenden Commit als neue Zielbasis erfassen. Kein Force-Push auf vorhandene Entwicklungsbranches.

**Konkreter anfänglicher Ablageplan:** Den freigegebenen Modernized-Code samt Build/Generatoren in ein separates Verzeichnis `modernized/` des Zielprojekts übernehmen. Dadurch bleiben Root-ForgeGradle-Build, Dokumente, Werkzeuge und die drei vorhandenen Java-Dateien erhalten. Der neue eigenständige Build verwendet `modernized/settings.gradle.kts` und seinen eigenen Wrapper; er wird anfangs explizit gestartet:

```bash
# Künftige Integrationsbefehle nach dem Import; in diesem PR existiert modernized/ nicht.
./modernized/gradlew -p modernized :1.20.1-forge:runData
./modernized/gradlew -p modernized :1.20.1-forge:build :1.20.1-forge:sourcesJar
```

Der Root-Build bleibt bis zur dokumentierten Umschaltung der bisherige Foundation-Build. README/CI müssen klar zwischen beiden unterscheiden, damit niemand die leere Root-JAR für das Portartefakt hält. Keine automatische Rekursion in beide Builds und kein Mischen von Gradle 8.8 und 9.3.1 in einer Prozessinstanz.

Ein Importmanifest ordnet jede Kopie dem M-Pin zu; ausgelassene Pfade und notwendige Ersatzressourcen werden mit Grund erfasst. Die Erstübernahme und eigene Anpassungen in getrennten Commits halten. Ein späteres Vendor-Update wird als eigener Upstream-Diff behandelt; eine neue tar-Datei ohne Herkunft ist kein Ersatz für diese Zuordnung.

Danach die Foundation-Anbindung in einem isolierten Commit herstellen: Die Forge-Variante nimmt die ausgewählten vorhandenen `com/hbm`-Quellen explizit in ihren SourceSet auf; die Dateien bleiben an ihrem bisherigen Pfad. `HbmPort` erhält den einen Initialisierungspfad, Modernizeds zweite `@Mod`-Annotation wird deaktiviert, und die Clientanbindung bekommt genau eine Zuständigkeit. Die leeren Foundation-Register dürfen nicht unabhängig Modernized-Inhalte nachregistrieren. Während der Namensraumumstellung in M3 keinen gemischten Build veröffentlichen.

**Abnahme:** Bestehende Projektdateien weiterhin vorhanden, nur klar definierte SourceSets aktiv, ein Modcontainer, eindeutige Build-/Runbefehle, alle Importpfade und Änderungen nachvollziehbar. Bisherige Inventurtests bleiben grün. M1-Prüfungen wiederholen sich, weil sich der kompilierte Quellbestand geändert hat.

### M3 – `hbm`-Identität und echte Datenverträge

Vor der ersten unterstützten Portwelt einen atomaren Integrationsschritt durchführen:

- Registrierungen pro **Registry-Art + ResourceLocation** exportieren. Für jedes Objekt O-Name/Metadaten/NBT, M-ID, Ziel-ID, Zielzustand und tatsächliche Erreichbarkeit zuordnen. Alte Java-Feldnamen oder `tile.`-/`item.`-Schlüssel nicht ungeprüft als gültige moderne IDs übernehmen.
- `hbm_m` → `hbm` für Modcontainer, Register, Assets, Datenpacks, Modelle/Texturen, Übersetzungsreferenzen, Loot/Rezepte/Tags, Sound-/Damage-/Biome-Keys und Paketkennungen erfassen. Harte Eventsubscriber-Mod-IDs, Mixinkonfiguration, SavedData-/NBT-Schlüssel und Konfigurationspfade separat prüfen. Nicht jeder String und Java-Paketname muss umbenannt werden; jede Ausnahme benötigt einen Grund.
- Keine zweite unversionierte Aliasregistry für `hbm_m` anlegen. Falls spätere Portversionen IDs ändern, ein eigenes Mapping-/Migrationskonzept samt unterstützten Versionspaaren vorsehen. O-Welten bleiben außerhalb dieser Zusage.
- Für jeden persistenten Typ Einheiten, Wertebereiche, Schema/Defaults, Save/Load und Invalidierung dokumentieren. Modernized-NBT nicht allein aufgrund ähnlicher Namen als originalkompatibel deklarieren.
- Paketliste mit Richtung, maximaler Größe, zuständigem Thread, Menü-/Welt-/Spielerbezug und Versionsregeln erfassen. Den belegten RBMK-Decoder-/Berechtigungsbefund vor einer Mehrspielerfreigabe beheben. Architectury als Transport ersetzt diese Prüfungen nicht.
- Energienetzticks auf eine belegte Zuständigkeit je Dimension reduzieren, Originalraten für RF-Konverter als Referenz erhalten und die konkrete FE-Abbildung spezifizieren. `LongEnergyWrapper`-Grenzfälle und Capability-Lebensdauer korrigieren, bevor diese Pfade als Basis gelten.

**Abnahme:** Vollständig aufgelöste Ressourcen, keine doppelte Registrierung, kohärente ID-/NBT-/Paketverträge, funktionierender Spielstand-Roundtrip einer unterstützten **Portwelt**, zwei verbundene Testclients und korrekte Tick-/Mengenbilanzen. M0-Vermerke und GPLv3-Gesamtkennzeichnung passen zur tatsächlichen Distribution.

### M4 – Erster vollständiger Originalprozess statt weiterer Platzhalter

Mit einer kleinen originalen Frühspielkette beginnen: Erze/Materialformen → Schmelzen bzw. Hochofen → Presse/Stempel → Holzverbrenner/Kabel/Batterie → Montage mit Vorlagen. Dazu die relevanten Rezepte, Tanks/Anschlüsse, Menüs und benötigten Ressourcen aus O einzeln inventarisieren und mit M abgleichen. Kreativbatterien und per Befehl beschaffte Teile sind kein Survivalnachweis.

Jeder Maschinen-PR enthält Originalbeleg, M-Herkunft, Ziel-ID, Eingaben/Ausgaben, Energie-/Tickkosten, NBT-/Automationsfälle und verbleibende Abweichungen. Unvollständige Zutatenketten oder generische Maschinenblöcke bleiben offen, auch wenn die Darstellung bereits funktioniert.

**Abnahme:** Die konkrete Kette ist auf einem frischen Survival-Teststand ohne Hilfsgegenstände erreichbar; gemessene Ergebnisse stimmen mit den dokumentierten O-Fällen überein. Nur die getesteten Einzelinhalte erhalten den entsprechenden Status. Die übergeordneten Familien gelten erst mit vollständig abgearbeitetem Bestand als verifiziert.

### M5 – Vorhandene anspruchsvolle Systeme vervollständigen

Danach nach Nutzbarkeit und Abhängigkeiten bündeln:

| Reihenfolge | Wiederverwendung | Arbeit gegenüber dem Original |
| --- | --- | --- |
| Umwelt/Schutz | Simple-Strahlung, Spieler-/Itemgefahren, Hazmat, Messgeräte, Fallout | Originalwerte/Schutz-/Dosisfälle, Lebenszyklen, Verschmutzungsfolgen; PRISM gesondert implementieren, solange es nur auskommentiert vorliegt. |
| Stoffkreisläufe | Tanks/Fluidnetze, Chemieanlage, Raffinerie, Zentrifugen, Zyklotron | Fehlende Stoffe/Rezepte/Varianten; Fabrik, Deuteriumtower, SILEX und andere Gerüste mit Originalprozessen füllen. |
| ZIRNOX und RBMK | Vorhandene Simulation, Konsole, Neutronen-/Fluidpfade | Brennstoff-/Wärme-/Druckkurven, Regelung, Unfälle, Corium/Debris, Anzeigen und Reloadfälle abnehmen. |
| Explosionen/Raketen/Radar | Vorhandene Entity-/Tick-/Chunkloading- und Effektpfade | Originalalgorithmen, Fuses/Nutzlasten, Block-/Entityschaden, Abwehr und Serverlast prüfen. Originalgrenzen bei Save/Restart ausdrücklich dokumentieren. |
| Ausrüstung/Client | Rüstungs-/Werkzeug-, Modell-, Sound-/GUI-Infrastruktur | Originalfilter, Fähigkeiten, Animationstiming, Sounds und Originalrezepte abgleichen; zusätzliche Modernized-Mechaniken nicht ungeprüft zur Portbalance machen. |

ZIRNOX/RBMK nicht als „Kerntechnik fertig“ zusammenfassen. Tests einer Familie decken Watz, PWR, Piles, Fusion und ICF nicht ab.

### M6 – Fehlende Originalfamilien auf der gemeinsamen Basis portieren

Der Fehlbestand bleibt verbindlich: unter anderem Forschungs-/Brut-/Pile-/PWR-/Watzprozesse, Torusfusion/ICF/DFC, weitere Industrie-/Chemieketten, vollständige Logistik, Sedna-Waffen, Satellitentypen, Mobs/Bosse, Fahrzeuge, Dungeons, Guide/Bobmazon und alte Integrationen. Der genaue Einzelbestand folgt aus der Inventur; die Liste ist keine Scopekürzung.

Originalcode unter seinen Bedingungen übernehmen bzw. technisch portieren, nachdem benötigte Schnittstellen stabilisiert und Rechtefragen geklärt sind. Vorhandene Modernized-Helfer bevorzugen; keinen zweiten HE-/Fluid-/Renderer-Unterbau für jede neue Familie entwickeln. Ein fehlender 1.20.1-Integrationspartner bleibt als offene oder ausdrücklich beschlossene Abweichung dokumentiert und wird nicht durch Create als „erledigt“ ersetzt.

### M7 – Laufender Upstream-Abgleich und Veröffentlichung

M-Updates anhand des zuletzt übernommenen SHAs prüfen: Build, Lizenz-/Assetänderungen, IDs/NBT/Pakete und Balance getrennt bewerten. Lokale Portkorrekturen mit Originalbelegen als kleine Patches halten, um spätere Konflikte einzugrenzen. Keine automatische Übernahme der neuesten Branchspitze in einen Releasebuild.

Releaseakte: Ziel-/M-/O-Commits, Konfiguration und Testprotokolle, Build-/JAR-Hashes, vollständiger zugehöriger Sourcebestand, Lizenz-/Noticepaket, Abweichungen und unterstützte Port-Spielstandversionen. Releasebezeichnungen müssen den geprüften Umfang widerspiegeln; „Complete“ im Projektnamen ist kein Beleg der Vollständigkeit.

## 4. Erforderliche Tests und Abnahmen

**Die folgende Tabelle ist ein Testplan; diese Prüfungen sind für Modernized noch nicht als bestanden dokumentiert.** Der tatsächlich ausgeführte Stand dieses PRs steht im [Vergleich, §6](MODERNIZED_COMPARISON.md#6-durchgeführte-prüfungen-und-reproduktion).

Jeder Originalvergleich protokolliert O- und Zielcommit, verwendete Abhängigkeiten, Konfiguration, Aufbau/Koordinaten, Inputs, Seed soweit relevant, Serverticks und erwartete/gemessene Zustände. Exakte Integer-/Inventar-/NBT-Ergebnisse sollen exakt verglichen werden; Floattoleranzen und stochastische Verteilungen benötigen eine begründete, vorher festgelegte Auswertung. Unterschiedliche Minecraft-Weltgeneratoren werden nicht durch eine unbegründete Zusage identischer Welten verglichen.

| Test-ID | Fall und prüfbares Ergebnis | Spätestens vor |
| --- | --- | --- |
| T01 Build/Datagen | Sauberer Forge-Checkout erzeugt JAR und Quellen; wiederholter Datagenlauf erklärt jede Differenz; keine fehlenden Serializer, Modelle, Tags, Loot-/Rezeptverweise. | M1/M2 |
| T02 Laufzeit/Packaging | Kern-JAR auf JDK17, Forge 47.4.20, ohne Client-/Profilermods; Dedicated Server startet, Client erreicht Testwelt. Eigene Klassen und eingebettete Bibliotheken laufen auf JDK17; keine Minecraft-/Forge-Entwicklungsdateien in Mod-/Sourcepaketen. | M1/M2 |
| T03 Registry/Identität | Export pro Registry vollständig auflösbar; genau ein `hbm`-Modcontainer, keine unbeabsichtigten `hbm_m`-Ressourcen-/Paketreferenzen, keine stille Überschreibung. | M3 |
| T04 Speicherung | NBT-Roundtrip, fehlende/falsche Felder, zukünftige Schemata, Abbau/Platzierung, Chunkentladung, Serverneustart, Spielerrespawn/Dimensionswechsel; kein stiller Verlust oder Duplikation. | M3, dann je Typ |
| T05 HE/FE | `0`, `Integer.MAX_VALUE`, `2^31`, `2^32` und zulässige hohe `long`-Werte; Simulationsaufrufe verändern nichts; keine negativen FE-Anzeigen, Überläufe oder verlustlosen Konverterkreise durch falsche Raten. Originalraten **5 HE → 1 RF**, **2 RF → 5 HE**, Verluste und Rundung getrennt prüfen; FE-Abbildung ausdrücklich festlegen. | M3 |
| T06 Tick/Netze | Instrumentierung in Overworld und weiterer Dimension: vereinbarte Tickfrequenz genau einmal; Netze bei Ring, Teilung, Zusammenführung, geladenen/entladenen Nachbarn und mehreren Serverstarts korrekt. | M3 |
| T07 Fluids | Druckstufen 0–5, ungleiche Drücke, Prioritäten, gemischte Medien, volle/leere Tanks, Ventile/Pumpen/Abgas, Druck-/Stoffwechsel, Simulations-/Teiltransfer und druckloser Forge-Adapter; Originalstoffbilanz bleibt erhalten. | M3, dann je Maschine |
| T08 Multiblocks | Alle unterstützten Orientierungen, blockierte Platzierung, Abbau von Teil/Controller, Anschlussseiten und Teilentladung; keine Itemduplikation oder verwaisten Teile. | M4 |
| T09 Prozess/Survival | Pro Originalrezept Stoffmengen, Zeit, HE, Nebenprodukte, Chance und Upgrade-/Slotregeln; volle Ausgänge, fehlende Inputs und Neustart; konkrete frühe Produktionskette ohne Kreativhilfen. | M4 |
| T10 Netzwerk/Autorität | Zwei Clients am Dedicated Server; falsches Menü/Dimension/Reichweite, fremde Maschine, unbekannte Aktion, ungültige Zahl und negative/überlange Sammlungen werden vor Verarbeitung abgewiesen. RBMK-Paketgrenzen vor Speicherallokation prüfen; Client darf keinen fertigen Serverzustand bestimmen. | M3 vor Multiplayer |
| T11 Strahlung/Schutz | O-Simple als Default und O-PRISM separat; Chunkdosis/Abklingen, Inventargefahr, Filter/Hazmat, Tod/Respawn, Biome/Fallout und Decon mit gleichen fachlichen Inputs vergleichen. Ein Simple-Erfolg nimmt PRISM nicht ab. | M5 |
| T12 Reaktoren | Jede Familie einzeln: Brennstoff/Neutronen/Hitze, Wasser/Kühlung/Druck, Redstone/Konsole, Leistungs-/Stoffbilanzen, Grenzfälle und Unfallfolgen. Watz/Breeder/Core-Gerüste müssen zunächst überhaupt einen Fachprozess erhalten. | M5/M6 je Familie |
| T13 Explosionen/Raketen | Originalschaden/-reichweite/-Fallout/-Zünder, Chunkgrenzen, Tracking, Abwehr, Budgetierung und Entladen/Restart; definierte Originalgrenzen beachten. Keine vollständige MK5-Neustartfähigkeit als Originalfunktion erfinden. | M5 |
| T14 Weltgen/Population | Mehrere dokumentierte Seeds/Dimensionen: Erzhöhen/-häufigkeit, Ressourcenverfügbarkeit, Strukturbedingungen, Loot, Mobs/Spawns. Neue Chunkgenerierung und bestehende Portwelten getrennt testen. | Je Weltgen-PR |
| T15 Darstellung/Bedienung | Modelle/Animationen/GUI/HUD, Tastenumlegung, Sprachschlüssel, Soundloops/-stopps und Resource-Reload; visuelle Referenzen mit O. Clientvarianten ohne/mit optionalen Render-/Create-Mods getrennt. | Je Client-PR |
| T16 Fremdmodgrenzen | Kernstart ohne JEI/Create/Flywheel; mit unterstützten Versionen Rezeptanzeige und Create-Pfade prüfen. Alte AE2-/OC-/Microblock-Verträge erst nach eigener Umsetzung abnehmen. | M2/M5/M6 |
| T17 Last/Stabilität | Dokumentierte Hardware, Forge/Java/Configs, Netz-/Maschinen-/Explosionstestwelten; TPS/MSPT, Spitzen, Speicher, Paketmengen und Langzeit-/Reloadverhalten messen. „512 Rohre <1 ms“ aus offener Upstreamliste ist ein Ziel, kein Messergebnis. | Vor jeweiliger Freigabe |
| T18 Herkunft/Release | Jede ausgelieferte Datei/Einbettung mit Lizenzbasis und Vermerken, passende Commit-/Hashzuordnung und vollständiger Sourcezugang; ungeklärte Assets fehlen in der Distribution. | M0/M2 und jeder Release |

Zuerst die systemübergreifenden Verträge prüfen, dann risikogerechte Prozess-/Originaltests pro übernommener Familie. Nicht für jede bloße Datei-/Namensänderung einen Implementierungsdetails spiegelnden Test schreiben. Bestehende Inventurtests schützen die Herkunftsarbeit; sie ersetzen keine dieser Spieltests.

## 5. Fortführung der Bestandsaufnahme

Für jeden tatsächlich erreichbaren Einzelinhalt künftig mindestens folgende Angaben führen:

| Feld | Zweck |
| --- | --- |
| Original-ID, Varianten und Quelle | O-Commit, Registrierungspfad, Metadaten/NBT und fachlicher Referenzfall |
| Modernized-Zuordnung | M-Commit, Quellpfad, ID und Befund S/T/N/U aus dem Vergleich |
| Ziel und Abhängigkeiten | Zielregistry/-ID, SourceSet, Ressourcen, Rezepte, Daten-/Netzverträge und benötigte Matrix-IDs |
| Rechte/Herkunft | Code-/Asset-/Bibliothekslizenz, Urheber, Vermerke und dokumentierte Änderungen |
| Implementierung/Abnahme | PR, Test-ID/Protokoll, gemessene Ergebnisse, offene Abweichungen und Status |

Ein registrierter generischer Block erhält beispielsweise „Platzhalter“ im Modernized-Befund und weiterhin einen offenen Originalportstatus. Eine auskommentierte PRISM-Klasse erhält keinen Implementierungsnachweis. Eine funktionierende M-Maschine ohne Originaltest kann als untersuchter Teilbestand gelten, nicht als originalgetreu verifiziert.

Es gibt derzeit weder einen seriös belegten Fertigstellungsprozentsatz noch eine belastbare Gesamtlaufzeit. Der nächste Fortschrittsmaßstab ist ein reproduzierbarer, lizenzseitig dokumentierter Forge-Basisbuild und danach eine vollständig geprüfte frühe Produktionskette. Erst diese Ergebnisse erlauben eine sinnvollere Aufwandsschätzung für die verbleibenden 140 Funktionsfamilien.
