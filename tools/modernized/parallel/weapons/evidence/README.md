# W-01 — geprüfte Waffenlieferung

Basis: `997b15c9d60dd293e9c436663e90a95140ab13af`, Branch `port/weapons`.
Minecraft 1.20.1, Forge **47.4.23**, Build-JDK 21, Mod-/Laufzeit-JDK 17,
Gradle 9.3.1. O/M-Pins und Einzeldateihashes stehen in
[area.json](../area.json) und [rights.json](../rights.json).

## Reproduziert und korrigiert

Der unveränderte Phase-5-Stand besteht alle 14 vorhandenen Regressionen und
verfehlt die zehn neuen erforderlichen Waffentests. Der Korrekturstand besteht
**24/24 required GameTests**. Die Tests rufen die tatsächlichen Architectury-
Handler auf dem Serverthread auf und enthalten gültige Gegenfälle.

| Befund an der Basis | Korrektur / Nachweis |
| --- | --- |
| Raketenbau, Turret, Radar und Soyuz mutieren ohne ihr Menü. | Exakt zugehöriges Menü und aktuelle BlockEntity in derselben Dimension; geladener, zulässiger Zielblock; lebender Nicht-Spectator, Distanz und `mayInteract`. Stale-/Fremdweltzugriff werden geprüft. |
| Radar akzeptiert beliebige Entity-IDs und lädt ungeprüft den Empfängerchunk. | Entity muss serverseitig erfasst, lebendig, endlich und in Reichweite sein; Empfänger muss bereits geladen sein. Koordinaten werden gegen Weltgrenzen geprüft. Ein verknüpfter Bildschirm in Reichweite bleibt ein gültiger Fernzugriff. |
| Decoder akzeptieren ungültige Aktionen, Modi/Slots, unzulässige Koordinaten, übergroße Daten und nichtendliches Detonator-NBT. | Feste Paketgrößen und Aktionsbereiche; der Detonationsbefehl darf nur leeres/null NBT tragen. Er benötigt das tatsächlich gehaltene Serveritem, kein erfundenes Menü. |
| Detonatorziele enthalten keine Dimension und treffen dieselben Koordinaten in einer anderen Welt. | Dimension beim Verknüpfen speichern und vor Auslösung prüfen; alte dimensionslose Punkte bleiben gespeichert, benötigen aber erneutes Verknüpfen. Identische Punkte innerhalb eines Befehls werden dedupliziert. |
| Standardgranate hat keinen Zeitzünder; NBT enthält keinen Zünderstand. | Gewählte O-Referenz Universalgranate/S3: 60 Ticks; Restzeit und Detonationssperre speichern. Echt registriertes Item erzeugt ein Projektil und verbraucht ein Item. Owner bleibt erhalten. |
| Wiedereintritt während der Explosion erzeugt zwei Explosionen; Zusatzschaden hat keinen Owner. | Vor Weltcallbacks gesetzte Detonationssperre; Zusatzschaden verwendet den Projektilbesitzer. Kontrollierter Kollisionswiedereintritt und tatsächliches Schadensereignis sind Bestandteil des Tests. |

Die Granatenprüfung beobachtet das echte Explosionsereignis. Dieses wird in den
kleinen Tests nach der Beobachtung abgebrochen, damit benachbarte Teststrukturen
erhalten bleiben. Der getrennte Produktionslauf unten prüft zusätzlich echten Blockschaden und
die Bedienung durch zwei Clients. Ein eigener Empfänger prüft das Radar-Dispatching; eine
vollständige Raketenflug-/Nutzlastkette bleibt W-05.

## Originalreferenz und Grenzen

O: `ItemGrenadeFuze.FUZE_3S` löst bei `getTimer() >= 60` aus;
`EntityGrenadeUniversal.getTimer()` ist `ticksInAir + ticksInGround`.
Diese ausdrücklich gewählte S3-Konfiguration gilt hier nur als vorläufige
Referenz für M `GrenadeType.STANDARD`. Am O-Pin ist keine direkte Registrierung
dieser einfachen M-Standardgranate zugeordnet. Es gibt keinen O-JDK8-Lauf und
keine Behauptung von Originalparität oder vollständiger Granatenfamilienabnahme.
Andere registrierte Varianten, ihre Nutzlasten und Kollisionsmodi bleiben
erhalten. Insbesondere wird der vom Konstruktor überschriebene Feldinitialwert
in O `ItemGrenade` nicht als Zünderbeleg verwendet.

## Build und Gates

