# Build- und Teststatus: Phase 4

Tests: **19. Oktober 2026 (UTC)**; Abschlussprüfung: **20. Oktober 2026**. Lokaler Linux-x86_64-Nachweis am Modernized-Pin `0365cef5956016913095eeeb9366f26c601ca9a0`, mit den unveränderten Phase-3-Korrekturen und der Phase-4-Integration. Minecraft **1.20.1**, Forge **47.4.20**, Mod-ID **`hbm_m`**. **Kein fertiges Release und keine Originalparitätsfreigabe.**

## Ausgeführte Prüfungen

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Ausgangs-/Quellprüfung | `main = c8d2746`, Phase-3-Arbeitsbasis `811b6e8`; geforderte Dokumente gelesen, M-Pin direkt per SHA geladen. |
| Inventur | 12/12 vorhandene Tests mit `HBM_ORIGINAL_SOURCE` auf dem O-Pin erfolgreich; committed Inventar unverändert verifiziert. |
| Schutz vor unkontrolliertem Import | Integration im Zielrepository und bestehender externer Checkout jeweils vor Änderung abgewiesen (erwarteter Exit 1). |
| Erstes Datagen | Exit 0, **8m 39s**, einschließlich frischer Minecraft-Vorbereitung und Downloads. 7.952 Ressourcendateien. |
| Zweites Datagen | Exit 0, **36s**; alle 7.952 Dateien bytegleich, JSON geparst. Manifest-SHA256 **`cc5e858c1c85e6f409141d2a1eaa558731001551b3cabb1182d307a7893c2700`**. |
| Erster Forge-Build | Exit 0, **44s**, `build sourcesJar`; Gradle-`test` meldet `NO-SOURCE`, keine behauptete JUnit-Spielfunktionstestsuite. |
| Frischer Integrationscheckout nach Gemäldekorrektur | Über `integrate_modernized.py` neu vorbereitet; Datagen Exit 0, **1m 11s**, identisches vollständiges Ressourcenmanifest; Build/Sources-JAR Exit 0, **43s**. Gemeinsamer Gradle-/Downloadcache verwendet. |
| Java 17 und Verpackung | Rekursive Klassenheaderprüfung erfolgreich, keine neueren/Preview-Klassen; ein Mod-Einstieg `com/hbm/HbmPort.class`, keine gemeinsam und clientseitig doppelt aufgeführten Mixins. Details unten. |
| Javadoc | **66 Fehler und 100 Warnungen** im ausgeführten normalen Build; Upstream toleriert diese über `isFailOnError=false`. Javadoc ist ausdrücklich keine bestandene Prüfung. |
| Erster isolierter Produktionsserver | Nach EULA-Annahme `Done` nach **63,830s**, weitere **30s** beobachtet, gespeichert und mit Exit 0 gestoppt. **Prüflauf fehlgeschlagen:** fehlende `hbm_m:bober1`-PaintingVariant im placeable-Tag; zusätzliche Mojang-Schlüsselabfrage mit `Connection refused`. Registrierung anschließend ergänzt. |
| Korrigierter Produktionsserver / Neustart | **2/2 Durchläufe bestanden**, jeweils `Done`, **30s** weitere Beobachtung, `save-all flush`, vollständiges Speichern und sauberer Exit **0**. Erster Start **123,647s**, Neustart **68,138s**. Keine unerwartete `ERROR`-/`FATAL`-Zeile; die genau benannte Yggdrasil-Schlüsselabfrage wird separat als Umgebungsfehler protokolliert. |
| GameTests | **3/3 erforderliche Tests bestanden**, Exit **0**, **4m 20s**: Registrierungen/geladene HBM-Rezepte/Gemäldetag, Batterie-NBT mit **5.000.000.123 HE** und Inventar, Batterie in der Serverwelt über **20 Ticks**. |
| Client | **Teilprüfung ausgeführt**, regulärer Exit **0**, Lauf **5m 37s**. Hauptmenü, kreative Superflat-Welt `Phase4IntegrationSmoke` (Seed **42012001**), sichtbare platzierte Batterie und ihr geöffnetes Inventarmenü, Speichern, Rückkehr zum Titel und reguläres Beenden beobachtet. **Keine saubere Darstellungsabnahme:** Asset-/Modell-/Tastenbelegungsfehler bleiben offen. |

