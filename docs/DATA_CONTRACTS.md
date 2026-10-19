# Datenverträge für das Forge-Grundgerüst

Stand: **19. Oktober 2026, Spezifikationsentwurf für P1**. Dieses Dokument definiert Regeln für spätere Implementierungen. Es implementiert keine Registry-Zuordnung, Speicherformate, Capabilities, Netzwerknachrichten, Maschinen oder Konverter. Ein startendes Grundgerüst belegt keine dieser Funktionen. Maßgeblich bleiben der [Portierungsplan](PORTING_PLAN.md), die [Feature-Matrix](FEATURE_MATRIX.md) und das unverändert untersuchte Original am Commit [`aee05a40f10fb7bb9b042b65eccaa449ecc1672d`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/tree/aee05a40f10fb7bb9b042b65eccaa449ecc1672d).

Das Ziel ist Minecraft 1.20.1 mit Forge und Java 17. Dieser Rahmen macht **keine Zusage zum Import von 1.7.10-Spielständen**. Alte Namen und NBT-Beispiele dienen dem Nachweis des Originalverhaltens; sie sind noch kein ausführbarer Konverter.

## Identitäten und Varianten

Die Mod-ID und der vorgesehene Zielnamensraum sind `hbm`. Eine moderne Identität besteht aus **Registry-Art und ResourceLocation**; identische Namen in Block- und Itemregistry sind dadurch unterscheidbar. Java-Feldnamen, Klassennamen, Übersetzungsschlüssel, Ressourcenpfade und numerische Laufzeit-IDs sind keine austauschbaren Identitäten.

Das ist im Original besonders relevant: [`ModBlocks.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/blocks/ModBlocks.java#L3530-L3535) und [`ModItems.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/items/ModItems.java) übergeben vielfach `getUnlocalizedName()` an `GameRegistry`. Die tatsächlichen alten Registrierungsnamen müssen deshalb nachgewiesen werden; ein aus dem Feldnamen abgeleiteter Name allein genügt nicht. Präfixe wie `tile.`/`item.`, Großschreibung oder historische Schreibfehler werden bei der Inventur nicht stillschweigend entfernt.

Jede spätere Einzelzuordnung erhält mindestens folgende Angaben:

| Feld | Bedeutung |
| --- | --- |
| Originalbeleg | Vollständiger Quellcommit, Pfad und Registrierungspfad; Laufzeitbeleg ergänzen, sobald verfügbar |
| Originalidentität | Registry-Art und nachgewiesener Originalname; Java-Symbol separat aufführen |
| Variante | Bedeutung von Metadaten/Damage und relevantem Item-/Tile-NBT; nicht pauschal als Untertyp behandeln |
| Erreichbarkeit | Registriert und erreichbar, konfigurationsabhängig, historischer Alias oder nur vorhandene Definition; Ungeprüft bleibt ausdrücklich offen |
| Zielidentität | Zielregistry und gültige `hbm:…`-ResourceLocation oder ausdrücklich noch offen |
| Zielzustand | BlockState-Eigenschaften, getrennte Item-/Block-ID oder NBT-Felder mit eindeutiger Zuordnung |
| Nachweis | Matrix-ID, betroffene Rezepte/Assets und Prüffall für Platzierung, Stackidentität, Drops und Speichern |

Metadaten werden pro Inhalt aufgelöst: Orientierung gehört gegebenenfalls in einen BlockState, unterschiedliche Materialien gegebenenfalls in getrennte IDs, Werkzeugverschleiß in Haltbarkeit. Diese Beispiele sind keine automatische Regel für alle Originalklassen. Mehrere Originalvarianten dürfen erst zusammengelegt werden, wenn ihr Verhalten, ihre Rezepte und ihre gespeicherten Daten nachweislich gleichwertig bleiben. Erforderliche Namensanpassungen für moderne ResourceLocations werden explizit dokumentiert.

Historische Tile-Aliase aus [`TileMappings.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/tileentity/TileMappings.java) und Entitätsnamen aus [`EntityMappings.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/entity/EntityMappings.java) werden getrennt erfasst. Ein späterer Missing-Mappings-Handler kann Namensänderungen innerhalb unterstützter Portversionen behandeln; daraus folgt keine Kompatibilität der alten Welt-, Block-, Entity- oder NBT-Formate. Numerische Registrierungsnummern werden nicht als dauerhafte Identitäten übernommen.

## NBT und Lebensdauer

