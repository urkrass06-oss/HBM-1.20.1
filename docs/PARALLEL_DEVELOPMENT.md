# Vier Entwicklungsaufträge für HBM Complete Port

Stand: **20.10.2026 (UTC)**. Geprüfter `main`: **`ff1eef39e870b9e4322d7a2d8b30f6bb3a517044`** (PR #6 eingeschlossen). Dieser Dokumentationsauftrag startet keine parallelen Implementierungen und erzeugt noch keine vier Entwicklungsbranches. Die folgenden Zuständigkeiten und Startbedingungen sind die Übergabe für diese Aufträge.

## 1. Verbindliche Basis und Ziel

| Bestand | Pin / Bedeutung |
| --- | --- |
| Original O | `HbmMods/Hbm-s-Nuclear-Tech-GIT@aee05a40f10fb7bb9b042b65eccaa449ecc1672d`, Minecraft 1.7.10 / Forge 10.13.4.1614; fachliche Referenz |
| Modernized M | `Raptor324/HBM-Modernized@0365cef5956016913095eeeb9366f26c601ca9a0`; nur Variante `1.20.1-forge` |
| Aktive Basis I | M + `forge-1.20.1.patch` + `phase4-integration.patch` + `phase5-multiplayer.patch` + Foundation-/GameTest-Overlay, erzeugt durch `tools/integrate_modernized.py … --phase5` |
| Gemeinsames Ziel | Minecraft **1.20.1**, Forge **47.4.23**, Mod-/Minecraft-JDK **17**, Build-JDK **21**, Gradle **9.3.1**, Namespace vorerst **`hbm_m`** |
| Bisheriger Build-Pin | **47.4.20**; 47.4.23 ist bereits als Runtime und GameTest-Ziel geprüft. Ein neuer Produktionsbuild gegen 47.4.23 ist ein zusätzliches Gate, kein bereits ausgeführter Nachweis. |
| Historisches Rootprojekt | Forge 47.4.10 / Gradle 8.8, drei Foundation-Klassen. Dessen JAR enthält keine Modernized-Spielinhalte. |

Gelesen: [Vergleich](MODERNIZED_COMPARISON.md), [Migration](MODERNIZED_MIGRATION.md), [Phase-3-Buildbericht](MODERNIZED_BUILD_REPORT.md), [Integration](INTEGRATION_REPORT.md), [Buildstatus](BUILD_STATUS.md), [Forge-/Mehrspielerbericht](FORGE_MULTIPLAYER_REPORT.md), [offene Punkte](REMAINING_ISSUES.md), [Importcheckliste](MODERNIZED_IMPORT_CHECKLIST.md), [Datenverträge](DATA_CONTRACTS.md) und [Originalmatrix](FEATURE_MATRIX.md). Historische Aussagen dieser Berichte beziehen sich auf ihre jeweiligen SHAs. Für den aktuellen Prüfstand hat Phase 5 Vorrang; die Originalmatrix bleibt der Umfangskatalog.

[FEATURE_GAPS.md](FEATURE_GAPS.md) ordnet alle 140 bestehenden Familien zu und unterscheidet fehlenden Fachprozess, vorhandenen Teilbestand und fehlenden Testnachweis. Keine Prozentzahl wird aus Datei- oder Registryzahlen abgeleitet. Laufzeitmessungen gegen O fehlen weiterhin; Originalparität darf daraus nicht behauptet werden.

## 2. Arbeitsbereiche und Schreibzuständigkeiten

**M = Maschinen/Industrie, W = Waffen/Explosionen, N = Reaktoren/Nukleartechnik, R = Rendering/Stabilität.** R übernimmt zusätzlich die serialisierte Integrationspflege. Es gibt vier Entwicklungsaufträge; die Integrationspflege ist eine Rolle innerhalb R, kein fünfter paralleler Auftrag.

Öffentliche neue Lieferpfade sind **vorgeschlagen und existieren an der geprüften Basis noch nicht**:

```text
tools/modernized/parallel/<machines|weapons|nuclear|rendering>/
  area.json                     # Basis, Pfade, Abhängigkeiten, Patch-/Overlayhashes
  changes.patch                 # nur einzeln zur Veröffentlichung geprüfte Deltas
  overlay/                      # neue eigene Produktionsklassen, soweit freigegeben
  gametest/com/hbm/integration/<area>/
  requests/                     # strukturierte Aufträge an den zentralen Schreiber
  rights.json                   # Herkunft/Veröffentlichungsstatus jeder Lieferung
  evidence/                     # geprüfte Textbefunde, keine Assets/JARs/Welten
```

Jeder Bereich ändert nur seinen Lieferpfad und seine `docs/TASKS_*.md`. `docs/FEATURE_GAPS.md`, dieses Dokument und zentrale Infrastruktur bearbeitet ausschließlich R nach Übergabe der Befunde. Auf dem externen M-Arbeitsbaum gelten die folgenden Zuständigkeiten **auf Dateiebene**, unabhängig vom Ablageort des öffentlichen Patches:

| Dateien / Familie relativ zu M | Alleiniger Schreiber | Abgrenzung |
| --- | --- | --- |
| `api/energy/**`, `api/fluids/**`, `inventory/fluid/**`, `blockentity/BaseMachineBlockEntity.java`, `blockentity/OilDrillBaseBlockEntity.java`, gemeinsame `multiblock/**`-Helfer | M | Gemeinsame API-Änderungen zuerst als kleine stabile Lieferung; keine konkurrierende Energie-/Fluidbasis durch N/W |
| Nichtnukleare Prozessmaschinen in `block/machines/`, `blockentity/machines/`, zugehörige `inventory/menu/`, `recipe/`, `inventory/recipes/`, `datagen/recipes/` | M | Ausnahmen N/W unten haben Vorrang. Jeder Task nennt seine konkreten Dateien; kein pauschales Schreibrecht für das ganze Maschinenpaket. |
| `MachineBreeder*`, `MachineZirnox*`, `MachineRbmkConsole*`, `machines/rbmk/**`, `MachineWatzPowerplant*`, `MachineCore*`, nukleare Fuel-/Neutronen-/Strahlungs-/Hazardklassen | N | Einschließlich nuklearer Menüs, `handler/rbmk/**`, `radiation/**`, `hazard/**`; N besitzt CHEM-009–012. Neue PWR/Pile/Fusion/ICF-Dateien vor dem Anlegen exakt in `area.json` reservieren. |
| `explosion/**`, `util/explosions/**`, Bomben-/Granaten-/Missile-/Turret-/Radar-/Soyuzklassen, `satellite/**`, Waffenitems und Munition | W | Einschließlich Waffenmenüs und zugehöriger Logikentities. `EntityFalloutRain` gehört W; Strahlungsablagerung ruft N-API auf. Kein Schreibrecht an gewöhnlichen Mob-/Rüstungsklassen. |
| `client/**`, **alle** `inventory/gui/**`, Modell-/Animationslader, Partikel-/Sounddarstellung, `config/ModConfigKeybindHandler.java` | R | M/N/W liefern Menü-/Datenvertrag und fachliche Darstellungsvorgaben. Nur R bearbeitet Screens/Renderer, auch für neue Maschinen/Waffen. |
| `network/FluidTankModePacket.java`, `FluidIdentifierControlPacket.java`, `UpdateBatteryC2SPacket.java`, `SetAssemblerRecipeC2SPacket.java`, `SetChemPlantRecipeC2SPacket.java`, weitere explizit benannte Prozesspakete | M | Andere Pakete erst nach genauer Reservierung; kein allgemeines Schreibrecht auf `network/**` |
| `network/RBMKConsoleControlPacket.java`, `ZirnoxControlPacket.java`, Strahlungspakete | N | Vorhandene Phase-5-Validierungen erhalten |
| `network/BuildMissilePacket.java`, `DetonateAllPacket.java`, `TurretControlPacket.java`, `UpdateRadarC2SPacket.java`, `SoyuzLauncherControlPacket.java`, `ItemDesignatorPacket.java` und neue Waffenpakete | W | Derselbe Serverautoritätsvertrag wie bei N/M |
| Zentrale Register: `block/ModBlocks.java`, `item/ModItems.java`, `blockentity/ModBlockEntities.java`, `entity/ModEntities.java`, `inventory/menu/ModMenuTypes.java`, `recipe/ModRecipes.java`, `network/ModPacketHandler.java`, `sound/ModSounds.java` | **R** | Nur dieser Schreiber übernimmt geprüfte Registry-/Initialisierungshunks aus `requests/`; M/N/W ändern diese Dateien auch extern nicht. Bestehende IDs bleiben erhalten. |
| `main/**`, Plattformadapter, zentrale Configschemas, `datagen/DataGenerators.java`, gemeinsame Provider, Buildskripte, Mixins/AT, `versions/**`, `tools/*.py`, CI und bestehende Phase-3–5-Patches/-Tests | **R** | M kann Änderungen an gemeinsamem Tickpfad anfordern; R integriert sie seriell. Bestehende Patches nicht von vier Branches fortschreiben. |
| Gemeinsame `lang/*.json`, `sounds.json`, Tags, Damage-/Biome-Register, `assets/**`, `data/**`, `src/generated/resources/**` | **R** | M/N/W liefern genaue Ressourcen-/Rezeptanforderungen; eigene bereichsspezifische Generator-Javaklassen bei jeweiligem Fachbereich. Datagenausgaben nur extern. Jede Assetdatei benötigt Rechtebeleg. |
| Mobs, Weltgen, allgemeine Spielerausrüstung und optionale Integrationen ohne obige Ausnahme | **R zunächst** | In der Restumfangsliste behalten; vor fachlicher Umsetzung einzelne Dateien an genau einen Bereich übergeben. Keine stillschweigende Ausklammerung. |

Alle Java-Pfade der Tabelle beginnen unter `src/main/java/com/hbm_m/`. Ausnahmen für zentrale Dateinamen gehen Familienmustern vor; R-Clientzuständigkeit geht fachlichen Familien vor. Neue oder überlappende Dateien werden **vor der Änderung** mit genau einem Eigentümer reserviert. Bei einem Streit stoppt nur die betroffene Datei, unabhängige Aufgaben laufen weiter.

## 3. Startfreigabe und Schnittstellen

Vor Beginn der vier Implementierungsaufträge: diese Zuständigkeiten am gemeinsamen Basis-SHA übernehmen, pro Bereich ersten Task und Dateiliste eintragen, eigene externe Checkouts anlegen und die gemeinsame Basis reproduzieren. Kein Auftrag erhält pauschal die Aufgabe „alles portieren“. Erste Lieferungen: **M-01**, **W-01**, **N-01**, **R-01/R-02** aus den vier Aufgabenlisten. Danach die dortigen Abhängigkeiten einhalten.

`area.json` muss mindestens enthalten: `target_base` (vollständiger gemeinsamer main-SHA), O/M-Pins, Hashes der drei Basispatches und Basisoverlays, Bereich, Task-/Feature-IDs, exakte geänderte/neu angelegte externe Dateien, `requires` mit konkretem Liefercommit und API-Version, Patch-/Overlay-/Testdateihashes, erforderliche Registrierungen und Rechte-/Testbeleg. Der Rechtsstatus ist pro Datei zu führen; ein Bereichsflag ersetzt ihn nicht. Abhängigkeiten bilden einen gerichteten Graphen; Kreisabhängigkeiten vor Integration in kleinere Lieferungen zerlegen.

| Vertrag | Verantwortung und verbindliche Regeln |
| --- | --- |
| Register | `(Registry-Art, hbm_m:ID)` ist die Identität. Registry-Request nennt alte/neue Klasse, BlockEntity-/Item-/Menü-/Serializerbindung, Initialisierungsort, Ressourcen und Tests. R liefert zugehörigen Integrationscommit. Keine doppelte Registrierung oder Namespaceumstellung in Fachbranches. |
| Prozess, HE und Fluid | M stellt die vorhandenen `BaseMachineBlockEntity`-/HE-/Tank-/FluidNet-APIs bereit. HE-Mengen als `long`, Tank-/Netzweiten gemäß konkreter Implementierung; Simulation ohne Mutation, keine doppelten Transfers pro Leveltick. Fluidtyp und Druck 0–5 getrennt erhalten. HIGH-Semantik nicht in normale FE umdeuten. RF-Originalraten sind kein Beweis HE=FE. |
| Menüs und Anzeige | Fachbereich besitzt Slot-/Button-/NBT-/S2C-Vertrag; R besitzt Screen und Renderer. Übergabe enthält Feldname, Typ, Einheit, Bereich, Initialzustand/Update, Slotfilter und berechtigte Aktionen. NBT-Speicherdaten nicht pauschal als Client-Schreibprotokoll verwenden. |
| Netzwerk | Vorhandenen Architectury-Transport beibehalten; der ältere `SimpleChannel`-Entwurf ist kein Auftrag zum zweiten Netzsystem. C2S: begrenztes Decode, Serverthread, gültiger Absender/Dimension/geladenes Ziel, passendes Menü oder fachlich begründeter Waffenbezug, Distanz/Berechtigung, endliche Werte, ungültig ⇒ keine Mutation. R registriert eindeutige Paket-IDs; Fachbereich implementiert Handler. |
| Nuklearunfall → Explosion | N entscheidet anhand seiner Simulation, ob und mit welchen belegten Parametern ein Unfall ausgelöst wird. W besitzt Explosionsalgorithmus/Arbeitsbudget, Weltänderung und Fallout-Entity. Neue gemeinsame Adapterdatei nur durch R, nach beiden Reviews; bis dahin vorhandene konkrete APIs verwenden, keine erfundene bereits implementierte Schnittstelle. |
| Explosion → Strahlung | W liefert Position, Dimension, Ursache und in O belegte Quellparameter; N besitzt Ablagerung, Dosis, Abschirmung und Zerfall. Ein Unfall darf Quelle/Explosion nur einmal erzeugen. Kein direkter Zugriff von W auf N-interne SavedData. |
| Lebensdauer | Server bestimmt Inventare, Wärme, HE, Fluids, Schaden und Weltänderungen. Capabilities invalidieren, Netzcaches beim Entladen lösen; NBT-Roundtrip und zwei Dimensionen prüfen. Keine Clientklassen aus Serverpfaden laden. |
| Originalmesswerte | Jede Prozesslieferung enthält O-Quellformel, Konfiguration, Input, Tickzahl und erwartete Outputs/Kosten. Ohne lauffähigen O-Test nur „quellgestützt“; „originalverifiziert“ erst mit getrenntem O-JDK8-Lauf. Keine Zahlen als geratenes Balancing einsetzen. |

Zentrale Änderungen sind serialisierte Voraussetzungen, keine verdeckten Nebenarbeiten: Bereich legt einen Request mit exakten Feldern/IDs und Testfall ab; R implementiert nur diesen Request in einem kleinen Commit; Bereich bindet dessen SHA als Abhängigkeit und testet dagegen. R führt eine bestellte Screen-/Registeränderung nicht gleichzeitig mit einem eigenen Umbau derselben Datei aus. Keine parallelen API-Rewrites.

## 4. Arbeiten ohne ungeklärten Vollimport

Die bestehende Entscheidung aus [rights-review.json](integration/rights-review.json) bleibt bestehen: vollständiger M-Code, Assets, generierte Bestände und Evaluations-JARs bleiben außerhalb des öffentlichen Repositories. **Extern bedeutet keinen zusätzlichen Rechtsanspruch**; nur rechtmäßig zugängliche Quellen lokal untersuchen/ändern und nur in einem rechtlich zulässigen Kreis teilen. Ein privater Branch, ein Patch oder ein Generator klärt ungeklärte Rechte nicht automatisch.

1. Jeder Auftrag verwendet einen eigenen externen M-Checkout und unveränderte O-Referenz. Vollbäume werden weder unter `modernized/` vendort noch als öffentliche Worktrees/Submodule, Git-LFS-Dateien, Actions-Artefakte oder Releases hochgeladen. Öffentliche Worktrees enthalten nur das kleine Zielrepository.
2. Neue eigene Tests, Werkzeuge und unabhängig geschriebene Implementierungen können nach Herkunftsprüfung als kleine Quelldateien geliefert werden. „Neu geschrieben“ bedeutet bei einer tatsächlichen Bearbeitung fremden Codes keine unabhängige Herkunft. Modernized-Derivate benötigen GPLv3-konforme Behandlung; vorhandene LGPL-/Copyrightvermerke bleiben erhalten.
3. Jeder veröffentlichte Patch wird einschließlich Kontextzeilen gegen die [Importakte](MODERNIZED_IMPORT_CHECKLIST.md#2-importakte-je-datei-oder-belegbar-homogener-gruppe) geprüft: Quellcommit, Blob/SHA256, Ursprungskette, Rechteinhaber, Lizenz/Erlaubnis, Notices, Änderung und Zielpfad. Bestehende kleine Patches sind keine pauschale Freigabe für weitere Dateien. Ist die Grundlage offen, bleiben Delta und betroffene Dateien extern; öffentlich nur nichtkopierende Befunde, Schnittstellen und zulässige eigene Tests. Ein davon abhängiger öffentlicher Feature-PR bleibt blockiert, bis die benötigten Rechte belegt oder zulässige Ersatzimplementierungen verfügbar sind.
4. Assets erhalten eine eigene Prüfung, auch Übersetzungen, Strukturen, Modelle, Animationen und Generatorinputs. Eigene Ersatzassets mit dokumentierter Urheberschaft oder ausdrücklich geeigneter Lizenz verwenden; keine ungeprüfte Kopie aus O als Ersatz. Korrekturen an Modellreferenzen dürfen öffentlich ohne Assetbytes beschrieben werden, soweit auch ihr Code-/Patchinhalt geprüft ist.
5. Öffentliche CI lädt die fixierte Basis nur temporär und erzeugt keine Quell-/Asset-/JAR-/Screenshot-/Weltuploads. Logs auf kopierte Quell-/Assetinhalte und Geheimnisse prüfen. Release bleibt gesperrt, bis Corresponding Source, aktive Buildlogik/Generatorinputs, Bibliotheksnotices und alle tatsächlich verteilten Dateien zulässig und vollständig zugeordnet sind.

Diese Vorgehensweise ermöglicht bereits konkrete Implementierungen und lokale Tests. Sie behauptet keine abgeschlossene Rechteklärung und ersetzt keine Entscheidung über einzelne ungeklärte Rechte.

## 5. Gemeinsame Prüfungen auf Forge 47.4.23

Alle folgenden Befehle laufen aus dem Zielcheckout. `HBM_CHECK_ROOT` liegt **außerhalb** sämtlicher öffentlicher Worktrees und ist pro Auftrag/Lauf neu; JDK-Pfade auf vollständige lokale JDKs setzen. Vorher jeweils `git rev-parse HEAD`, O/M-SHAs, Patch-/Overlayhashes und Konfiguration im externen Evidenzmanifest festhalten.

```bash
export HBM_CHECK_ROOT=/absolute/external/hbm-check-unique
export HBM_JAVA21=/absolute/toolchains/jdk-21
export HBM_JAVA17=/absolute/toolchains/jdk-17
python3 tools/integrate_modernized.py "$HBM_CHECK_ROOT/modernized" --phase5
```

**Stand heute:** Der Helfer lädt nur die vorhandene Phase-5-Basis. Er hat noch keinen Bereichsloader. R-01 implementiert und testet diesen. Vorher kann eine freigegebene Bereichslieferung gezielt mit `git -C "$HBM_CHECK_ROOT/modernized" apply --check /absolute/changes.patch`, danach `apply` und Kopieren ihrer explizit gelisteten eigenen Overlay-/Testdateien eingespielt werden. Keine unkontrollierten `cp -r`-Vollbäume. Neue Dateien nicht in den getrackten M-Pin committen: `modernized_build.py` verlangt `HEAD == M-Pin`. Der erzeugte `integration/provenance.json` beschreibt zunächst nur die Basis; die Bereichshashes müssen bis R-01 zusätzlich separat erfasst werden.

Produktionsprofil explizit gegen **47.4.23** bauen; jeder Aufruf erhält denselben Override. Der reguläre 47.4.20-Pin wird dadurch nicht stillschweigend geändert:

```bash
python3 tools/modernized_build.py run "$HBM_CHECK_ROOT/modernized" runData \
  --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
  --gradle-home "$HBM_CHECK_ROOT/gradle-home" --log-dir "$HBM_CHECK_ROOT/logs" \
  --gradle-arg=-Pdeps.forge=47.4.23
python3 tools/audit_modernized.py resources "$HBM_CHECK_ROOT/modernized/src/generated/resources" \
  --output "$HBM_CHECK_ROOT/datagen.sha256"
python3 tools/modernized_build.py run "$HBM_CHECK_ROOT/modernized" runData \
  --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
  --gradle-home "$HBM_CHECK_ROOT/gradle-home" --log-dir "$HBM_CHECK_ROOT/logs" \
  --gradle-arg=-Pdeps.forge=47.4.23
python3 tools/audit_modernized.py resources "$HBM_CHECK_ROOT/modernized/src/generated/resources" \
  --compare "$HBM_CHECK_ROOT/datagen.sha256"
python3 tools/modernized_build.py run "$HBM_CHECK_ROOT/modernized" build sourcesJar \
  --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
  --gradle-home "$HBM_CHECK_ROOT/gradle-home" --log-dir "$HBM_CHECK_ROOT/logs" \
  --gradle-arg=-Pdeps.forge=47.4.23
export HBM_CHECK_JAR="$HBM_CHECK_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase5-dev+1.20.1-forge.jar"
python3 tools/audit_modernized.py jar "$HBM_CHECK_JAR" \
  --generated-source "$HBM_CHECK_ROOT/modernized/src/generated/resources"
sha256sum "$HBM_CHECK_JAR"
python3 tools/test_modernized_server.py "$HBM_CHECK_JAR" "$HBM_CHECK_ROOT/server-47.4.23" \
  --forge 47.4.23 --java17-home "$HBM_JAVA17" --accept-eula
python3 tools/modernized_build.py run "$HBM_CHECK_ROOT/modernized" runGameTestServer \
  --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
  --gradle-home "$HBM_CHECK_ROOT/gradle-home" --log-dir "$HBM_CHECK_ROOT/logs" \
  --gradle-arg=-Pmodernized.gameTests=true --gradle-arg=-Pdeps.forge=47.4.23
```

Der JAR-Name gilt für die unveränderte Phase-5-Version. Nach einer Versionsänderung den tatsächlich gebauten Dateinamen im Manifest aktualisieren; kein beliebiges `*.jar` auswählen. Testprofil erst nach Audit/Hash der Produktions-JAR starten, um Test-JARs nicht mit dieser zu verwechseln. EULA nur nach Lesen/Annahme durch den Betreiber; das Beispiel ist für entsprechend autorisierte isolierte Tests. In der Cloud gegebenenfalls `--trust-store /etc/ssl/certs/java/cacerts` verwenden, Proxy/TLS beibehalten. `--allow-offline-auth-failure` nur bei dem exakt dokumentierten Offline-Loopback-Fall aus Phase 5; keine anderen Logfehler ausblenden.

| Gate | Für jeden Feature-PR und erneut für den Integrationsstand |
| --- | --- |
| G1 Herkunft/Scope | Allowlist eingehalten, keine ungeprüften Dateien veröffentlicht, alle Änderungen einschließlich neuer externer Dateien erfasst; Basispins/Abhängigkeiten stimmen. |
| G2 Datagen/Build/Paket | Zwei identische Datagenläufe; getrenntes `build sourcesJar`; Exit 0; Forge 47.4.23 tatsächlich in Befehlen/Logs; Java-17-/Jar-in-Jar-/Ein-Einstieg-Audit, alle generierten Ressourcen vorhanden, keine Testklassen/-strukturen in Produktion. Kein Registry-/Ressourceneintrag ohne begründeten Ersatz entfernt. Neue Ressourcen ändern das Manifest legitim; der alte Hash ist kein Sollwert für neue Features. |
| G3 GameTests | **Alle 14 vorhandenen Tests** plus die Bereichstests bestehen als required Tests auf 47.4.23; Testzahl/IDs explizit prüfen. `NO-SOURCE`, 0 Tests oder nur Gradle Exit 0 reichen nicht. FakePlayer ersetzt keinen echten Clienttest. |
| G4 Dedicated Server | Produktions-JAR auf Forge 47.4.23 / Java 17; mindestens zwei Starts, jeweils `Done`, 30 s Beobachtung, Save/Stop, Exit 0; unerwartete ERROR/FATAL/Crash fehlen. Relevante NBT-/Inventarwerte nach Neustart abfragen. |
| G5 Zwei Clients | Beide Produktionsclients gleichzeitig mit exakt dem Server-JAR-Hash auf 47.4.23; gemeinsame Bedienung, Anzeigen und Aktionen prüfen, beide Logs und Serverzustand abgleichen; mindestens 10 Minuten gemeinsame Verbindung pro Lieferung. Fehlgeschlagene Schritte erhalten, nach Fix gezielt wiederholen. |
| G6 Lebensdauer | Ohne Force-Loading Arena normal entladen/laden, neu verbinden und Dimension wechseln; Werte und Capabilities prüfen. Save/Restart und Singleplayer-Weltkopie zusätzlich. Phase-5-Forcechunks beweisen dieses Gate noch nicht. |
| G7 Originalvergleich | Relevante O-Registrierungen/Varianten, Rezepte, Einheiten, Tickkosten und Verhalten einzeln messen. Quellgestützte Werte sind vorläufig; keine ganze Familie aufgrund eines bestandenen Rezepts schließen. |
| G8 Integration/Stabilität | Nach vier Lieferungen zusätzlich zwei Stunden gemischter Betrieb mit Maschinen, Reaktor und Waffen, Tickzeiten/Heap/Netzgrößen protokollieren. Definierte Last/Hardware/Seed nennen; keine pauschale TPS-Garantie ableiten. Onlineauthentifizierung und echte Modpackliste gesondert prüfen. |

G5 reproduziert mindestens Batterieinventar in beide Richtungen ohne Duplikation, 20.000.000-HE-Netzbilanz, Tank/Eimer/Moduspaket und 18.000-mB-Bilanz, RBMK-Spalte live hinzufügen/entfernen, Sollwert/Bildschirm/AZ-5 von beiden Clients und eine echte Spielergranate mit Owner/Blockschaden. Danach die Fachszenarien aus jeder Aufgabenliste ergänzen. Renderer/Lifecycle zusätzlich bei Resource-Reload und erneuter Weltverbindung prüfen. Produktionsclient-/Serversitzungsbefehle und Arena: [Phase-5-Reproduktion](FORGE_MULTIPLAYER_REPORT.md#reproduktion), `tools/modernized/multiplayer-fixture.commands`.

Die 14 bestehenden Tests stehen in `tools/modernized/gametest/.../ModernizedIntegrationTests.java` (3) und `tools/modernized/phase5-gametest/.../ModernizedSystemsTests.java` (11). Sie bleiben unverändert verpflichtend. Neue Tests liegen in getrennten Bereichspaketen; keine zweite Klasse mit gleichem FQCN oder kollidierendem Testnamen. Bestehende Regressionen nicht zur Anpassung an einen Fehler abschwächen. Die 66 tolerierten Javadocfehler/100 Warnungen bleiben bekannte offene Arbeit, kein bestandener Javadocnachweis.

## 6. Vier Branches ab demselben aktuellen main-SHA

Für die spätere Ausführung **nach Übernahme dieser Dokumente und vor jeder Implementierung**. Bei inzwischen geändertem main den gesamten Basisunterschied prüfen, die Basisangabe aller Aufträge gemeinsam aktualisieren und dann genau einmal einfrieren. `ff1eef39…` ist der Analyse-SHA, kein erfundener zukünftiger Merge-SHA.

```bash
set -euo pipefail
git fetch origin main
test -z "$(git status --porcelain)"
HBM_PARALLEL_BASE=$(git rev-parse origin/main)
printf '%s\n' "$HBM_PARALLEL_BASE" > /absolute/external/hbm-parallel-base.txt
git worktree add -b port/machines ../hbm-work-machines "$HBM_PARALLEL_BASE"
git worktree add -b port/weapons ../hbm-work-weapons "$HBM_PARALLEL_BASE"
git worktree add -b port/nuclear ../hbm-work-nuclear "$HBM_PARALLEL_BASE"
git worktree add -b port/rendering ../hbm-work-rendering "$HBM_PARALLEL_BASE"
for HBM_AREA in machines weapons nuclear rendering; do
  test "$(git -C "../hbm-work-$HBM_AREA" rev-parse HEAD)" = "$HBM_PARALLEL_BASE"
done
```

Die Befehle verweigern bereits existierende Branchnamen/Pfade; vorhandene Arbeit nicht löschen oder mit `-B` überschreiben. Den vollständigen SHA in allen vier Aufträgen und `area.json` festhalten. Basispatches/Overlayhashes gemeinsam einfrieren. Pro Auftrag separat `integrate_modernized.py <neuer-externer-pfad> --phase5` ausführen; keine gemeinsam beschreibbare M-Arbeitskopie, Welt, Datagenausgabe oder Gradleprojekt verwenden. O-Referenz bleibt read-only. Caches nur mit geeigneter Gradle-Sperrung teilen, Testwelten nie teilen.

Nach R-01 und nötigen M-01-Vertragslieferungen werden konkrete Abhängigkeitscommits in die konsumierenden Branches übernommen (oder als geprüfte Overlays im externen Build gebunden). Ihre **ursprüngliche Basis bleibt derselbe SHA**; ein anderer Branchkopf ist kein neuer ungeprüfter Basis-Pin.

## 7. Sichere Zusammenführung

1. Pro Bereich kleine PRs gegen `main`, mit Task-/Feature-IDs, O/M-Beleg, Dateiliste, Rechteakte, Abhängigkeits-SHAs, Tests und verbleibenden Lücken. Noch offene zentrale Requests oder nicht publizierbare notwendige Deltas ⇒ Draft/blockiert, keine Fertigmeldung. Keine Bereichs-PRs direkt gegenseitig mergen.
2. R legt einen temporären Integrationsbranch vom dann aktuellen `origin/main` an. Seit dem Basis-SHA hinzugekommene Änderungen prüfen; Basispin nicht stillschweigend verschieben. R-01/Registry-/API-Voraussetzungen zuerst, dann M, N und W gemäß tatsächlichem Abhängigkeitsgraphen; unabhängige Renderingkorrekturen können vorher hinein. Ganze Featurelieferungen mit ihren Abhängigkeiten auswählen, keine halben Reaktoren.
3. `git merge --no-ff --no-commit <geprüfter-bereichs-SHA>` auf dem Integrationsbranch; Konflikte vor Commit mit dem Dateieigentümer lösen. `git status`, `git diff --cached --check` und Pfadprüfung; bei unklarer Auflösung `git merge --abort`. Nie blind `--ours`/`--theirs` auf Register/Patches anwenden. Danach geprüften Merge committen. Git-konfliktfreie Patchdateien trotzdem gemeinsam in **einem frischen externen Checkout** anwenden: Textmerge beweist keine Laufzeitverträglichkeit.
4. Unveränderte Phase-3→4→5-Basis anwenden, dann geprüfte zentrale Lieferungen und Bereichsdeltas in dokumentierter Reihenfolge. Jeder Patch zuerst `git apply --check`; keine Fuzz-/Reject-Fortsetzung. Overlaykollisionen/Registryduplikate ablehnen. Endgültigen Quell-/Ressourcenbestand gegen Basis differenzieren, entfernte IDs/Dateien fachlich prüfen und alle Hashes erfassen.
5. G1–G8 auf dem zusammengeführten Stand durchführen. Jeder neue Integrationsfix ist ein eigener Commit mit betroffenen Eigentümern im Review und gezielter Testwiederholung; danach die gemeinsamen Regressionen erneut. Konfliktauflösungen selbst benötigen Tests. Prüfbelege sind an den **tatsächlich getesteten** Ziel-/Bereichs-/Integrations-SHA und JAR-Hash gebunden.
6. Erst danach Integrations-PR nach `main` mergen. Falls main inzwischen weiterläuft, Änderungen einbeziehen und relevante Gates vor Merge wiederholen. CI-Status des aktuellen PR-Heads prüfen; historische grüne Läufe reichen nicht. Kein Force-Push auf main oder gemeinsam genutzte Branches, kein automatisches Überschreiben geschützter Regeln.
7. Fehler nach Merge über einen nachvollziehbaren Revert der betroffenen atomaren Lieferung beheben. Bei Mergecommit vorher den richtigen Mainline-Elternteil prüfen (`git show --no-patch --pretty=raw <merge>`); abhängige Lieferungen gemeinsam zurücknehmen oder vorwärts reparieren. Keine persistierten Spielwelten durch blindes Code-Rollback migrieren. Branches erst nach Review/Integration und gesicherter externer Evidenz aufräumen.

## 8. Prüfung dieses Dokumentationsauftrags

Erneut gelesen wurden main und die fixierten O/M-Java-Bäume sowie Ressourcenpfade im Git-Baum; bestätigte Gegenbeispiele stehen in [FEATURE_GAPS.md](FEATURE_GAPS.md). Vorhandene Originalinventur: **12/12 Tests bestanden**, `inventory_original.py --check` erfolgreich, SHA256 `d392db7291b9bf0b29089f1829eb987fa3a6ebd6c01ceff90781f70a7699c2fb`. Erfolgreich geprüft: lokale Dokumentverweise, 140/140 eindeutige Feature-IDs, 36 eindeutige Aufgaben-IDs, Tabellenstruktur, konkrete O/M-Quellpfade, Bash-Syntax aller Befehlsbeispiele und `git diff --cached --check`. In diesem Dokumentationsauftrag wurden keine neuen Forge-/Client-/Multiplayerläufe ausgeführt; Phase-5-Ergebnisse sind ausdrücklich frühere Belege.