## Erzeugtes Evaluationsartefakt

Exakter lokaler Pfad der korrigierten reobfuskierten Mod-JAR:

```text
/workspace/scratch/modernized-phase4/integrated/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-phase4-dev+1.20.1-forge.jar
```

SHA256:

```text
ba2be84cf560bb0eb6f145a4477c4a2098d18fa8c671378fcd081a9f416c64e9
```

Größe: **44.924.417 Bytes**. Im selben Verzeichnis liegen:

| Datei | Bytes / SHA256 |
| --- | --- |
| `hbm_m-0.2.1-phase4-dev+1.20.1-forge-sources.jar` | 41.977.095 / `ac83f5e3726a52435189ae9e97729e6615386e8ab3fb7946285e267729eb5b5c` |
| `hbm_m-0.2.1-phase4-dev+1.20.1-forge-javadoc.jar` | 7.521.764 / `8ee7045ce8f62df70f4a6267dc8b6f3bc82a59b6397e2d020489a28e604078f6` (Javadocfehler siehe oben) |

Die vollständige Reproduktion steht in [INTEGRATION_REPORT.md](INTEGRATION_REPORT.md#reproduktion); Einstieg: `python3 tools/integrate_modernized.py <neuer-externer-checkout>`, danach getrennt `runData` und `build sourcesJar` über `tools/modernized_build.py`. Die lokale Datei wird wegen offener Rechte nicht als Download, Actions-Artefakt oder GitHub-Release veröffentlicht. Dieser temporäre Speicherort ist kein dauerhaft gehostetes Artefakt.

Der geprüfte Produktionsserver liegt unter `/workspace/scratch/modernized-phase4/server-final`; `result.json` bindet beide Läufe an genau den obigen JAR-Hash. Aufruf mit `--accept-eula --allow-offline-auth-failure`, ausschließlich Loopback und Offlineauthentifizierung. Der Tagfehler ist in beiden korrigierten Läufen verschwunden. Der vorherige fehlerhafte Lauf unter `server-verified` bleibt als Fehlerbeleg erhalten.

## Java-/Paketprüfung und Umfang

Das äußere Mod-JAR enthält **1.915 Klassen**, alle mit Major **61**, und genau den einen HBM-`@Mod`-Einstieg `com.hbm.HbmPort`. Die Bytecodeprüfung wurde nach den Laufzeittests am unveränderten JAR-Hash nochmals mit der Verpackungsinventur abgeglichen.

Der Build verwendet Temurin **21.0.12.1+1** für Gradle **9.3.1**, vollständiges Temurin-JDK **17.0.20.1+1** für Kompilierung und Minecraft. Beide JDK-Archive, der Wrapper und der Forge-Installer wurden gegen die dokumentierten SHA256 geprüft; die Gradle-Distribution ist über `distributionSha256Sum` abgesichert. Die aktiven Java-Kompilierungen verwenden `--release 17`.

Im Mod-JAR liegen ausschließlich die zwei erwarteten Jar-in-Jar-Bibliotheken:

| Einbettung | Klassenmajor / SHA256 |
| --- | --- |
| Architectury Forge **9.2.14** | 1×52, 381×60; **`47d5eca3d83aae1ac1d4a70116727715bd7ef4c077d228fee873065cbca94687`** |
| MixinConstraints **1.1.0** | 21×61; **`67e1fca9cb518f8afb356105c7816587e02880c2acca3bbdb6e08c8e967fc1be`** |

Major **61** entspricht Java 17. Klassenheader beweisen keine vollständige API-/Laufzeitabdeckung; die konkreten Starts und GameTests werden separat gemessen. JEI, Create, Flywheel und zusätzliche Entwicklungsclientmods werden nicht in diese JAR eingebettet. Der normale Build enthält weder unsere GameTest-Klasse noch die Teststruktur; keine `.cache`-Einträge oder Minecraft-/Forge-Plattformklassen im äußeren Mod-JAR. GPL-, LGPL- und MIT-Texte sowie Credits/Änderungsvermerk liegen bei. Das Source-JAR ist kein vollständiges Corresponding-Source-Paket.

## Grenzen und Belege

Der Client lief als **Entwicklungsstart `runClient`**, mit Java 17, Xorg-Dummy-Display `:99`, Mesa **25.0.7**, llvmpipe/LLVM **19.1.7** und OpenGL **4.5**. Aufruf mit `DISPLAY=:99 LIBGL_ALWAYS_SOFTWARE=true ALSOFT_DRIVERS=null`, zusätzlich zum normalen Buildhelfer `--gradle-arg=-Dorg.gradle.jvmargs=-Xmx1G`. Die gebaute Produktions-JAR wurde auf dem dedizierten Server geprüft; ein Produktions-JAR-Clientstart wurde nicht ausgeführt. Keine echte Audioausgabe oder Hardware-Grafikprüfung.

Tatsächliche Clientbefunde: Großbuchstaben in SU-47-Texturpfaden werden als ungültige ResourceLocations verworfen; `ore_acidizer.png` ist am M-Pin eine ASCII-Platzhalterdatei, kein PNG. OBJ-Bakes für Radgen, Solidifier und Liquefactor werfen `IndexOutOfBoundsException` und verwenden fehlende Modelle; zusätzliche Modellreferenzen fehlen. Architectury meldet spät registrierte KeyMappings und Shader melden fehlende Uniforms. Die statische Nachprüfung fand **50** unzulässige Pfade unter `assets/`/`data/` und genau **eine** PNG-Datei ohne PNG-Signatur ([Dateiliste/Hash](integration/client-asset-findings.json)). Keine ungeklärten Assets wurden ersetzt oder veröffentlicht; hierfür sind Herkunftsklärung und eigene Darstellungsprüfungen erforderlich. Der erfolgreiche Menü-/Batterietest macht diese Fehler nicht zu bestandenen Tests.

Die vollständigen lokalen Buildbefehle mit UTC, JDK-Pfaden, Exitcodes und Logs liegen unter `/workspace/scratch/modernized-phase4/logs/commands.jsonl`. Die öffentlichen Textbelege und ihre Hashes werden unter `docs/integration/` archiviert. Rohlogs von Fehlversuchen bleiben erhalten; ein `Done` oder Exit 0 allein überschreibt keinen darin enthaltenen Fehlerbefund.

Weitere tatsächliche Meldungen: erste fehlende `server.properties` beim GameTeststart (Settings-`ERROR`, danach Defaultdatei automatisch erzeugt; 3/3 Tests dennoch bestanden). Die Integrationsvorbereitung legt diese Datei nun vor dem ersten Start an; Erstellung und Verweigerung eines bestehenden Laufzeitordners wurden separat geprüft. Vier Deprecation-Warnungen betreffen `ResourceLocation`-Konstruktoren im Testprofil. `UniformHeight: Empty height range: [3 absolute-64 above bottom]` stammt aus der Navalmine-Strukturkonfiguration und bleibt ein offener Weltgenbefund. Unter paralleler Weltgenerierungs-/Buildlast traten einzelne `Can't keep up`-Warnungen auf; keine Last-/TPS-Abnahme. Standardwarnungen zu anfänglich korrigierten Forge-Konfigurationen, `mods.toml` in Forge-Sprachprovidern und Entwicklungs-Refmaps sind in den Rohlogs erhalten.

Keine Windowsprüfung, kein Original-1.7.10-Build, keine vollständige Maschinen-/Reaktor-/Netzwerk-/Progressionsabnahme und kein authentifizierter Mehrspielertest. Die aktuelle [Feature-Matrix](FEATURE_MATRIX.md) bleibt unverändert. Weitere offene Punkte: [REMAINING_ISSUES.md](REMAINING_ISSUES.md).