Für jeden künftig persistenten Typ wird vor seiner Implementierung festgelegt: Eigentümer der Daten, Feldnamen, NBT-Typen, Einheiten, Wertebereiche, Standard bei fehlenden Feldern, Versionswechsel und Synchronisationsbedarf. Vanilla-eigene Schlüssel wie `id`, `x`, `y`, `z` und `DataVersion` behalten ihre Plattformbedeutung.

Für neu entworfene eigene Daten ist ein eigener Compound mit einem ganzzahligen Schemafeld vorgesehen; konkrete Namen und erste Versionsnummer werden mit dem ersten tatsächlich implementierten Typ festgelegt. Eine Modversion und eine NBT-Schemaversion sind unterschiedliche Angaben. Wo ein Originalschlüssel erhalten wird, werden sein Originaltyp und seine Bedeutung dokumentiert, bevor eine neue Struktur eingeführt wird.

| Datenträger | Geplanter Vertrag |
| --- | --- |
| BlockEntity | Dauerzustand über `saveAdditional`/`load`; Änderungen markieren den Zustand zum Speichern. Anschlusscache, Netzreferenzen und Clientdarstellung werden aus diesem Zustand abgeleitet. |
| Weltweiter Zustand | Eigene `SavedData` mit geklärter Dimension und Lebensdauer; keine unkontrollierten statischen Weltdaten. |
| Entity-/Spielerzustand | Geeignete persistente Daten/Capabilities mit expliziten Regeln für Speichern, Tod, Respawn, Klonen und Dimensionswechsel. |
| ItemStack | Identitätsrelevantes NBT, Haltbarkeit und Stapelregeln gemeinsam spezifizieren; kein Verlust beim Crafting, Teilen oder Automatisieren. |
| Clientansicht | Nur benötigte freigegebene Projektion des Serverzustands; Synchronisationsdaten sind nicht automatisch das vollständige Speicherformat. |

Fehlende Felder erhalten nur dokumentierte Defaults. Falsche NBT-Typen, ungültige IDs und nicht unterstützte zukünftige Schemaversionen dürfen nicht unbemerkt zu scheinbar gültigen leeren Maschinen oder anderen Stoffen werden. Die konkrete Fehlerbehandlung wird pro Typ festgelegt und muss Diagnose sowie Schutz vor stiller Datenüberschreibung berücksichtigen. Migrationen gelten nur zwischen ausdrücklich unterstützten **Portschemata** und müssen wiederholbar geprüft werden. Ein Schemafeld allein implementiert keine Migration.

Laden und Synchronisieren dürfen keine Energie, Items oder Fluids erzeugen. In Capabilities veröffentlichte Ansichten benötigen eine definierte Seite und Lebensdauer; bei Entfernung oder Entladen werden zugehörige `LazyOptional`-Referenzen invalidiert. Dynamische Netzzugehörigkeit wird aus geladenen, gültigen Anschlüssen rekonstruiert, soweit der spätere Originalvergleich keine zusätzliche persistente Information erfordert.

## Energie, Fluids und Zeiteinheiten

