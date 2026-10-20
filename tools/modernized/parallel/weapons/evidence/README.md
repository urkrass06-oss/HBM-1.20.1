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
erhalten bleiben. Das ist **kein** Nachweis von Produktions-Blockschaden oder
Clientdarstellung. Ein eigener Empfänger prüft das Radar-Dispatching; eine
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
| G4 | Zwei Produktionsstarts mit je 30 Sekunden, Save/Stop und Exit 0 bestanden. EULA ausdrücklich vom Nutzer angenommen. Arena-NBT-Abgleich nach Neustart noch in Arbeit. |
| G5 | Zwei echte Clients mit identischem Produktionshash beigetreten. Umgebung unterbrach den ersten Lauf vor zehn Minuten; separater Folgelauf in Arbeit. Keine vollständige G5-Abnahme behauptet. |
| G6 | NBT-Roundtrip geprüft. Normaler Chunkreload, echter Reconnect/Dimensionswechsel, Produktionsneustart und Singleplayer-Weltkopie offen. |
| G7 | Nur die genannte quellgestützte S3-Referenz; Laufzeitvergleich und direkte Variantenzuordnung offen. |
| G8 | Zweistündiger Mischbetrieb erst am gemeinsamen M/N/W/R-Integrationsstand; nicht ausgeführt. |

Die einzige ERROR-Zeile des erfolgreichen GameTest-Laufs ist die bereits
dokumentierte Yggdrasil-Public-Key-Anfrage im isolierten Offlinebetrieb. Sie
bleibt in den externen Rohlogs erhalten. Der bekannte Naval-Mine-Höhenbereich
bleibt eine Warnung im Zuständigkeitsbereich R. Keine allgemeine
Fehlerunterdrückung wurde ergänzt.

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
