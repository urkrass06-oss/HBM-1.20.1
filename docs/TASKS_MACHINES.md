# Auftrag M: Maschinen und Industrie

Alle Aufgaben gelten für die externe Phase-5-Basis am gemeinsamen main-SHA aus [PARALLEL_DEVELOPMENT.md](PARALLEL_DEVELOPMENT.md). O/M-Pins, Rechteprüfung, Dateireservierung und Gates G1–G8 sind verpflichtend. `M:` beginnt unter `src/main/java/com/hbm_m/`, `O:` unter `src/main/java/com/hbm/`, sofern nicht anders angegeben. **„Neu“ bezeichnet vorgeschlagene Dateien/Tests, keine vorhandene Implementierung.** P0 zuerst, P1 danach, P2/P3 nach den genannten Abhängigkeiten; jede Zeile ist eine eigene funktionale Lieferung mit Tests. Fehler nur korrigieren, wenn reproduziert; eine offene Prüfung ist kein Beweis eines Defekts.

Tests werden neu unter `tools/modernized/parallel/machines/gametest/com/hbm/integration/machines/` geliefert und im externen Testprofil ausgeführt. Testnamen unten sind verbindliche vorgeschlagene Prüffälle; bestehende 14 Regressionen bleiben zusätzlich aktiv. Fachliche Sollwerte aus O mit Quellformel und Konfiguration belegen, später gegen die getrennte 1.7.10-Laufzeit messen. Öffentliche Dateien nur nach Einzelprüfung ihrer Herkunft veröffentlichen.

## Zuständigkeit und erste Lieferung

M besitzt nichtnukleare Maschinen, HE-/Fluidnetze, Industrie-/Öl-/Chemieprozesse CHEM-001–008 und Logistik. CHEM-009–012, Breeder, Watz, RBMK/ZIRNOX und Core gehören N; Waffenfertigung/Launchpads/Turrets W. Zentralregister, allgemeine Datagenprovider, Screen-/Rendererdateien und Ressourcenintegration gehören R. M liefert dafür Requests mit IDs, Slot-/Feldvertrag und erforderlichen Modellen. Keine Änderung der drei bestehenden Basispatches oder der Root-Foundation.

**Zuerst M-01:** vorhandene Energie-/Fluidbasis unter Entladen/Laden und zwei Dimensionen ausführbar absichern. Damit können N/W dieselben APIs verwenden. M-02 kann danach die erste vollständige Produktionskette liefern. Keine zweite universelle Maschinenbasis bauen.

## Priorisierte Implementierungsaufträge