Die korrigierte Produktions-JAR hat SHA256
`08e5283dd4d7c9c9a146fb4e89192d91c2de7d532449944ebc89178273b44c7e`.
Sie wurde **vor** dem Testprofil separat gebaut, geprüft und extern gesichert.
Zwei Datagenläufe ergeben identische 7.952 Ressourcen, Manifest-SHA256
`cc5e858c1c85e6f409141d2a1eaa558731001551b3cabb1182d307a7893c2700`.
Runtime- und Source-JAR enthalten keine Waffen-/Baseline-Testklassen oder
Teststruktur. Die Java-17-Prüfung umfasst auch Architectury 9.2.14 und
MixinConstraints 1.1.0; einziger Mod-Einstieg ist `com.hbm.HbmPort` / `hbm_m`.
Die bestehenden 66 Javadocfehler/100 Warnungen sind weiterhin offene Arbeit.

| Gate | Tatsächlicher Stand |
| --- | --- |
| G1 | Bereichspfade, Herkunft jedes gelieferten Deltas einschließlich Kontext, Pins und frisches Patch-Replay geprüft. Zentrale R-01-Lieferung/Commit fehlt; Integration bleibt blockiert. |
| G2 | Zwei bytegleiche Datagenläufe, getrenntes `build sourcesJar`, Audit und Hash erfolgreich auf 47.4.23. Kein sauberer Javadoc-Nachweis. |
| G3 | 24/24 required Tests, davon 14 unverändert und zehn Waffenprüfungen. |
| G4 | Bestanden: zwei initiale Produktionsstarts mit je 30 Sekunden, Save/Stop und Exit 0; zusätzliche Mehrspieler-/Neustartsitzungen ebenfalls sauber beendet. Neun NBT-/Inventarabfragen nach Neustart identisch. EULA ausdrücklich angenommen. |
| G5 | Fachszenarien und 608 Sekunden ununterbrochene Zweiclientverbindung bestanden. Gesamtgate wegen vorhandener Client-Asset-/Starterfehler und überlappender Detonatorwidgets bei R offen; [konkreter Request](../requests/R-02-runtime-ui.json). |
| G6 | Für die lokalen W-01-Fixtures bestanden: tatsächliches Entladen ohne Force-Loading, zwei Dimensionswechsel/Rückkehr, Transfer nach Reload, Reconnect, Save/Restart und echte Singleplayer-Weltkopie; neun Abfragen an allen vier Ständen identisch. Zünder-/Owner-NBT zusätzlich per GameTest. |
| G7 | Nur die genannte quellgestützte S3-Referenz; Laufzeitvergleich und direkte Variantenzuordnung offen. |
| G8 | Zweistündiger Mischbetrieb erst am gemeinsamen M/N/W/R-Integrationsstand; nicht ausgeführt. |

Die einzige ERROR-Zeile des erfolgreichen GameTest-Laufs ist die bereits
dokumentierte Yggdrasil-Public-Key-Anfrage im isolierten Offlinebetrieb. Sie
bleibt in den externen Rohlogs erhalten. Der bekannte Naval-Mine-Höhenbereich
bleibt eine Warnung im Zuständigkeitsbereich R. Keine allgemeine
Fehlerunterdrückung wurde ergänzt.

## Produktionslauf mit zwei Clients und Lebensdauer

Getestete Codelieferung: `494da12957638953e854cde8d4a8276d27b74d87`;
Patch-/Quellhashes und Produktions-JAR blieben unverändert. Beide echten
Forge-47.4.23-Clients nutzten exakt denselben JAR-Hash wie der Server.
Ununterbrochene gemeinsame Verbindung: **17:36:46–17:46:54 UTC (608 Sekunden)**.
Zwei vorherige unterbrochene Versuche werden nicht als Erfolg gezählt.

| Tatsächliche Aktion | Abgleich mit Serverzustand |
| --- | --- |
| Batterieitem One → Maschine → Two und zurück | Maschineninventar danach leer, genau ein Batterieitem beim erwarteten Spieler; anderer Spieler leer. |
| HE-Netzübertragung | Quelle 20.000.000 → 0 HE, Ziel 0 → 20.000.000 HE. Nach normalem Reload auch Rück- und erneuter Hintransfer ohne Mengenverlust. |
| Zwei echte Wassereimer, Tankmodus und Duct-Netz | 16.000 + 2.000 = 18.000 mB, zwei leere Eimer; Ziel 18.000 mB. Moduspaket von beiden Clients, Transfer nach Reload in beide Richtungen. |
| RBMK-Spalte live hinzufügen/entfernen | Beide Screens aktualisiert. One setzt 0,37 / AZ-5 → 0; Two setzt 0,81 / AZ-5 → 0. Beide ändern Bildschirmtyp. |
| Nahezu gleichzeitiger Raketenbau beider Clients | Klicks 57 ms auseinander; genau eine `missile_micro`, jeder Bestandteil genau einmal verbraucht, Ausgabe verhindert weiteren Bau. |
| Gemeinsame Turret-/Radar-/Soyuzmenüs | Änderungen beider Clients und Anzeigen/Serverwerte stimmen überein. Leerer Soyuz startet nicht. |
| Radarbildschirm 64 Blöcke von der Quelle | Echter verknüpfter Screen bedient Quellradar; zweiter Client hält Quelle normal geladen und sieht Änderung. Kein Force-Loading. |
| Echte Spielergranate | Owner exakt Spieler-UUID; 2 → 1 Item, Restzünder 48 Ticks beobachtet; nach Ablauf kein Projektil. Von 75 Glasblöcken bleiben 55. Rückprall tötet Werfer; Todesmeldung nennt korrekt HBMClientOne als Ursache. |
| Echter Multi-Detonator | Shift-Rechtsklick speichert `Dimension: minecraft:overworld`; leerer echter C2S-Befehl löst gehaltenes Serverziel aus. Wiederholung lässt Ziel entfernt. |
| Ressourcenreload / Reconnect | Beide Clients laden Ressourcen neu und verbinden sich nach Save/Restart erneut; keine Client-Crashdatei. Vorhandene Fehler bleiben unten offen. |

