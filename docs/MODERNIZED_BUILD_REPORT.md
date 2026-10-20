# Modernized-Buildvorbereitung: Phase 3

Stand: **19. Oktober 2026 (UTC)**. Ziel ist eine reproduzierbare technische Grundlage für **Minecraft 1.20.1 / Forge 47.4.20**, mit **JDK 21 für Gradle** und **Java 17 für Mod und Minecraft**. Der isolierte Nachweis behält Mod-ID und Namensraum `hbm_m` bei.

**Ergebnis: Forge-Build, Datengenerierung und Java-17-Bytecodeprüfung sind erfolgreich.** Der Dedicated-Server-Aufruf erreicht nach einer behobenen Mixin-Verpackungskorrektur die ausstehende Minecraft-EULA-Annahme; **kein Start bis `Done`, keine Testwelt und keine Spielbarkeitsfreigabe**. Einzelassetrechte, vollständige Bibliotheks-Notices und weitere Laufzeitabnahmen bleiben offen.

## 1. Feste Quellen und Arbeitsverzeichnisse

| Rolle | Festgehaltener Stand |
| --- | --- |
| Modernized | [Raptor324/HBM-Modernized @ 0365cef5956016913095eeeb9366f26c601ca9a0](https://github.com/Raptor324/HBM-Modernized/tree/0365cef5956016913095eeeb9366f26c601ca9a0), exakt der Pin aus [MODERNIZED_COMPARISON.md](MODERNIZED_COMPARISON.md). |
| Original | [HbmMods/Hbm-s-Nuclear-Tech-GIT @ aee05a40f10fb7bb9b042b65eccaa449ecc1672d](https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT/tree/aee05a40f10fb7bb9b042b65eccaa449ecc1672d), unverändert fachliche Referenz; kein Originalbuild in dieser Phase. |
| Zielbasis | `de4bb82c477fb36ad49eeacfd0a9e65abac668c1`, `docs/original-porting-plan`, nach Merge von PR #3. `main` enthält weiterhin nur die initiale README; deshalb baut dieser PR auf dem Entwicklungsbranch auf. |
| Zielcheckout | `/workspace/HBM-1.20.1`, neuer Branch `build/modernized-phase3`. |
| Separater Analyse-/Buildcheckout | `/workspace/scratch/modernized-phase3/upstream`, detached HEAD am M-Pin. |
| Frische Reproduktionscheckouts | `/workspace/scratch/modernized-phase3/replay` für die erste Patchfassung; `replay-final` für Sortierung/Lizenzbeilage; `replay-verified` für die abschließende Mixin-Verpackungskorrektur, jeweils unter demselben externen Arbeitsverzeichnis und mit detached HEAD am M-Pin. |
| JDKs, Cache, vollständige lokale Logs | Unter `/workspace/scratch/modernized-phase3/`; außerhalb des Zielrepositorys. Diese lokalen Dateien sind keine dauerhaft gehosteten Releaseartefakte. |

Bestehende Projektdateien, Spielfunktionsstatus, Lizenzen und Foundation-Build bleiben erhalten. Der neue Helfer lädt ausschließlich in ein externes Verzeichnis. Es werden keine vollständigen fremden Quellcode-/Assetdateien, JDKs, Gradle-Binaries, Minecraft-Dateien oder JARs in das öffentliche Zielrepository kopiert. Die kleinen Buildänderungen und eine Generatorzeile sind als [Textpatch](../tools/modernized/forge-1.20.1.patch) enthalten.

## 2. Tatsächliche Umgebung

Linux x86_64, Kernel `6.18.55`, Python 3.12; kein grafischer Clienttest. Die Maschine meldet rund 9,7 GiB RAM, das Containerlimit beträgt **8 GiB** (`/sys/fs/cgroup/memory.max = 8589934592`), kein Swap. Das Dateisystem hatte zu Beginn etwa 30 GiB frei. Gradle wird mit höchstens zwei Workern aufgerufen.

Die aktuelle Cloud-Netzwerkpolicy war `unrestricted` / `enforced`, ohne VPN, zusätzliche Secretbindungen oder Outbound-Identitäten. HTTP/HTTPS müssen trotzdem über den geerbten Sidecarproxy laufen. Die Diagnose las `/etc/codex/network-policy.json` und den aktuellen Cloud-Umgebungsstatus; keine Zugangsdaten wurden in die Dokumentation übernommen. TLS-Prüfung blieb aktiv. Die Java-Prozesse verwendeten den vorhandenen CA-Truststore `/etc/ssl/certs/java/cacerts`.

| Bestandteil | Tatsächlich verwendet / geprüft |
| --- | --- |
| Vorinstalliertes Java | Debian OpenJDK Runtime `21.0.12.1+1-1-deb13u1-Debian`; **nur JRE**, kein `bin/javac`. |
| Build-JDK | Eclipse Temurin **21.0.12.1+1**, vollständiges JDK, extern entpackt. |
| Mod-/Minecraft-JDK | Eclipse Temurin **17.0.20.1+1**, vollständiges JDK, extern entpackt. |
| Gradle | Wrapperdistribution **9.3.1**, kein systemweit installiertes Gradle erforderlich. |
| Aktive Zielplattform | Minecraft **1.20.1**, Forge **47.4.20**, Parchment **1.20.1:2023.09.03**. |
| Direkte Buildpins | Stonecutter `0.8`, LegacyForge ModDev `2.0.120`, Kotlin `2.2.10`, KSP `2.2.10-2.0.2`, Fletching Table `0.1.0-alpha.22`, Postprocess `2.1-beta.8`, Mixin-Processor `0.8.5`. |

### Downloads und Prüfsummen

| Download | SHA256 |
| --- | --- |
| [Temurin 21, Linux x64 JDK](https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz) | `ce79869e1307ed8ee1e2baa86a412b1eb5b75d10a01006d788a6f968bcfaee94` |
| [Temurin 17, Linux x64 JDK](https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.20.1%2B1/OpenJDK17U-jdk_x64_linux_hotspot_17.0.20.1_1.tar.gz) | `3808d1d15e3ec6bd5b84057fb5d84c33d8a1536a258146bcea2e603fc726e08e` |
| [Gradle 9.3.1 bin](https://services.gradle.org/distributions/gradle-9.3.1-bin.zip) | `b266d5ff6b90eada6dc3b20cb090e3731302e553a27c5d3e4df1f0d76beaff06` |
| [Offizielles Gradle-9.3.1-Wrapper-JAR](https://raw.githubusercontent.com/gradle/gradle/v9.3.1/gradle/wrapper/gradle-wrapper.jar) | `b3a875ddc1f044746e1b1a55f645584505f4a10438c1afea9f15e92a7c42ec13` |
| Ursprüngliches M-Wrapper-JAR am Pin | `423cb469ccc0ecc31f0e4e1c309976198ccb734cdcbb7029d4bda0f18f57e8d9`; unterscheidet sich vom offiziellen Wrapper-JAR für 9.3.1. Dieser Befund behauptet keine Beschädigung. |

Die JDK-Metadaten wurden über Adoptiums API für Java 17/21 bezogen, die Archive danach gegen die dort genannten SHA256-Werte geprüft. Für die Reproduktion gelten die festen URLs/Hashes in dieser Tabelle. Gradles veröffentlichte `gradle-9.3.1-bin.zip.sha256` und `gradle-9.3.1-wrapper.jar.sha256` wurden ebenfalls abgerufen. Der Helfer prüft das Wrapper-JAR vor dem Schreiben; der Patch aktiviert die Wrapper-Prüfung der Distribution über `distributionSha256Sum`. Weil die erste Distribution vor Ergänzung dieser Property geladen wurde, wurde sie zusätzlich separat per `curl` heruntergeladen und gehasht: Alle **314 Dateien** der tatsächlich benutzten entpackten Gradle-Distribution stimmen bytegenau mit dem SHA256-geprüften Archiv überein (Exit **0**).

## 3. Belegte Ausgangsfehler und Behebung

### A. Java-Wrapper verwendet den Umgebungsproxy nicht automatisch

Ausgeführt im unveränderten externen Checkout:

```bash
timeout 60 ./gradlew --no-daemon --version
```

Exit **1**, beim Distributiondownload:

```text
Downloading https://services.gradle.org/distributions/gradle-9.3.1-bin.zip
Exception in thread "main" java.net.ConnectException: Connection refused
```

Mit expliziten `http.proxyHost`, `http.proxyPort`, `https.proxyHost`, `https.proxyPort` und dem vorhandenen CA-Truststore wurde Gradle heruntergeladen. Der neue Helfer übersetzt die geerbten HTTP-Proxyadressen in JVM-Optionen und gibt sie über `JAVA_TOOL_OPTIONS` auch an geforkte Werkzeug-JVMs weiter. Er speichert keine Proxywerte in öffentlichen Gradle-Dateien und deaktiviert keine Zertifikatsprüfung.

### B. Java-21-Daemonkriterium findet kein vollständiges JDK

Ausgeführt nach erfolgreichem Wrapperdownload, zunächst weiterhin mit der vorinstallierten Java-21-Runtime:

```bash
# Jeweils mit expliziten Java-Proxyparametern und JAVA_HOME auf die Debian-Runtime:
./gradlew --no-daemon --console=plain --max-workers=2 :1.20.1-forge:help --stacktrace
./gradlew --no-daemon --console=plain --max-workers=2 \
  -Dorg.gradle.java.installations.paths=/usr/lib/jvm/java-21-openjdk-amd64 \
  :1.20.1-forge:help --info
./gradlew --no-daemon --console=plain --max-workers=2 \
  -Porg.gradle.java.installations.paths=/usr/lib/jvm/java-21-openjdk-amd64 \
  -Porg.gradle.java.installations.auto-download=false :1.20.1-forge:help --info
```

Die ersten beiden Versuche endeten mit Exit **1**:

```text
Unable to download toolchain matching the requirements ({languageVersion=21, ...})
from 'null', due to: No defined toolchain download url for LINUX on x86_64 architecture.
```

Mit deaktiviertem Autodownload lautete der Fehler:

```text
Cannot find a Java installation on your machine ... matching: {languageVersion=21, ...}.
Toolchain auto-provisioning is not enabled.
```

`java -version` allein reichte als Diagnose nicht: `ls` und der direkte Aufruf von `/usr/lib/jvm/java-21-openjdk-amd64/bin/javac -version` belegten, dass dort **kein javac** existiert (Shell-Exit **127**). Gradles `--info` erkannte die Runtime, aber keine passende vollständige Toolchain. Ein expliziter Pfad ergänzt keinen fehlenden Compiler. Das Daemonkriterienfile enthält keine Download-URL; der Foojay-Resolver aus den Projekteinstellungen löst diesen vorgelagerten Start nicht automatisch.

**Behebung:** vollständiges JDK 21 bereitgestellt, `JAVA_HOME` darauf gesetzt; vollständiges JDK 17 separat über `JAVA17_HOME` ausgewählt. Das portable Daemonkriterium `toolchainVersion=21` bleibt erhalten. Es wurde kein vermeintlicher Quellcodefehler durch Absenken der Build-JVM auf Java 17 umgangen.

### C. Portable Konfiguration und Begrenzung auf Forge

Alle Anpassungen am temporären Checkout sind im [Patch](../tools/modernized/forge-1.20.1.patch) und im [Helfer](../tools/modernized_build.py) nachvollziehbar:

| Datei in M | Änderung und Zweck |
| --- | --- |
| `settings.gradle.kts` | Nur `1.20.1-forge` aktiv; NeoForge-1.21.1-Projekt deaktiviert. Inaktive Upstreamdateien bleiben erhalten. |
| `versions/1.20.1-forge/gradle.properties` | Fest eingebauten Windows-JDK-Pfad entfernt; JDK-Auswahl erfolgt extern über Umgebungsvariablen und Gradle-Toolchains. |
| `build-logic/src/main/kotlin/ModPlatformPlugin.kt` | Java-Toolchain aus der für die Minecraft-Version ermittelten Java-Anforderung auswählen; `JavaCompile.options.release` zusätzlich setzen. Für 1.20.1 resultiert **17**, einschließlich API-Schranke. |
| `settings.gradle.kts`, `build-logic/build.gradle.kts`, `build.forge.gradle.kts` | `mavenLocal()` entfernt, damit lokale unveröffentlichte Artefakte nicht das Ergebnis verändern. |
| `stonecutter.gradle.kts` | Unbenutzte Fabric-Loom-Pluginauflösung entfernt. Der unbenutzte Snapshot-Katalogeintrag bleibt inaktiv; kein Fabric-Build behauptet. |
| `build.forge.gradle.kts` | Zusätzliche `modRuntimeOnly`-Entwicklungshilfen einschließlich JEI-Runtime nur mit `-Pmodernized.devRuntime=true` aktiv. Compile-only-Integrationen, Architectury und MixinConstraints bleiben bestehen. Vorhandenen M-Root-Lizenztext als `LICENSE.hbm_m` allen Archiven beilegen; reproduzierbare Dateireihenfolge und keine Dateizeitstempel im Archiv explizit konfigurieren. Im `processResources`-Ergebnis bereits client-/serverseitig deklarierte Mixins aus der gemeinsamen Liste entfernen, nachdem Fletching Table sie dort zusätzlich eingetragen hat. |
| `src/main/java/com/hbm_m/datagen/assets/ModItemModelProvider.java` | Modellteilnamen vor der JSON-Erzeugung sortieren. Der zweite Datagenlauf belegte eine wechselnde Arrayreihenfolge aus `Set.of(...)` für `missile_shuttle.json`; eine Generatorzeile behebt die Ursache. |
| `gradle/wrapper/gradle-wrapper.properties` | SHA256 für die festgelegte 9.3.1-Distribution ergänzt. |
| `gradle/wrapper/gradle-wrapper.jar` | Nur im externen Checkout durch das offizielle, SHA256-geprüfte 9.3.1-Wrapper-JAR ersetzt; der Helfer reproduziert dies ohne Binärdatei im Zielrepository. |

Mod-IDs, Copyright-/Lizenzhinweise, Spielmechaniken und handgepflegte Assets bleiben unverändert. Datagen erzeugt im externen Checkout Ressourcen neu und aktualisiert auch die zwei bereits getrackten generierten Sprachdateien; diese Ausgaben sind kein Teil des Patches. Die Buildlogik-/Generatorausschnitte im Patch stammen aus M und bleiben dessen GPLv3-Bestand zugeordnet; die eigenständig geschriebenen Python-Helfer tragen LGPL-3.0-only wie die bestehenden Werkzeuge. Die vorhandenen Lizenzdateien werden nicht ersetzt.

Endgültiger Patch: **10.014 Bytes**, SHA256 **`ff9bf74fde827a9a5362c196795f7fa849ed26475c3297b73ca8d7cd4f489be4`**. Er verändert acht Textdateien; das extern heruntergeladene Wrapper-JAR ist die neunte veränderte Datei. Die Reproduktionscheckouts wurden mit `prepare` erzeugt und die veränderten Dateien gegen den Analysecheckout verglichen. Frühere Fassungen und ihre Ergebnisse bleiben im Befehlsprotokoll nachvollziehbar; nur die endgültige Patchfassung liegt im PR. Der abschließende Archivfilter schließt außerdem `.cache`-Dateien aus allen JAR-Aufgaben aus, nachdem die Archivprüfung elf Cacheeinträge im Sources-JAR fand.

## 4. Ausgeführte Prüfungen und Ergebnisse

Alle folgenden Ergebnisse stammen aus tatsächlich ausgeführten Aufrufen am M-Pin. Gradle `test` meldet **`NO-SOURCE`**; ein erfolgreicher Build bedeutet hier keine bestandene Spielfunktionstestsuite.

### Datengenerierung und Wiederholbarkeit

1. Erster `:1.20.1-forge:runData`: Exit **0**, `BUILD SUCCESSFUL in 7m 17s`. Stonecutter, KSP, Java-Kompilierung mit JDK17 und alle zehn Datagenprovider liefen. Der erste Lauf lud zusätzlich 3.575 Minecraft-Assetdateien (621 MiB) in den externen Werkzeugcache; davon wurde nichts ins Zielrepository kopiert.
2. Zweiter Lauf ohne Generatoränderung: Exit **0**, **31 s**. Beide Ausgabebestände enthalten **7.952 gültig geparste JSON-Dateien**. Der nach Laufende ausgeführte Hashvergleich scheiterte mit Exit **1**: `AssertionError: Datagen content changed between runs`. Genau eine Datei unterschied sich: `assets/hbm_m/models/item/missile_shuttle.json`.
3. Ursache: `MissileFormFactorModels.SHUTTLE` liefert ein `Set.of(...)` mit fünf Modellteilen; `ModItemModelProvider` übernahm dessen nicht festgelegte Iterationsreihenfolge direkt als JSON-Array. Der Patch sortiert die Namen vor `toArray`. Kein JSON-Asset wurde von Hand als vermeintlich dauerhafte Korrektur überschrieben.
4. Datagen nach Korrektur im Analysecheckout: Exit **0**, **1m 23s**. Anschließend neuer Checkout `replay-final` vollständig über `prepare` erstellt, dort erneut Datagen: Exit **0**, **37 s**, mit drei Tasks aus dem gemeinsamen Gradle-Cache. Dies war kein zweiter vollständig cacheleerer Downloadlauf.
5. Inhaltsvergleich der beiden korrigierten Checkouts: Exit **0**, **alle 7.952 Dateien bytegleich**, Manifest-SHA256 **`cc5e858c1c85e6f409141d2a1eaa558731001551b3cabb1182d307a7893c2700`**. Die `.cache`-Verwaltungsdateien sind bewusst ausgeschlossen; alle eigentlichen Ausgaben sind enthalten und alle JSON-Dateien wurden geparst.
6. Nach der Mixin-Verpackungskorrektur nochmals frisches `replay-verified`: Datagen Exit **0**, **43 s**; Ressourcenvergleich Exit **0**, derselbe vollständige Manifest-Hash. Die zusätzliche Archivbereinigung verändert keine Datageneingabe oder -ausgabe.

Die ursprünglichen Manifest-Hashes waren `cc5e858c1c85e6f409141d2a1eaa558731001551b3cabb1182d307a7893c2700` und `937d5273f06fb2c18fe5e02df1b697403f051359f34439c6dcac61781d8e5a4d`. Der erste Vergleich des zweiten Laufs wurde versehentlich ausgelöst, bevor der Prozessabschluss bestätigt war; er wurde nach Abschluss wiederholt und zeigte dieselbe reale Abweichung. Nur der abgeschlossene Vergleich begründet den Befund. Die sortierte Ausgabe entspricht zufällig bereits der ersten beobachteten Reihenfolge.

Das beweist Wiederholbarkeit dieser Datengenerierung auf Linux mit den genannten Eingaben. Es ist kein vollständiger Audit jedes Rezept-/Modellverweises und kein Originalparitätsnachweis.

### Build, Javadoc und Hilfsskripte

- `:1.20.1-forge:tasks --all`: Exit **0**, **1m 28s**; eigene Kotlin-Buildlogik erfolgreich kompiliert.
- Erster `javaToolchains build sourcesJar --continue --info`: Exit **0**, **1m 9s**. Gradle erkennt vollständige Temurin-JDKs 17 und 21; Reobfuskierung sowie Mod-, Sources- und Javadoc-Archive wurden erzeugt. Dieser Zwischenstand enthielt noch nicht die Sortierkorrektur und Lizenzbeilage.
- Build im frischen `replay-final` nach Sortierung/Lizenzbeilage: Exit **0**, **46 s**. Build im frischen `replay-verified` mit korrigierter Mixin-Seitentrennung: Exit **0**, **42 s**.
- Nach dem Cacheausschluss erneut `build sourcesJar --continue --info`: Exit **0**, **26 s**. Die Mod-JAR bleibt byteidentisch zur zuvor am Produktionsserver getesteten Datei; das Sources-JAR ist um die elf Cacheeinträge bereinigt. Deshalb war kein erneuter identischer Serverversuch nötig.
- Javadoc meldete dabei vorhandene Kommentarfehler (`reference not found`, `@param name not found`, `unknown tag: key/category/BlockState/example`, `bad HTML entity`) und Warnungen zu fehlenden Kommentaren. Upstreams bereits vorhandenes `isFailOnError = false` lässt den Build weiterlaufen. **Die Javadoc-Erzeugung wird deshalb nicht als fehlerfrei gewertet.** Diese fachfremden Kommentarprobleme wurden nicht durch Entfernen von Hinweisen kaschiert.
- `prepare` wurde für die erste und endgültige Patchfassung in neuen externen Verzeichnissen erfolgreich ausgeführt. Die endgültigen neun veränderten Dateien wurden bytegenau mit dem Analysecheckout verglichen.
- Negativprüfungen des Helfers: Checkout innerhalb des Zielrepositorys mit Exit **1** abgewiesen; vorinstallierte JRE ohne `javac` mit Exit **1** vor dem Gradlestart abgewiesen. Diese erwarteten Fehler sind bestandene Schutzprüfungen, keine erfolgreichen Builds.
- `python3 -m py_compile tools/modernized_build.py` war erfolgreich. Die tatsächlich benutzten Auditbefehle und ihr Ergebnis werden ebenfalls protokolliert.

Weitere beobachtete Meldungen: Gradle verwendet veraltete, für Gradle 10 inkompatible Features; NFRT lud einige fest versionierte Werkzeuge nach Warnungen `... is not present in the artifact manifest` nach; Forge meldet bei seinen Sprach-/Kernbibliotheken fehlendes `mods.toml`; Datagen meldet nicht lesbares Entwicklungs-Refmap und `union:`-Ressourcen-URLs. Diese Meldungen verhinderten die erfolgreichen Datagen-/Buildaufrufe nicht. Das Mod-JAR enthält ein Refmap; die Entwicklungswarnung wird nicht mit einem fehlenden JAR-Eintrag gleichgesetzt. Ein Wechsel auf Gradle 10 ist nicht getestet.

### Java-17- und Verpackungsprüfung

Das tatsächlich reobfuskierte Modartefakt liegt unter `replay-verified/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-alpha+1.20.1-forge.jar`. Das separate `build/devlibs/`-JAR ist das Entwicklungsartefakt und wurde nicht als Server-Mod verwendet.

| Geprüfter JAR-Inhalt | Tatsächliches Ergebnis |
| --- | --- |
| Eigener Bytecode | **1.911 Klassen mit Major 61 (Java 17)**, keine neueren oder Preview-Klassen. Der Java-Compiler läuft über die JDK17-Toolchain mit `--release 17`. |
| Eingebettetes Architectury 9.2.14 | **381 Klassen mit Major 60 (Java 16)** und **1 mit Major 52 (Java 8)**; SHA256 identisch zum separat untersuchten Maven-JAR. |
| Eingebettetes MixinConstraints 1.1.0 | **21 Klassen mit Major 61**, SHA256 identisch zum separat untersuchten Maven-JAR. |
| Jar-in-Jar | Genau diese beiden JARs, keine weitere rekursive Einbettung; Versionen und Pfade in `META-INF/jarjar/metadata.json` geprüft. Keine JEI-/Create-/Render-/Profilermod-JARs eingebettet. |
| Modmetadaten | `hbm_m`, Version `0.2.1-alpha`, Forge 47.x/Minecraft 1.20.1; erforderliches Architectury und optionales Create bleiben gemäß Upstreammetadaten erhalten. |
| Mixins | `MixinConfigs` im Manifest und `mixins.hbm_m.refmap.json` vorhanden. Nach Korrektur **6 gemeinsame, 6 clientseitige, 0 serverexklusive Mixins**, keine Überschneidung. Automatisch gefundenes gemeinsames `ChunkMapAccessor` bleibt erhalten. |
| Lizenz | `LICENSE.hbm_m` enthält den unveränderten M-GPL-Text, SHA256 `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`. Fehlende vollständige Notices der eingebetteten Bibliotheken werden dadurch nicht ersetzt. |
| Plattformklassen | Keine `net/minecraft/**.class` oder `net/minecraftforge/**.class` im Mod-JAR. |

Der [Audithelfer](../tools/audit_modernized.py) liest tatsächliche Klassenheader, prüft auch eingebettete JARs und weist Preview-/neuere Klassen sowie überschneidende Mixin-Seitenzuweisungen zurück. **Java-17-Bytecodekompatibilität ist damit belegt.** Die eigene API-Nutzung wird zusätzlich durch die JDK17-Kompilierung begrenzt; ein vollständiger Linkage-/API-/Gameplaynachweis aller externen und optionalen Pfade folgt daraus nicht. Insbesondere bleibt der vollständige Dedicated-Server-/Clientlauf noch abzunehmen.

Die zusätzliche Archivprüfung fand zunächst elf `.cache`-Einträge im Sources-JAR (`AssertionError: Datagen cache packaged`, Exit **1**). Der abschließende Archivfilter behebt dies. Ein weiterer Prüflauf wandte versehentlich die Prüfung auf expandierte **Laufzeit**metadaten auch auf die Sources-Vorlage an (`AssertionError: Unexpanded metadata placeholders`, Exit **1**); dies war ein Fehler im Prüfskript. Nach Begrenzung auf die Mod-JAR bestand die Prüfung mit Exit **0**: unveränderter GPL-Text in allen drei Archiven, keine doppelten ZIP-Einträge, keine Datagen-Caches oder Plattformklassen; Laufzeit-TOML erfolgreich geparst und ohne Platzhalter.

Endgültige Artefakte nach der Archivbereinigung, **nur lokal, nicht veröffentlicht**:

| Datei unter `replay-verified/versions/1.20.1-forge/build/libs/` | Bytes | SHA256 |
| --- | ---: | --- |
| `hbm_m-0.2.1-alpha+1.20.1-forge.jar` | 44.888.266 | `3bf35768b36500bcae88988f971adaa180c5197cbff54f4438207f281e886a95` |
| `hbm_m-0.2.1-alpha+1.20.1-forge-sources.jar` | 41.942.516 | `fac289adbf3c69dde406d4b3e3cfee06181b2afeaffd56d6029cb9fab13de6c7` |
| `hbm_m-0.2.1-alpha+1.20.1-forge-javadoc.jar` | 7.460.785 | `76cea95e5c32cd8867ec4887dc6227947d271eb6fae173e3ccff46945afc5899` |

Das Javadoc-Archiv ist wegen der dokumentierten Kommentarfehler kein Nachweis einer fehlerfrei erzeugten API-Dokumentation. Das Sources-JAR enthält Modquellen/Ressourcen, aber ersetzt nicht den vollständigen zugehörigen Quellstand einschließlich Buildlogik und Generatoren.

### Dedicated-Server-Versuche mit dem erzeugten Mod-JAR

Ein eigener Produktionsserver wurde außerhalb aller Quellcheckouts installiert: Forge-Installer **1.20.1-47.4.20**, SHA256 `0ebcf198609f925e0018842a79473ef74fda78534f86d82f2c0fdb26449c1fa4`; `java17 -jar forge-installer.jar --installServer` mit expliziten Proxy-/CA-Optionen endete mit Exit **0** und `The server installed successfully`. Im `mods/`-Verzeichnis liegt genau das erzeugte Mod-JAR; Architectury/MixinConstraints kommen aus Jar-in-Jar. Keine zusätzlichen Entwicklungsclientmods wurden installiert.

Der erste Aufruf unter Java **17.0.20.1** fand beide eingebetteten Bibliotheken, meldete aber unter anderem:

```text
Attempted to load class net/minecraft/client/renderer/LightTexture for invalid dist DEDICATED_SERVER
@Mixin target net.minecraft.client.renderer.LightTexture was not found mixins.hbm_m.json:LightTextureMixin
```

Entsprechende Meldungen betrafen außerdem `LivingEntityRenderer`, `AbstractClientPlayer`, `ItemRenderer`, `ModelBlockRenderer` und `GameRenderer`. Der Vergleich von Quellkonfiguration und JAR belegte: Fletching Table ergänzt die bereits im `client`-Abschnitt stehenden Klassen zusätzlich in `mixins`. Die Verpackungskorrektur entfernt bereits seitenspezifisch deklarierte Klassen aus der gemeinsamen Liste und erhält übrige automatisch erkannte Mixins. Keine Renderer-/Mixin-Klasse wurde dafür entfernt oder umgeschrieben.

Der erneute Produktionsserver-Aufruf mit der korrigierten JAR endete nach etwa vier Sekunden mit Exit **0**, **ohne diese Dist-/Mixin-Fehler**, nach:

```text
Found 2 dependencies adding them to mods collection
Compatibility level set to JAVA_17
Launching target 'forgeserver' with arguments [nogui]
You need to agree to the EULA in order to run the server. Go to eula.txt for more info.
```

**Das ist kein vollständig bestandener Serverstart.** Es gab kein `Done`, keine Weltinitialisierung, keinen Clientbeitritt und keinen Gameplaytest. Die erzeugte `eula.txt` bleibt bei `eula=false`; keine EULA-Annahme wurde automatisiert. Weitere Startprobleme nach diesem Punkt sind noch nicht ausgeschlossen. Der nächste konkrete Schritt ist die eigene Prüfung/Annahme der Minecraft-EULA im Testserververzeichnis und die Wiederholung genau dieses Java-17-Aufrufs, danach Welt-, Client- und Funktionsprüfungen.

### Vorbereitung, Downloads und Diagnosebefehle

Die Arbeiten begannen ohne vorhandenen Git-Checkout in `/workspace` (`git -C /workspace status`: Exit **128**, `not a git repository`). Nach dem Klonen der Zielquelle fehlten die beiden Analysedokumente auf `main` (`cat`: Exit **1**, `No such file or directory`). Branch-/PR-Prüfung zeigte die bereits nach `docs/original-porting-plan` gemergte Analyse. Dies sind Verzeichnis-/Branchbefunde und keine Modernized-Buildfehler.

```bash
git clone https://github.com/urkrass06-oss/HBM-1.20.1.git /workspace/HBM-1.20.1
git branch -a
git log -8 --oneline
gh pr list --state all --limit 30 --json number,title,headRefName,baseRefName,state,url
git ls-remote --heads origin
git switch -c build/modernized-phase3 origin/docs/original-porting-plan

git ls-remote https://github.com/Raptor324/HBM-Modernized.git HEAD
git clone --no-checkout https://github.com/Raptor324/HBM-Modernized.git /workspace/scratch/modernized-phase3/upstream
git -C /workspace/scratch/modernized-phase3/upstream checkout --detach 0365cef5956016913095eeeb9366f26c601ca9a0

uname -a
free -m
df -h /workspace
cat /etc/codex/network-policy.json
cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.events
java -version
ls -la /usr/lib/jvm/java-21-openjdk-amd64/bin
/usr/lib/jvm/java-21-openjdk-amd64/bin/javac -version
python3 --version
git --version

curl -fsSL --max-time 60 'https://api.adoptium.net/v3/assets/latest/17/hotspot?architecture=x64&image_type=jdk&os=linux&vendor=eclipse' -o jdk17-release.json
curl -fsSL --max-time 60 'https://api.adoptium.net/v3/assets/latest/21/hotspot?architecture=x64&image_type=jdk&os=linux&vendor=eclipse' -o jdk21-release.json
curl --fail --location --retry 2 --max-time 180 -o jdk17.tar.gz 'https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.20.1%2B1/OpenJDK17U-jdk_x64_linux_hotspot_17.0.20.1_1.tar.gz'
curl --fail --location --retry 2 --max-time 180 -o jdk21.tar.gz 'https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz'
curl -fsSL --max-time 45 https://services.gradle.org/distributions/gradle-9.3.1-bin.zip.sha256 -o gradle-9.3.1-bin.zip.sha256
curl -fsSL --max-time 45 https://services.gradle.org/distributions/gradle-9.3.1-wrapper.jar.sha256 -o gradle-9.3.1-wrapper.jar.sha256
curl -fsSL --max-time 45 https://raw.githubusercontent.com/gradle/gradle/v9.3.1/gradle/wrapper/gradle-wrapper.jar -o gradle-wrapper-9.3.1.jar
curl --fail --location --retry 2 --max-time 180 --output gradle-9.3.1-bin.zip https://services.gradle.org/distributions/gradle-9.3.1-bin.zip
```

Die Downloads erfolgten im externen Arbeitsverzeichnis; alle oben genannten eigentlichen Downloads waren erfolgreich. Ein vorgeschaltetes `curl -fsSIL` gegen Adoptiums `/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse` prüfte die Weiterleitung. Hashprüfung/Entpacken erfolgten mit Python `hashlib`/`tarfile`, der Distributionsabgleich mit `zipfile`. Die ergänzende Paketprüfung `apt-cache policy openjdk-17-jdk-headless` lieferte keine nutzbare Installation und meldete `Unable to read /etc/apt/apt.conf.d/80-applied-apt-retries ... Permission denied`; es wurden keine Systempakete verändert.

Gelesen wurden die beiden vorhandenen Analysen, README, Git-Dateibaum, aktive Gradle-/Katalog-/Buildlogik-/Daemon-/Wrapperdateien, CI-/Releaseworkflows, `mods.toml`, Mixins sowie die in der Importcheckliste verlinkten Herkunftsanker (`rg`, `cat`, `sed`, `git show`, `git rev-parse`, `git ls-tree`). `tail`, `du`, `ps`, Container-Speicherzähler und einmal `jcmd <Daemon-PID> Thread.print` dienten der laufenden Builddiagnose. Das 8-GiB-Containerlimit führte während der abgeschlossenen Minecraft-Vorbereitung zu keinem OOM-Kill.

Die Bibliotheksprüfung lud die beiden in der [Importcheckliste](MODERNIZED_IMPORT_CHECKLIST.md#5-bibliotheken-und-verpackung) genannten JARs und POMs sowie das MixinConstraints-Sources-JAR mit `curl -fsSL --max-time 45`. ZIP-Dateiliste, Metadaten, Klassenheader und SHA256 wurden per Python gelesen. `git ls-remote --tags` auf `architectury/architectury-api` mit `refs/tags/9.2.14*` und auf `Moulberry/MixinConstraints` mit `refs/tags/*1.1.0*` waren erfolgreich, lieferten aber keine passenden Refs. Es wurde daraus keine automatische Sourcezuordnung abgeleitet.

## 5. Reproduktion mit einem frischen externen Checkout

Benötigt werden Git, Python 3.10 oder neuer und vollständige JDKs **21 und 17**. Ein Java-Runtimepaket ohne `javac` reicht nicht. Die Pfade werden von der jeweiligen Maschine vorgegeben; keine Benutzer-/Windows-Pfade in Projektproperties eintragen.

```bash
# Aus dem Zielrepository; HBM_PHASE3_ROOT muss außerhalb davon liegen.
export HBM_PHASE3_ROOT=/workspace/scratch/modernized-phase3-neu
export JAVA21_HOME=/pfad/zum/vollstaendigen/jdk-21
export JAVA17_HOME=/pfad/zum/vollstaendigen/jdk-17

python3 tools/modernized_build.py prepare "$HBM_PHASE3_ROOT/upstream"

python3 tools/modernized_build.py run "$HBM_PHASE3_ROOT/upstream" javaToolchains \
  --gradle-home "$HBM_PHASE3_ROOT/gradle-home" --log-dir "$HBM_PHASE3_ROOT/logs"
python3 tools/modernized_build.py run "$HBM_PHASE3_ROOT/upstream" runData \
  --gradle-home "$HBM_PHASE3_ROOT/gradle-home" --log-dir "$HBM_PHASE3_ROOT/logs"
python3 tools/audit_modernized.py resources "$HBM_PHASE3_ROOT/upstream/src/generated/resources" \
  --output "$HBM_PHASE3_ROOT/datagen-1.sha256"
# Erst nach Prozessabschluss erneut starten und anschließend den Inhalt vergleichen:
python3 tools/modernized_build.py run "$HBM_PHASE3_ROOT/upstream" runData \
  --gradle-home "$HBM_PHASE3_ROOT/gradle-home" --log-dir "$HBM_PHASE3_ROOT/logs"
python3 tools/audit_modernized.py resources "$HBM_PHASE3_ROOT/upstream/src/generated/resources" \
  --output "$HBM_PHASE3_ROOT/datagen-2.sha256" --compare "$HBM_PHASE3_ROOT/datagen-1.sha256"
python3 tools/modernized_build.py run "$HBM_PHASE3_ROOT/upstream" build sourcesJar \
  --gradle-home "$HBM_PHASE3_ROOT/gradle-home" --log-dir "$HBM_PHASE3_ROOT/logs"
python3 tools/audit_modernized.py jar \
  "$HBM_PHASE3_ROOT/upstream/versions/1.20.1-forge/build/libs/hbm_m-0.2.1-alpha+1.20.1-forge.jar"
python3 tools/modernized_build.py run "$HBM_PHASE3_ROOT/upstream" runServer \
  --gradle-home "$HBM_PHASE3_ROOT/gradle-home" --log-dir "$HBM_PHASE3_ROOT/logs"
```

In der hier benutzten Cloudumgebung wurde bei jedem `run` zusätzlich **`--trust-store /etc/ssl/certs/java/cacerts`** gesetzt. Andere Umgebungen verwenden ihren eigenen gültigen CA-Truststore oder den JDK-Standard. Proxyvariablen werden geerbt. Der Helfer unterstützt die hier vorhandenen HTTP-Proxys ohne Benutzerinformationen; andere Proxy-Authentifizierung muss über die unterstützte lokale JVM-Konfiguration erfolgen.

`prepare` verlangt ein neues Verzeichnis, lädt den Commit direkt per SHA und prüft den Textpatch mit `git apply --check`. Ein abgebrochener Vorbereitungsversuch wird nicht durch Löschen vorhandener Dateien bereinigt; stattdessen ein neues Ziel wählen. `run` schreibt vollständige stdout/stderr-Logs und ein `commands.jsonl` mit UTC, ausgeführter Argumentliste, Commit und Exitcode. Nach Vorbereitung `git diff` prüfen. Windows wurde nicht getestet.

Der obige `runServer`-Befehl ist ein zusätzlicher **Entwicklungsstart** zur Reproduktion; tatsächlich getestet wurde der Produktionsserver mit der reobfuskierten JAR. Der genaue ausgeführte Aufruf im separaten Serververzeichnis war:

```bash
timeout 150 /workspace/scratch/modernized-phase3/jdks/jdk-17.0.20.1+1/bin/java \
  -Xms512M -Xmx3G -Dhttp.proxyHost=proxy -Dhttp.proxyPort=8080 \
  -Dhttps.proxyHost=proxy -Dhttps.proxyPort=8080 \
  -Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts \
  @libraries/net/minecraftforge/forge/1.20.1-47.4.20/unix_args.txt nogui
```

Das ist ein kontrolliert wiederholbarer Linux-Build. Ein byteidentischer kompletter Neuaufbau ohne Cache und vollständig offline wiederholbare Builds wurden nicht nachgewiesen. Inaktive Mehrloaderdateien und Upstream-Publishworkflows werden nicht gestartet oder in unser CI übernommen.

### Dauerhaft im PR enthaltene Prüfbelege

Der [Belegordner](modernized-build/README.md) enthält **48 Befehlsdatensätze** mit UTC, exakten Argumentlisten und Exitcodes sowie die zugehörigen vollständigen Logs einschließlich Fehlversuchen. Die [719 Artefakthashes](modernized-build/artifacts-sha256.tsv) dokumentieren tatsächlich aufgelöste Downloads aus Build-/NFRT-Caches und Serverinstallation. Das ist eine beobachtete Obermenge, kein erzwungenes Dependency-Locking und keine pauschale Freigabe dieser Dateien. Lizenz-/Einbettungsnachweise bleiben auf das konkrete Modartefakt bezogen.

Die frühen lokalen Diagnoseprogramme sind als Textbelege beigefügt; für neue Läufe sind die beiden Helfer in `tools/` maßgeblich. Reine Lese-/Statusbefehle stehen gesammelt in §4; Änderungen am Fremdcheckout vollständig im Patch und Wrapperdownload des Helfers. Im Zielrepository wurden ausschließlich Dokumentation, Prüfbelege und die beiden Helfer samt Patch ergänzt. Das vorhandene Grundgerüst und seine Tests wurden nicht verändert; historische Foundation-/Inventurprüfungen werden nicht als neue Modernized-Erfolge ausgegeben.

Abschlussprüfungen: `python3 -m py_compile tools/modernized_build.py tools/audit_modernized.py` erfolgreich; alle archivierten Loghashes und Befehlsverweise geprüft; lokale Markdown-Dateilinks vorhanden; endgültiger Patchhash und Bytegleichheit aller neun Checkoutänderungen bestätigt. Quell-/Dokumentationsdiff und Git-Dateistatus werden vor dem PR geprüft; unveränderte Originalausgaben in den Textprotokollen werden nicht durch Formatierungskorrekturen verfälscht.

## 6. Herkunft und noch erforderliche Abnahme

Die [Importcheckliste](MODERNIZED_IMPORT_CHECKLIST.md) führt Quellpins, Pflichtfelder pro Datei, konkrete Blob-/SHA256-Anker, Assetnachweise, Bibliotheksbelege und GPL-/LGPL-Verpflichtungen zusammen. Eine erfolgreiche technische Prüfung gibt keine ungeprüften Assets frei und ändert keinen Originalportstatus.

Für den technischen Basisbuild sind Proxy-, vollständige-JDK-/Toolchain-, Datagen- und die beobachteten Verpackungsprobleme behoben. Vor einem Import/Release bleiben konkret:

1. EULA im eigenen Testserver prüfen/annehmen, Java-17-Server bis `Done` und Weltinitialisierung erneut testen; danach Clientbeitritt, minimaler Kernbetrieb und optionale Integrationen getrennt abnehmen. Keine weitere Serverkompatibilität aus dem frühen Abbruch ableiten.
2. Individuelle Assetherkunft und Bibliotheks-Notices gemäß Importcheckliste schließen; passende Gesamtwerkkennzeichnung und vollständigen Corresponding Source vorbereiten. Die lokale JAR wird nicht als Download oder spielbar veröffentlicht.
3. Abhängigkeiten anhand der beobachteten Hashes für einen späteren eingefrorenen Releasebuild verifizieren/locken, frischen Build ohne gemeinsame Caches und Archivhashvergleich durchführen. Windows- und CI-Läufe gesondert prüfen; den alten JDK17-/Gradle8.7-Upstreamworkflow nicht unverändert verwenden.
4. Javadoc-Kommentarfehler separat bereinigen. Fachliche Porttreue, Netzwerk-/Speicher-/Maschinen-/Rendererabnahmen aus dem Migrationsplan bleiben offen; dieser PR ändert keine Feature-Matrix-Statuswerte.