| Task / Priorität / Feature | Konkrete Klassen und Lieferung | Abhängigkeiten | Überprüfbare Abnahme |
| --- | --- | --- | --- |
| **M-01 / P0** NET-001–006, BASE-005/008 | `M:api/energy/EnergyNetworkManager.java`, `EnergyNetwork.java`, `LongEnergyWrapper.java`, `HbmForgeWrapper.java`, `WireBlockEntity.java`; `M:api/fluids/FluidNet.java`, `inventory/fluid/tank/FluidTank.java`, `blockentity/machines/FluidPumpBlockEntity.java`, `FluidValveBlockEntity.java`. Capability-/Netzlebensdauer prüfen, nachgewiesene Fehler beheben; stabile API-Lieferung. | R-01 Testeinbindung; bestehende Phase-5-Korrekturen | Neu `networkUnloadReloadConservesAmounts`, `networksAreDimensionLocal`, `capabilitiesInvalidateOnRemoval`: normale Chunkentladung, Wiederaufbau/Split/Merge, alte Capability nach Entfernung ungültig, unveränderte HE-/Fluidbilanz ohne Quelle/Senke. Simulation mutiert nicht; Druck 0–5 und inkompatible Stoffe getrennt prüfen. Bestehende FE-/HIGH-/Doppelticktests bestehen unverändert. |
| **M-02 / P1** IND-001–003/007, BASE-009/012 | `M:blockentity/machines/MachinePressBlockEntity.java`, `MachineShredderBlockEntity.java`, `BlastFurnaceBlockEntity.java`, `MachineAssemblerBlockEntity.java`, zugehörige `recipe/*` und `datagen/recipes/custom/*`. Vorhandene Kette Erz/Material → Schmelzen/Legierung → Stempel/Presse → Montage funktionsfähig vervollständigen; keine fehlende Maschine behaupten. O-Einstiege `TileEntityMachinePress`, Originalrezepte aus der Matrix. | M-01; R Registry-/Rezept-/Screenrequests | `pressRejectsWrongDie`, `assemblerRecipeRoundTrip`, `blockedOutputDoesNotConsume`: mindestens ein konkret dokumentiertes O-Rezept je Stufe mit identischen Mengen/HE/Ticks/Resten. Falscher Stempel, fehlende Energie, volle Ausgabe, Shift-Klick/Automation und Save mitten im Prozess. Survivalpfad ohne Kreativquelle/Befehlsmaterial nachspielen; Rezept-IDs im Nachweis nennen. |
| **M-03 / P1** CHEM-001 | `M:blockentity/machines/MachineChemicalFactoryBlockEntity.java` besitzt nur Netzinitialisierung; Fachprozess, Slotregeln und Menü ergänzen, `block/machines/MachineChemicalFactoryBlock.java`/neues Menü über R anbinden. `O:tileentity/machine/TileEntityMachineChemicalFactory.java`, `inventory/container/ContainerMachineChemicalFactory.java`; vorhandene `MachineChemicalPlantBlockEntity` und Prozessmodule wiederverwenden. | M-01; M-02 Rezeptgrundlagen; R zentrale Registrierungen/GUI | `chemicalFactoryProcessesRecipe`, `chemicalFactoryFullOutputIsAtomic`: ein belegtes Mehrstoffrezept verbraucht genau Zutaten/HE, erzeugt genau Produkte nach O-Ticks; keine Teilentnahme bei gesperrter Ausgabe. Alle Slots/Tanks, Seiten und Fortschritt über Save/Load; zwei Clients sehen denselben Prozess. Registry `chemical_factory` bleibt erhalten. |
| **M-04 / P1** CHEM-004–008 | Zuerst `M:blockentity/machines/MachineFractionTowerBlockEntity.java` (bisher nur Fortschrittszähler), anschließend einzeln `MachinePumpjackBlockEntity`, `MachineVacuumDistillBlockEntity` und Cracking-/Hydrotreater-Gerüste. O:`tileentity/machine/oil/TileEntityMachineFractionTower.java`, `TileEntityMachineRefinery.java`. Bestehende `MachineRefineryBlockEntity.refine()` als Teilbestand erhalten. | M-01/M-03; N-08 Verschmutzungsschnittstelle erst für Emissionen | `fractionTowerBalancesFluids`, `refiningStopsOnFullTank`: dokumentiertes O-Input/Mehrproduktrezept mit Typ/Druck/Mengen, korrektem Energie-/Tickverbrauch, begrenzten Ausgaben und Roundtrip aller Tanks. Pro weiterer Maschine eigener belegter Prozess und Test; bloß laufender Fortschrittsbalken reicht nicht. |
| **M-05 / P2** CHEM-003, IND-004 | `M:block/ModBlocks.java` enthält `electrolyser`, `radiolysis`, `rotary_furnace` als generische Blöcke (Schreiber R). Neu jeweils eigene Block-/BE-/Menü-/Rezeptklassen durch M; `MachineDeuteriumTowerBlockEntity` vervollständigen. O:`TileEntityElectrolyser`, `TileEntityMachineRadiolysis`, `TileEntityMachineRotaryFurnace`. | M-01/02/03; R ersetzt Registrylieferant unter derselben ID | `electrolyserSeparatesProducts`, `radiolysisRequiresSource`, `rotaryFurnaceUsesFuel`: jede Maschine verarbeitet mindestens ein O-Rezept mit allen Betriebsbedingungen/Produkten; fehlende Quelle/volle Ausgabe stoppt ohne Verlust. R Registrytest beweist tatsächlich erzeugte BE und Serverticker, keine generische `Block`-Instanz mehr. |
| **M-06 / P2** IND-012–016 | Bestehende `MachineIndustrialTurbineBlockEntity.processTurbine()` und passende Boiler-/Kondensator-/Solarpfade aus `ModBlockEntities` zu einer geschlossenen O-Dampfversorgung verbinden; konkrete Dateiliste vor Änderung reservieren. | M-01/02; N-02 liefert Reaktordampf als optionalen zweiten Erzeuger | `steamLoopAccountsForWaterAndEnergy`: Eingangsmedium, Druckwechsel, Dampfverbrauch, Kondensat und HE je dokumentierter O-Kette bilanzieren, einschließlich zulässiger Verluste. Kein Betrieb mit falschem Druck, kein unendlicher Kreislauf ohne Wärmequelle; Weltneustart und zwei Clients bestehen. |
| **M-07 / P2** NET-007–010 | `M:block/ModBlocks.java` enthält `conveyor*` als Platzhalter. Neu bereichseigene Transport-BE/Logik, zuerst einzelnes Förderband mit Übergabe, dann Doppel-/Express-/Tripelvarianten; O-Einstiege aus NET-007–010 der Originalmatrix. Krane/Pneumatik/Drohnen als jeweils separate Lieferungen auf derselben Itembilanz. | M-01; R Registrierungen/Entity-/Rendererrequests | `conveyorTransfersOnce`, `conveyorUnloadKeepsStacks`: ein ItemStack über mehrere gedrehte Bänder an Lager übergeben, Rückstau, Split/Merge, Chunkgrenze und Save/Load ohne Duplikation/Verlust. Geschwindigkeit/Filter je O-Variante belegen. Jede weitere Logistikfamilie eigener Request, ausführbarer Pfad und Bilanztest. |
| **M-08 / P2** NET-003, COMPAT-005 | O:`tileentity/network/TileEntityConverterHeRf.java`, `TileEntityConverterRfHe.java`; auf vorhandener `M:api/energy/HbmForgeWrapper.java`-Außenansicht dedizierte Konverter implementieren, nicht sämtliche Speicher umskalieren. | M-01; R neue Konverter-Registrierungen | `converterDirectionsAndRemainders`: Default **5 HE → 1 RF** und **2 RF → 5 HE** getrennt als O-Spezifikation; konkrete FE-Zielabbildung dokumentieren, Restmengen/Simulation/Int-Grenzen/volle Puffer und konfigurierte Verluste testen. Kein aus beiden Raten unbeabsichtigt unbegrenzter Energiegewinn; Abweichung ausdrücklich reviewen. Create erst mit versionierter Installation separat testen. |
| **M-09 / P3** übrige IND, NET-011–013, PLAYER-005 | Je nächste Lieferung einen konkreten O-Einstieg aus der Matrix portieren: zuerst `IND-018` mit `O:tileentity/machine/TileEntityMachineSuperComputer.java` und `inventory/recipes/SuperComputerRecipes.java`, danach Maschinenwerkzeuge/Scanner und `O:tileentity/network/TileEntityRadioTelex.java`. Vorhandene `M:blockentity/crates/BaseCrateBlockEntity.java` plus konkrete Kisten auf Zugriffs-/Automationsregeln vervollständigen. Für bisher nicht belegte Gegenstücke zuerst reproduzierbaren fehlgeschlagenen Fachtest schreiben und dann implementieren. | M-02/07; zentrale Requests R | `crateAccessAndAutomation`, für Supercomputer eigenes O-Rechenrezept, für Telex Nachricht zwischen zwei Geräten mit Speichern/Neustart. Pro Feature echte Aktion/Ausgabe, nicht nur Registrierung. Originalvarianten/erreichbare IDs vollständig zuordnen; ungeprüfte übrige Fälle offen lassen. |
| **M-10 / P2** IND-005/006/008/017, CHEM-002 | Bestehende `M:blockentity/machines/MachineCrucibleBlockEntity.java`, `MachineFoundryChannelBlockEntity.java`, `MachineFoundryBasinBlockEntity.java`, `AnvilBlockEntity.java`, `MachineSolderingStationBlockEntity.java`, `MachineArcWelderBlockEntity.java`, `MachineMixerBlockEntity.java`, `MachineCrystallizerBlockEntity.java`; Stranggießer als eigene neue BE-/Rezeptlieferung nach O-Einstieg IND-006. Je Verfahren einen vollständigen O-Materialpfad implementieren oder vorhandenen Pfad fachlich korrigieren, kein Umklassifizieren vorhandener Maschinen als fehlend. | M-01/02/03; R Registrierungen/Screens bei neuen Pfaden | `foundryAccountsForMoltenMaterial`, `mixerAndCrystallizerPreserveProducts`, `formingRecipeCostsAndToolWear`: Originalmengen/Temperatur-/Form-/Werkzeugbedingungen und Nebenprodukte, blockierte Ausgaben, Rotation, Automation und Midcycle-Roundtrip. Stranggießer benötigt echte Formgebung mit Testoutput; Schweißen/Löten/Amboss erhalten eigene nachgewiesene Rezepte. |