Die Arena bei X≈1024 liegt außerhalb der Spawnchunks. `forceload query`
meldete keine erzwungenen Chunks; nach beiden Netherwechseln bestätigte `unless loaded`
das tatsächliche Entladen. Neun identische Abfragen liegen vor Entladen,
nach Rückkehr, nach Dedicated-Neustart/Reconnect und im integrierten
Singleplayer vor: Batterie 123.456 HE, Netzziel 20.000.000 HE, Tank 18.000 mB,
Raketeninventar, Turret/Radar/Soyuz, RBMK-Sollwert und gehaltenes Detonator-NBT.
Die Weltkopie entstand nach sauberem Stop; alle 54 Dateien waren zunächst
bytegleich. Nur Kopiename und Befehlsfreigabe wurden dort für Abfragen geändert.
Dies ist keine allgemeine Modpack-/Capability- oder Variantenabnahme.

Beide Clientlogs enthalten jeweils 74 ERROR-Zeilen: 68 ungültige Assetpfade,
zweimal fehlendes `nuke_prototype`-Modell, zweimal fehlende `ore_acidizer`-Textur,
ein unzulässiger `simulationDistance:2`-Starterwert und eine Offline-Profil-
Schlüsselanfrage. Keine wurde unterdrückt. Zusätzlich überlappen im
Multi-Detonator bei 854×480 / GUI-Skala 2 der vierte Punkt und „Detonate All“;
der schmale freie Buttonbereich löst korrekt aus. R besitzt diese Screens,
den Starter und die Assets; W hat dort nichts geändert. Der Request beschreibt
konkrete Reproduktion und Abnahme. G5 wird deshalb nicht pauschal grün erklärt.

Rohlogs, Bilder, Clientaktionen und Welten bleiben extern. `checks.json` enthält
nur geprüfte Textwerte, Befehle und SHA256-Nachweise; keine Asset-/Bildbytes.

## Einspielen und Nachweise

Bis R-01 gilt ausschließlich der manuelle Weg aus
`docs/PARALLEL_DEVELOPMENT.md`, Abschnitt 5: **frische externe** Phase-5-Basis
erzeugen, `git apply --check changes.patch`, dann `git apply changes.patch`.
Die zwei Quellen aus dem [R-Request](../requests/R-01-test-profile.json) einzeln
an ihre ausdrücklich genannten, noch nicht vorhandenen Zielpfade kopieren.
Der Helfer gehört nach `src/main/java`, die Testklasse ausschließlich nach
`integration/src/gametest/java`. Keine Register-/Rendereränderung ist nötig.

Alle Datagen-/Build-/GameTestaufrufe müssen `--gradle-arg=-Pdeps.forge=47.4.23`
führen. Für GameTests zusätzlich `--gradle-arg=-Pmodernized.gameTests=true`;
Produktions-JAR zuerst separat bauen/auditieren/sichern. Die 14 bestehenden
Tests bleiben unverändert. Ein frisches vollständiges Basis-Replay hat die
Anwendbarkeit des veröffentlichten Patches und Bytegleichheit aller acht
gepatchten Dateien mit dem getesteten Stand bestätigt.

[checks.json](checks.json) enthält konkrete Fehler vor der Korrektur, Befehle,
Exitcodes, Profil-/Datei-/Loghashes, Paketprüfung und offene Gates. Der erste
Testversuch mit einer fehlerhaften Launchpad-Testfixture ist dort als eigener
Fehlversuch erhalten; er wird nicht als Produktionsfehler ausgegeben.
Ungeprüfte vollständige Quell-/Assetbäume, JARs, Welten und Bilder bleiben extern.
Der PR ist bis zur Erfüllung der offenen Voraussetzungen **Draft**.
