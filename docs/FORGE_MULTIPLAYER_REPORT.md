# Phase 5: Forge 47.4.23 und isolierter Mehrspielertest

Stand: **20. Oktober 2026 (UTC)**. Ausgangspunkt ist `main` **`de6083c75c6dbb586d66cb6606d023d66c1ba26a`**, einschließlich des zusammengeführten [Phase-4-PR #5](https://github.com/urkrass06-oss/HBM-1.20.1/pull/5). Modernized bleibt am Commit **`0365cef5956016913095eeeb9366f26c601ca9a0`**, Minecraft **1.20.1**, Mod-ID **`hbm_m`**. Der reguläre Build verwendet weiterhin Forge **47.4.20**. Forge **47.4.23** wird zusätzlich als Laufzeit und im GameTest-Profil geprüft.

WASTELAND INDUSTRIES hat laut Auftraggeber noch keine endgültige Modliste/Konfiguration. Die Prüfungen betreffen die isolierte HBM-Kernintegration mit ihren eingebetteten Bibliotheken. Create und weitere Modpack-Mods waren nicht installiert.

## Unveränderte Phase-4-JAR auf Forge 47.4.23

JAR: `/workspace/scratch/modernized-phase4/integrated/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase4-dev+1.20.1-forge.jar`; SHA256 **`ba2be84cf560bb0eb6f145a4477c4a2098d18fa8c671378fcd081a9f416c64e9`**. Server und beide Produktionsclients verwendeten exakt diese Datei, keine Entwicklungsklassen und keine weiteren Gameplay-Mods.

| Tatsächlich ausgeführt | Beobachtung |
| --- | --- |
| Forge-Installer 47.4.23 gegen offiziellen SHA256 geprüft | `75cfcb11f60cc641dc83757c1357c08c9bdba255ec529feb115c5e89a59cf75a`. |
| Dedizierter Produktionsserver, zwei Starts | `Done` nach **66,285 s** und **32,918 s**; jeweils weitere **30 s**, Speichern, Exit **0**. Keine unerwartete ERROR-/FATAL-Zeile. |
| Zwei echte Produktionsclients gleichzeitig verbunden | `HBMClientOne` und `HBMClientTwo`, beide Forge 47.4.23/Java 17. Gemeinsame Verbindung vom zweiten Beitritt **05:43:52** bis zum geordneten Serverstopp **05:49:32 UTC**, rund **5 min 40 s**. Server-`list`, beide Clientlogs und lokale Sichtprüfungen belegen den gemeinsamen Weltzustand. |
| Maschineninventar und Energieanzeige | Beide Clients öffneten dieselbe Batterie und zeigten **123,46k HE** für serverseitig **123.456 HE**. Client 1 setzte eine HBM-Batterie in Slot 0 ein; Client 2 sah und entnahm sie; der Slot wurde auch bei Client 1 leer. Die Batterie lag anschließend einmal im Inventar von Client 2. |
| Energienetz | Zwei Schrabbatterien über einen `wire_coated` verbunden, Ausgabe-/Eingabemodus. Kontrollierter Mengenfall: **20.000.000 HE** aus der Quelle, Ziel zuvor 0; abschließend Quelle **0**, Ziel **20.000.000 HE**. Der frühere Versuch mit einem NBT-Wert oberhalb der Tierkapazität wird nicht als Mengenbilanz gewertet. |
| Tank, Inventar und Clientanzeige | Tank-Multiblock mit **38 Teilen**, anfangs **16.000 mB Wasser**. Ein Wassereimer aus Client 1 erhöhte den Füllstand auf **17.000 mB**; beide offenen Menüs zeigten denselben Wert und das leere Ausgabeeimer-Item. Das Tankmodell mit Wasserkennzeichnung war sichtbar. |
| Flüssigkeitsnetz | Zwei Tanks über fünf auf Wasser konfigurierte Ducts an Multiblock-Anschlüssen verbunden, Quellmodus 0/Zielmodus 2. Ergebnis: Quelle **0 mB**, Ziel **17.000 mB**, ohne Serverabsturz. |
| RBMK-Konsole und Steuerstab | AZ-5 über die echte Clientoberfläche setzte serverseitig `level` und `targetLevel` von **1 auf 0**. **Fehler:** das Reaktorfeld der Konsole blieb auf beiden Clients leer. Dieser Befund wird nicht als bestandener Synchronisierungstest gewertet. |
| Projektil und begrenzte Explosion | Eine serverseitig beschworene Standardgranate zerstörte die Glasfläche bei `(9,99,12)`; Projektil danach entfernt. Anschließend warf Client 1 das echte Granaten-Item; ein HBM-Granatenprojektil mit seiner Owner-UUID war serverseitig nachweisbar und wurde nach dem Flug wieder entfernt. Beide Clients blieben verbunden. Keine Nuklear-/Großexplosionsabnahme. |
| Speichern | `save-all flush`, `Saved the game`, geordnetes Speichern aller Dimensionen, Server-Exit **0**. Vor den Korrekturen wurde die gespeicherte Welt separat kopiert. |
| Singleplayer auf 47.4.23 | Eine Kopie der Phase-4-Testwelt wurde im Produktionsclient geladen, die vorhandene Batterie gerendert, das Menü geöffnet, gespeichert, zum Titel zurückgekehrt und der Client mit Exit **0** beendet. Dies ist ein begrenzter Welt-Upgrade-/Menütest. |

Die isolierte Testadresse war `127.0.0.1:59275`, Offline-Modus, zwei getrennte Spielverzeichnisse, keine echten Konten/Authentifizierungsdaten, RCON/Query deaktiviert. EULA-Annahme ausschließlich entsprechend dem Auftrag in dieser Testumgebung. Authlib konnte die Mojang-Schlüssel-/Skin-Dienste nicht direkt erreichen; die genauen Meldungen bleiben in den Logs sichtbar. Dies ist kein Nachweis für authentifiziertes Internet-Multiplayer.

## Nachtest mit der vollständigen Phase-5-JAR

Server und beide Produktionsclients verwendeten die **gegen Forge 47.4.20 gebaute** Datei auf Forge **47.4.23**:

```text
/workspace/scratch/modernized-phase5/final/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase5-dev+1.20.1-forge.jar
SHA256: 056beb76f3410d34aaf5553cfc5439e767c6b258e73edaa1366c66f05b6b77c3
Bytes: 44925653
```

Die bestehende isolierte Serverwelt wurde nach gesonderter Sicherung weiterverwendet; die alte Mod-JAR liegt separat unter `server-47.4.23/tested-phase4-mod/`. Der neue interaktive Lauf `multiplayer-fixed` startete nach **117,126 s**, endete mit gespeichertem Spiel und Exit **0**, Gesamtdauer **466,073 s**. Gemeinsame Clientverbindung **06:14:03–06:18:22 UTC**, etwa **4 min 19 s**. Die Beobachtungen sind begrenzte Szenarien, keine mehrstündige Stabilitätsmessung.

| Tatsächlich erneut geprüft | Ergebnis |
| --- | --- |
| Laden der Phase-4-Mehrspielerwelt | Einzelbatterie **123.456 HE**, Netzquelle **0 HE**, Netzziel **20.000.000 HE**, Tanks **0/17.000 mB**, Wasserkennung des Ducts und RBMK-Stabwert **0** erhalten. |
| RBMK-Liveanzeige bei beiden offenen Konsolen | Steuerstab serverseitig entfernt: Spalte verschwand in beiden GUIs. Neuer Stab: Spalte erschien mit **100 %**. Beide Schritte ohne Schließen oder Neuladen der Menüs. |
| RBMK-Steuerung von beiden Clients | Client 1 setzte Zielwert **0,25**, laufender Stabwert aktualisierte sich bei Client 2. Bildschirmtyp von Client 1 auf `CONTROL` umgeschaltet und auf beiden sichtbar. Client 2 löste AZ-5 aus; Server `level = targetLevel = 0`, beide Tooltips **0,0 %**. |
| Inventar in umgekehrter Richtung | Die eine gespeicherte Batterie aus Client 2 in den gemeinsamen Maschinen-Slot eingelegt; Client 1 sah und entnahm sie. Anschließend Client 1 genau **1 Batterie**, Client 2 keine, Maschinen-Slot leer. Keine zusätzliche Batterie für diesen Nachtest erzeugt. |
| Wasser und Moduspaket | Weiterer Eimer von Client 1: **17.000 → 18.000 mB**, gleicher Wert in beiden Menüs, leerer Ausgabeeimer. Client 2 schaltete über die GUI **2 → 3 → 0**. Mit Gegenstelle im Eingabemodus flossen **18.000 mB** zurück; Ziel **18.000**, Quelle **0**, beide offenen Menüs zeigten den Abfluss bis 0. |
| Spielergranate und Explosion | Client 1 warf das echte Granaten-Item. Projektil-Owner entsprach seiner Offline-UUID; anschließend Projektil entfernt und Glasblock `(9,99,12)` zu Luft zerstört. Die Glaslücke war auch bei Client 2 sichtbar; beide blieben verbunden. |
| Speichern | Batterie-/Tank-/RBMK-NBT und beide Spielerinventare abgefragt, Spiel und alle Dimensionen gespeichert, Exit 0. Sechs Arena-Chunks wurden vor diesem Speicherpunkt ausdrücklich force-geladen; dieser Fall ersetzt keinen Test des normalen Chunkentladens. |

Ein früher Quick-Play-Beitritt von Client 1 wurde mit **„Server is still starting“** zurückgewiesen; die Wiederverbindung war erfolgreich. Sieben frühe NBT-Konsolenabfragen direkt nach Start ergaben **„An unexpected error occurred trying to execute that command“**. Nach Spielerbeitritt liefen dieselben sieben Abfragen erfolgreich. Die ersten Abfragen gelten als fehlgeschlagene Harness-Schritte; die genaue interne Ausnahme wurde nicht ausgegeben. Die spätere Persistenzprüfung wartet auf vollständigen Start und prüft die geladenen Arena-Chunks ausdrücklich. Einzelne `Can't keep up`-Meldungen unter gemeinsamer Zwei-CPU-/Speicherlast und eine `moved too quickly`-Warnung während eines Testteleports bleiben protokolliert. Kein unerwarteter ERROR-/FATAL-Eintrag oder Serverabsturz in diesem Lauf; die Yggdrasil-Abfrage bleibt gesondert sichtbar.

**Abschließender Neustart ausgeführt:** `reload-fixed`, `Done` nach **51,345 s**, Gesamtdauer **183,205 s**, erneut gespeichert und Exit **0**. Vor Spielerbeitritt bestätigten die Abfragen die sechs geladenen Arena-Chunks sowie **123.456 HE**, **20.000.000 HE**, **18.000/0 mB**, leeren Ausgabeeimer, Bildschirmtyp `CONTROL` und Stabwert **0**. Keine fehlgeschlagene Konsolenabfrage in diesem Wiederholungslauf. Beide Clients verbanden sich erneut **06:20:57–06:21:57 UTC**, also **60 s** gleichzeitig. Spielerinventare entsprachen dem gespeicherten Zustand; beide geöffneten Tankmenüs zeigten nach dem Neustart **18.000 mB**.

**Singleplayer auch mit der korrigierten JAR ausgeführt:** Client 1 lud anschließend die gesonderte Weltkopie `Phase5SingleplayerFinal`, stellte die vorhandene Batterie dar, öffnete ihr Menü, speicherte alle Dimensionen und kehrte zum Titel zurück. Beide Produktionsclients wurden regulär mit Exit **0** beendet. Clientprozessdauern **829,008 s** und **696,180 s** umfassen Laden, Menüs, Multiplayer/Neustart und bei Client 1 Singleplayer; sie sind keine reine Gameplay-/Lastmessung. Die bekannten Renderer-/Assetfehler blieben bestehen.

## Reproduzierte Fehler und Korrekturen

Ein gezielter Lauf gegen die **noch unkorrigierten** Klassen auf Forge 47.4.20 führte **11 GameTests** aus: **7 bestanden, 4 fehlgeschlagen**, GameTest-JVM Exit **4**, Gradle Exit **1**. Die später ergänzten Autorisierungs-/HIGH-Grenztests waren in diesem Ausgangslauf noch nicht enthalten.

| Reproduktion | Änderung im Phase-5-Patch |
| --- | --- |
| Laufendes RBMK-Blockentity-Paket verlor die Spaltendaten | `onDataPacket` führt denselben vollständigen Datenpfad wie die anfängliche Chunk-Synchronisierung aus. Der Regressionstest prüft Hinzufügen und Entfernen einer Spalte. |
| Ungültige RBMK-Auswahllänge | Länge vor Allokation auf **0–225** und verfügbare Bytes begrenzt. Aktionen, endliche Stellwerte, Index-/Farb-/Bildschirmgrenzen und Ursprungsformat geprüft. |
| RBMK-Steuerung ohne überprüften offenen Menübezug | Gleiche Konsole in derselben Welt, geladenes Ziel, lebender Spieler, gültiges nahes Menü und gültiger Weltursprung erforderlich. Gültige Clientaktionen bleiben erhalten. |
| Große HE-Menge als negativer Forge-Energy-`int` | Normale FE-Ansicht liefert gesättigte nichtnegative Werte; negative Transferanforderungen liefern 0. HIGH-Einheiten passen nur bei ausreichend freiem Speicher einschließlich LOW-Rest. Die bestehende spezielle HIGH-Semantik bleibt erhalten und ist keine Create-Abnahme. |
| Zweite Energieübertragung im selben Leveltick | Gemeinsamer Tickpfad und Forge-Leveltick teilen sich einen Tickschutz pro `EnergyNetworkManager`. Andere Dimensionen behalten ihren eigenen Manager. |

**GameTests nach Korrektur auf 47.4.20: 14/14 bestanden, Exit 0.** Erfasst: ursprüngliche drei Basisprüfungen, FE-Grenzwerte/Simulation, HIGH-Restkapazität, Draht-Mengenbilanz, doppelter Netzaufruf, Fluid-Simulation/Typäquivalenz/NBT, Tankaufbau/NBT, RBMK-Steuerstab/AZ-5, laufende Konsolenpakete, Paketlängen, ungültige Aktionsdaten und Menü-/Entfernungs-/Stale-Block-Autorisierung. Autorisierungsfälle verwenden einen Forge-FakePlayer als Testfixture; die oben dokumentierten zwei Multiplayer-Clients waren echte Minecraft-Prozesse.

**Auf Forge 47.4.23 ebenfalls 14/14 GameTests bestanden, Exit 0**, tatsächliche Versionsmeldung `MinecraftForge v47.4.23 Initialized`. Die vollständige Produktions-JAR bestand außerdem zwei dedizierte Forge-47.4.20-Starts mit je 30 Sekunden Beobachtung, Save/Stop und Exit 0. Der JAR-Vergleich hat **keinen entfernten oder hinzugefügten Eintrag** und **keine Änderung an Assets/Datendateien** festgestellt; geändert wurden nur vier Klassen, Modmetadaten und Änderungsvermerk.

## Build-/Paketkontrolle

Datagen erzeugte erneut **7.952 Dateien**, Manifest-SHA256 **`cc5e858c1c85e6f409141d2a1eaa558731001551b3cabb1182d307a7893c2700`**, bytegleich zur Phase-4-Inventur. JDK 21.0.12.1+1/Gradle 9.3.1 für den Build, JDK 17.0.20.1+1 und `--release 17` für die Mod.

Ein eigener fehlgeschlagener Buildablauf wurde erkannt und verworfen: `runData build sourcesJar` in einem Gradleaufruf verpackte vor den Datagen-Ausgaben. Kandidatenhash **`df1c0df4598ec078f4753156e627b980dffa2b3807caa02496560c0cf129402a`**; das neue Paketgate weist **7.823 fehlende generierte Ressourcen** nach. Ein dadurch gestarteter Serverlauf wird nicht als Nachweis der vollständigen Basis gewertet; dessen zweiter Lauf wurde gezielt beendet. `modernized_build.py` verweigert solche kombinierten Datagen-Aufrufe nun. Datagen und Produktionsbuild müssen getrennte Aufrufe sein. Die CI prüft zusätzlich die Anwesenheit aller generierten Ressourcen und den Ausschluss der Testklassen/-struktur.

Die weiterhin tolerierten **66 Javadocfehler/100 Warnungen** sind kein erfolgreicher Javadocnachweis. Der vollständige Code-/Assetbestand sowie Evaluations-JARs bleiben wegen der offenen Rechtefragen außerhalb dieses öffentlichen Repositorys. Veröffentlicht werden eigene Werkzeuge, Tests, ein kleiner nachvollziehbarer GPL-Patch, erhaltene Lizenztexte und Textnachweise.

## Reproduktion

Aus dem Repository heraus; alle Platzhalter auf **neue externe** Verzeichnisse beziehungsweise vollständige JDKs setzen:

```bash
export HBM_TEST_ROOT=/absolute/external/hbm-phase5
export HBM_JAVA21=/absolute/toolchains/jdk-21
export HBM_JAVA17=/absolute/toolchains/jdk-17
python3 tools/integrate_modernized.py "$HBM_TEST_ROOT/modernized" --phase5
python3 tools/modernized_build.py run "$HBM_TEST_ROOT/modernized" runData \
  --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
  --gradle-home "$HBM_TEST_ROOT/gradle-home" --log-dir "$HBM_TEST_ROOT/logs"
python3 tools/modernized_build.py run "$HBM_TEST_ROOT/modernized" build sourcesJar \
  --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
  --gradle-home "$HBM_TEST_ROOT/gradle-home" --log-dir "$HBM_TEST_ROOT/logs"
python3 tools/audit_modernized.py jar \
  "$HBM_TEST_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase5-dev+1.20.1-forge.jar" \
  --generated-source "$HBM_TEST_ROOT/modernized/src/generated/resources"
for runtime_forge in 47.4.20 47.4.23; do
  python3 tools/test_modernized_server.py \
    "$HBM_TEST_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase5-dev+1.20.1-forge.jar" \
    "$HBM_TEST_ROOT/server-$runtime_forge" --forge "$runtime_forge" \
    --java17-home "$HBM_JAVA17" --accept-eula
  python3 tools/modernized_build.py run "$HBM_TEST_ROOT/modernized" runGameTestServer \
    --java21-home "$HBM_JAVA21" --java17-home "$HBM_JAVA17" \
    --gradle-home "$HBM_TEST_ROOT/gradle-home" --log-dir "$HBM_TEST_ROOT/logs" \
    --gradle-arg=-Pmodernized.gameTests=true --gradle-arg="-Pdeps.forge=$runtime_forge"
done
```

Im lokalen Cloudlauf zusätzlich `--trust-store /etc/ssl/certs/java/cacerts`; beim Server außerdem `--allow-offline-auth-failure` nur für die dokumentierte einzelne Yggdrasil-Public-Key-Fehlermeldung. Die Ausnahme bleibt in `environment_error_lines` sichtbar und erlaubt keine anderen ERRORs.

Für die Produktionsclients stellt [modernized_client.py](../tools/modernized_client.py) offizielle, hashgeprüfte Mojang-/Forge-Bestände in einem externen Installationsverzeichnis bereit. Linux x86_64, Xorg-Dummy-Treiber, Mesa/OpenGL, libX11 und libXtst werden benötigt. [xorg-dummy.conf](../tools/modernized/xorg-dummy.conf) ergibt das getestete 1280×720-Display; Xorg mit `-nolisten tcp` auf `:99` und `:100` starten. Beide Clients rendern mit llvmpipe, 854×480, 1.800 MB Heap, Sicht-/Simulationsdistanz 2, 20 FPS. Der dedizierte interaktive Server verwendete 1.600 MB Heap; für drei Prozesse waren hier 8 GiB cgroup-RAM ohne Swap verfügbar. Keine Hardware-GPU-/Audioabnahme oder Lastmessung.

```bash
python3 tools/modernized_client.py prepare "$HBM_TEST_ROOT/client-install" --forge 47.4.23 \
  --assets "$HBM_TEST_ROOT/assets" --java17-home "$HBM_JAVA17"
# In einem separaten Terminal, bestehende isolierte Serverinstallation:
python3 tools/modernized_server_session.py "$HBM_TEST_ROOT/server-47.4.23" \
  "$HBM_TEST_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase5-dev+1.20.1-forge.jar" \
  --forge 47.4.23 --session multiplayer --java17-home "$HBM_JAVA17" --accept-eula
# Auf Done warten, die Arena-Chunks laden und die beiden Clients verbinden.
DISPLAY=:99 LIBGL_ALWAYS_SOFTWARE=true ALSOFT_DRIVERS=null \
python3 tools/modernized_client.py launch "$HBM_TEST_ROOT/client-install" \
  "$HBM_TEST_ROOT/client-one" \
  "$HBM_TEST_ROOT/modernized/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase5-dev+1.20.1-forge.jar" \
  --username HBMClientOne --java17-home "$HBM_JAVA17" --server 127.0.0.1:PORT
# Gleichzeitig in einem zweiten Terminal: DISPLAY=:100, neues client-two, --username HBMClientTwo.
```

Der Starter verweigert bestehende Spiel-/Installationsverzeichnisse, schreibt vollständige Befehle/JAR-Hash/Exitcode in `launch.json` und erlaubt Offline-Direktverbindung ausschließlich zu `127.0.0.1:PORT`. Ein zunächst falsch zusammengesetzter Teststarter-Classpath erzeugte einen doppelten Minecraft-Modulfehler; der dokumentierte Fehlversuch blieb erhalten. Nach Entfernen des rohen Vanilla-JAR aus dem Forge-Classpath starteten beide Produktionsclients regulär.

Die [Arena-Kommandos](../tools/modernized/multiplayer-fixture.commands) sind für eine wegwerfbare Testwelt bestimmt; Kommentare vor Einspeisen in die Serverkonsole herausfiltern. Nach Inventartest beide Clients an den Tank teleportieren, Client 1 einen Wassereimer geben und über den Tank-Füllslot einlegen. Danach Quelltank auf Modus 0 und die fünf Ducts per `data merge block -9 100 Z {FluidType:"minecraft:water"}` für Z=3…7 konfigurieren. Füllmengen vor/nach Transfer serverseitig abfragen. RBMK-Konsole bei `(0,100,8)`, Stab bei `(3,100,8)`; GUI-AZ-5 erst aufklappen, dann auslösen. Standardgranate und Glasfläche separat im Arena-Bereich testen. Vor `save-all flush` die geprüften Zustände und `list` protokollieren, anschließend geordnet stoppen und beim Neustart dieselben NBT-Werte sowie beide Clientbeitritte prüfen.

[modernized_xinput.py](../tools/modernized_xinput.py) unterstützt `click X Y`, `right X Y`, `move X Y`, `key`, `text` und `selectall` auf dem expliziten `DISPLAY`. Die Sichtprüfungen sind keine automatische Bildvergleichssuite; sie sind mit Screenshothashes und Rohlogs dokumentiert.

## Noch offene Abnahme

Breite Produktionsketten, sämtliche Maschinen und Reaktortypen, Brennstoff-/Wärme-/Dampfkreisläufe, Meltdowns, Schusswaffen/Munition, große/nukleare Explosionen, Chunk-/Dimensionswechsel, mehrere Stunden Betrieb, Paketverlust/Latenz, Last/TPS, echte Onlineauthentifizierung, Clienthardware/Audio und Create-/Modpack-Kombinationen sind weiterhin offen. Die bekannten ungültigen Assetpfade, Platzhaltertextur, fehlerhaften OBJ-Bakes und fehlenden Modelle verhindern eine vollständige Renderingfreigabe. Siehe [REMAINING_ISSUES.md](REMAINING_ISSUES.md).

Die Baseline-Nachweise sind über [baseline-evidence.json](integration/phase5/baseline-evidence.json) mit Quellpfad, SHA256 und vollständigem Textumfang verknüpft. Lokale Welten, Assets, Screenshots, Minecraft-Dateien und Mod-JARs werden nicht veröffentlicht. Die Tests erlauben eine begrenzte Kompatibilitätsaussage, keine fertige WASTELAND-INDUSTRIES- oder Releasefreigabe.

Abschließende Belege: [Builds/GameTests](integration/phase5/build-evidence.json), [Mehrspieler-/Neustartläufe](integration/phase5/multiplayer-evidence.json), [vollständige Clientlogs und Befehle](integration/phase5/client-evidence.json), [maschinell lesbare Ergebnisse](integration/phase5/results.json), [75 lokale Screenshothashes](integration/phase5/local-screenshots.json). Die Bilder selbst bleiben extern. Alle Zahlen sind gemessene lokale Ergebnisse; neue GitHub-Actions-Läufe sind davon getrennt zu beurteilen.