Alle genannten M-Pfade müssen am Pin bzw. mit den Basispatches existieren oder ausdrücklich als neu markiert sein; exakte zusätzliche Dateien vor Änderung reservieren.

## Lieferumfang und Mehrspielerabnahme

Jede Lieferung enthält Implementierung, bereichseigene erforderliche GameTests, konkrete O-Rezept-/Prozessdaten und die Registry-/Screenrequests an R. Bei unbekannter Laufzeitparität die Quellherleitung und offene O-Messung nennen; keine bestehende Rezeptkette entfernen. G1–G7 pro Lieferung, G8 am Integrationsstand.

Zwei echte Clients bedienen dieselbe Maschine gleichzeitig, setzen/entnehmen Inputs in entgegengesetzter Richtung und prüfen HE/Fluid/Slots während des Prozesses. Danach ohne Forcechunks entladen/laden und Server neu starten: Zwischenfortschritt, Stofftypen/-druck und Mengen erhalten; keine zweite Ausgabe. Neue Maschinen müssen aus den dokumentierten Rezepten erreichbar sein. Tests mit Kreativquellen dürfen Isolation belegen, ersetzen aber die Survivalabnahme nicht.

## M-01-Lieferung vom 20.10.2026

Gemeinsamer Startcommit: `997b15c9d60dd293e9c436663e90a95140ab13af`,
eigener Branch `port/machines`. M/O bleiben an den oben festgelegten Pins.
[Liefermanifest](../tools/modernized/parallel/machines/area.json),
[Rechte je Payload](../tools/modernized/parallel/machines/rights.json) und
[Quell-/Kontextakte](../tools/modernized/parallel/machines/evidence/source-rights.json).
Nur fünf der neun reservierten Produktionsdateien ändern sich:
`EnergyNetwork`, `WireBlockEntity`, `FluidTank`, `FluidPumpBlockEntity`,
`FluidValveBlockEntity`. Der kleine GPLv3-Patch behebt sechs nachgewiesene Fehler:
verwaiste Einzelknoten, erneuerte Ladetickets durch Abfragen ruhender Chunks,
endgültig invalidierte Draht-Capabilities, zurückgehaltene Ventilnetzknoten,
abgewiesene interne Drucktransfers und nicht zur Speicherung gemeldete Pumpenpuffer.
Signaturen, HE-Einheiten, IDs, Menüs und Pakete bleiben erhalten.