HBM-Energie bleibt ein eigenes Modell. [`PowerNetMK2.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/api/hbm/energymk2/PowerNetMK2.java) verwendet `long` für Energie und Verteilung. Ein späteres HE-Datenmodell muss gültige Originalwerte ohne Verengung auf `int` speichern, synchronisieren und anzeigen. Ein Zahlenfeld namens `power` begründet noch keine physikalische Watt-Einheit; Menge und Durchsatz werden pro Originalvertrag unterschieden.

| Größe | Beobachtete Originalgrenze | Regel für den Portentwurf |
| --- | --- | --- |
| Energie | HE-Mengen und Netzsummen als `long` | `long` erhalten; gültige Bereiche und eventuelle Sonderwerte je Typ belegen. Zwischenrechnungen, Addition und Konvertierung gegen Überlauf prüfen. |
| Außenadapter | CoFH/RF-Speicher und API verwenden `int` | Forge Energy ist ein begrenzter Außenadapter, kein Ersatz des HE-Modells. Simulation verändert keinen Zustand; zugesagte und tatsächlich übertragene Mengen müssen übereinstimmen. |
| HE → RF | Standard `heInput=5`, `rfOutput=1` | **5 HE → 1 RF** ist eine richtungsabhängige Originalvorgabe, keine allgemeine Gleichsetzung von HE mit FE. |
| RF → HE | Standard `rfInput=2`, `heOutput=5` | **2 RF → 5 HE** separat erhalten; keine symmetrische Gegenrate erfinden. |
| Fluidmenge | Tankfüllung/-kapazität als `int`, Netzsummen/-bedarf als `long` | Gültige Tankgrenzen und weite Netzberechnungen erhalten; keine stillen Casts oder Mengenverluste im Adapter. |
| Fluididentität | Eigene `FluidType`-ID und Namen | Stabile eigene Zuordnung aus Typ, Eigenschaften und Varianten; numerische Original-ID ist ein Herkunftsmerkmal, keine globale Forge-Fluid-ID. |
| Fluiddruck | Eigener ganzzahliger Druck, im MK2-Vertrag Druckstufen 0 bis 5 | Druck bleibt Teil der Identität eines Fluidzustands/Transfers; weder aus Temperatur ableiten noch beim Forge-Adapter entfernen. Keine ungeprüfte Umdeutung in bar/Pascal. |
| Verarbeitungszeit | Originalfelder und Tickabläufe sind je Maschine zu untersuchen | Prozesskosten und Raten auf dokumentierte Serverticks beziehen; reale Sekunden oder Clientframes ersetzen die Originalbasis nicht. |

Die Konverterdefaults stehen in [`TileEntityConverterHeRf.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/tileentity/network/TileEntityConverterHeRf.java#L27-L31) und [`TileEntityConverterRfHe.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/tileentity/network/TileEntityConverterRfHe.java#L21-L25). Beide sind konfigurierbar und haben eigene Integer-Reihenfolgen, Pufferspeicher und Verlustparameter. Eine spätere Implementierung muss diese Regeln einschließlich Restmengen erfassen. Die RF-Vorgaben allein legen keine neue automatische FE-Konvertierung fest. Bei einem zukünftigen FE-Adapter werden technische Abbildung und Auswirkungen ausdrücklich dokumentiert.

[`FluidTank.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/inventory/fluid/tank/FluidTank.java#L257-L291) schreibt unter einem tankabhängigen Präfix `s` die Menge `s`, Kapazität `s_max`, Typ `s_type` jeweils als Integer und Druck `s_p` als Short. Der Leser enthält außerdem eine historische Namenskompatibilität für den Typ. Das ist ein konkretes Originalbeispiel, kein allgemeines Schema aller Tanks. [`IFluidUserMK2.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/api/hbm/fluidmk2/IFluidUserMK2.java) und [`FluidNetMK2.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/api/hbm/fluidmk2/FluidNetMK2.java) belegen die getrennte Druckbehandlung.

Die Original-Tankanzeige verwendet `mB`; daraus folgt noch keine geprüfte Austauschbarkeit sämtlicher HBM-Stoffe und Druckstufen mit Forge-`FluidStack`. Pro Außenadapter sind Stoffzuordnung, Mengenverhältnis, zulässiger Druck, Rundung, Restmengen und Ablehnung nicht darstellbarer Zustände zu spezifizieren. Ohne belegte Abbildung erfolgt keine verlustbehaftete Normalisierung.

## Seiten, Threads und Autorität

Physische Distribution (`CLIENT`/Dedicated Server), logische Seite (Client/Server) und Anschlussrichtung eines Blocks sind getrennte Begriffe. Minecraft-Clientklassen dürfen nicht als statische Abhängigkeiten gemeinsam geladener Klassen benötigt werden. Clientregistrierungen erfolgen über passende clientseitige Forge-Einstiegspunkte; der integrierte Server bleibt eine logische Serverseite.

| Vorgang | Zuständigkeit |
| --- | --- |
| Inventar, Prozesse, Energie, Fluidtransfer, Dosis, Schaden und Weltänderungen | Logischer Server; Prüfung vor einer Zustandsänderung |
| Rendering, Audio und Eingabeerfassung | Physischer Client; Anzeige erhält freigegebene Zustandsdaten |
| Clientbedienung | Client sendet eine fachliche Anfrage; der Server bestimmt das zulässige Ergebnis |
| Netzwerkempfang | Dekodieren mit Grenzen; Welt-/Entity-/Menüzugriffe auf dem zuständigen Hauptthread |
| Ausgelagerte Berechnung | Nur geeignete Datenkopien; Anwendung eines Ergebnisses prüft die weiterhin gültige Welt-/Objektzuordnung auf dem Serverthread |
| Seitliche Automation | Anschlussrichtung aus Originalorientierung und Portdefinition ableiten; `null`-Seite, interne Aufrufe und externe Automatisierung ausdrücklich behandeln |

Ein Client darf keine gespeicherten ItemStacks, HE-Mengen oder Maschinen-NBT als verbindliches Ergebnis setzen. Eine Serveranfrage benötigt einen gültigen Absender, den passenden Menü-/Objektbezug, Dimension, Reichweite und Rechte sowie begrenzte Parameter. Das konkrete Rechtssystem bleibt Sache der jeweiligen Originalfunktion.

## Protokoll und Synchronisation

Das Original registriert Nachrichten über [`PacketDispatcher.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/packet/PacketDispatcher.java) und einen eigenen [`NetworkHandler.java`](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/blob/aee05a40f10fb7bb9b042b65eccaa449ecc1672d/src/main/java/com/hbm/main/NetworkHandler.java). Dessen Registrierungsreihenfolge und generische NBT-Pakete sind kein zu übernehmendes binärkompatibles Protokoll. Ein 1.7.10-Client kann nicht mit dem Forge-1.20.1-Port verbunden werden.

Für spätere eigene Nachrichten ist Forge-1.20.1-`SimpleChannel` vorgesehen. Vor der ersten Nachricht werden Kanalname, Protokollversion und explizite Nachrichtentabelle versioniert. Protokollversion und NBT-Schemaversion bleiben unabhängig. Kompatibilität wird ausdrücklich angegeben; eine pauschale Annahme aller Versionen ist kein zulässiger Standard.

Jeder Nachrichteneintrag benötigt Richtung, Kennung, Felder/Typen, maximale Größen, Objektbezug, Empfangsthread, Berechtigung und fachliche Wirkung. Kennungen werden nicht durch eine später veränderte Klassenreihenfolge umnummeriert. Ungültige Nachrichtentypen, zu große Sammlungen/Strings/NBT und unbekannte Pflicht-IDs dürfen keine unbeschränkte Verarbeitung oder Weltänderung auslösen.

Serverzustand wird nach Bedarf beim Öffnen eines Menüs, Beginn des Entity-/Chunktrackings und anschließend durch begrenzte Änderungen synchronisiert. Ziele, Sichtbarkeit und Dimension müssen passen. Persistente Daten werden nicht allein durch flüchtige Effektnachrichten beschrieben. Ein vollständiger Zustand und ein Delta benötigen eine eindeutig festgelegte Bedeutung; veraltete Updates dürfen keine neue Objektinstanz am selben Ort verändern. Die technische Lösung dafür wird pro Familie festgelegt.

Das Grundgerüst darf ohne eigene Spielfunktionsnachrichten auskommen. Diese Spezifikation verlangt weder einen ungenutzten Kanal noch generische NBT-Schreibpakete als Platzhalter.

## Nachweise vor Umsetzung einer Funktionsfamilie

Die folgenden Prüfungen sind **Anforderungen an spätere Implementierungen**, keine in P1 bereits ausgeführten Tests:

- Originalname, Registry-Art und Varianten sind belegt; eine Java-Feldliste wird nicht als vollständige Laufzeitregistrierung ausgegeben.
- Speicher-Roundtrip erhält zulässige Zustände einschließlich großer HE-Werte, Fluidtyp/-druck und inventarrelevanter Daten. Fehlende, falsche und zukünftige Daten haben eine dokumentierte Behandlung.
- Adaptertests behandeln `int`-/`long`-Grenzen, Simulationsaufrufe, Rundung, Teilübertragung und die beiden verschiedenen Originalkonverterraten. Konfigurierte und beabsichtigte Verluste werden von Fehlern unterschieden.
- Chunkentladung, erneutes Laden, Entfernung und Seitenwechsel erzeugen keine duplizierten Inventare, ungültigen Capability-Zugriffe oder verwaisten Netze.
- Dedicated Server lädt keine Clientklassen; Multiplayerbedienung verändert nur serverseitig berechtigte Zustände und überträgt vollständige benötigte Anzeigen.

Offen bleiben die vollständige ID-/Varianteninventur, konkrete per-Typ-NBT-Schemata, erste Nachrichtentabelle, alle Einheiten-/Adapterzuordnungen und numerische Originalvergleichswerte. Ihre Dokumentation und Umsetzung erfolgen mit den zugehörigen Matrix-IDs; das Vorliegen dieses Entwurfs setzt keinen Featurestatus auf „Implementiert“ oder „Verifiziert“.