Acht eigene erforderliche Regressionen ergänzen unverändert alle 14 Basistests.
Mit exakt derselben Testquelle bestehen auf unveränderter Phase 5 nur **15/22**;
sieben neue Prüfungen scheitern. Mit den Korrekturen bestehen **22/22** auf
Forge 47.4.23 / Java 17. Der Entladetest verlangt tatsächlich nicht mehr geladene
Chunks, neue BlockEntity-Identitäten und wieder aufgebaute Netze; auslaufende
Vanilla-Portaltickets ersetzen keine permanente Entladung. Er prüft
20.000.000 HE / 18.000 mB, daneben getrennte Dimensionen, Split/Merge,
Capabilities, Simulation, Stoff/Druck 0–5 sowie Pumpen-Speichermeldungen.

[Buildnachweis](../tools/modernized/parallel/machines/evidence/build-summary.json):
zweimal identische Datagen mit 7.952 Pfaden, separates `build sourcesJar`,
Java-17-/Jar-in-Jar-/Produktionsaudit erfolgreich. Kein Testinhalt und keine
entfernten Dateien/Ressourcen im Produktionspaket. Die bekannten 66
Javadocfehler und 100 Warnungen sind weiterhin offen. Produktions-SHA256:
`46affa601e100d88cd1eb56cb990c6a82dca25a93d995c9544dae7961864307d`.

R-01 ist mit `c63be0f5bcf43ff1d1f8b4febb25f831a15fc047` / API `1`
konkret gebunden. Der strenge Loader blockiert die noch fehlende zentrale
Testzieldatei-Reservierung; der [exakte Request an R](../tools/modernized/parallel/machines/requests/R-01-machines-policy.json)
liegt bei. Zentrale Dateien wurden nicht geändert. Die 22 Tests wurden gemäß
Abschnitt 5 des Parallelvertrags manuell auf der eingefrorenen Phase-5-Basis
ausgeführt; die kombinierte 24er-Suite mit R ist noch kein bestandener Nachweis.

Originalverträge sind [quellgestützt](../tools/modernized/parallel/machines/evidence/original-contracts.json);
G7 benötigt weiterhin den getrennten O-/JDK8-Messlauf. G8 folgt erst nach der
geprüften Zusammenführung aller vier Lieferungen. Offene zentrale Requests
und Gates halten den Code-PR im Draft; dies ist keine vollständige Port- oder
Originalparitätsfreigabe.

Die Produktion lief mit zwei echten Clients mindestens **606 s** gemeinsam
(17:39:06–17:49:12 UTC). Batterieinventar in beide Richtungen, zwei Wassereimer,
Tankmoduspaket, HE-/Fluidbilanz sowie RBMK- und echte Spielergranatenaktionen
wurden geprüft. Beide Spieler wechselten in den Nether; drei entfernte
Arenachunks waren nachweislich ungeladen. Nach Rückkehr übertrugen beide Netze
auch in Gegenrichtung ohne Verlust. Zwei Dedicated-Serverstarts, jeweils mehr
als 30 s nach `Done`, Save/Stop und Exit 0, bestätigen nach Neustart
20.000.000 HE, 18.000 mB, unveränderte Inventare und 7.000 mB Wasser bei Druck 3
im separaten Pumpenpuffer. Beide Clientmenüs zeigen erneut 18.000 mB.
[Runtimebefund](../tools/modernized/parallel/machines/evidence/runtime-results.json)
und Loghashes dokumentieren Grenzen und Messpunkte. Beim Resource-Reload
treten bestehende Modell-/Texturfehler auf; der
[Request an R](../tools/modernized/parallel/machines/requests/R-02-machines-client-assets.json)
hält die vollständige G5-Darstellungsabnahme offen. Keine TPS-Garantie,
Survival- oder Onlineauthentifizierungsabnahme aus diesen isolierten Kreativtests.

Die nach Exit 0 erzeugte Einzelspieler-Weltkopie wurde mit derselben JAR
geladen. Das echte Tankmenü und integrierte Serverabfragen bestätigen erneut
20.000.000 HE, 18.000 mB, 7.000 mB Wasser bei Druck 3 und das unveränderte
Spielerinventar; anschließend regulär gespeichert und zum Titel zurückgekehrt.
Die Kopie erhält nur einen eigenen Weltnamen und aktivierte Prüfkommandos;
die ursprüngliche Serverwelt bleibt unverändert. Die
[Gateakte](../tools/modernized/parallel/machines/evidence/gates.json) hält
bestandene Teilschritte und offene Abnahmen einzeln fest.
