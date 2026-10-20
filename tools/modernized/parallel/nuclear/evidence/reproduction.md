# N-01 reproduzieren

Diese Lieferung ist ein Draft mit realer Prozessimplementierung und Tests. Zentrale Produktionsbindungen und die N-05-Forschungsquelle fehlen. Der zusätzliche required Test `breederRequiresProductionBindings` muss diesen Zustand melden. Tests nicht filtern oder abschwächen. Die bisherige zentrale Phase-5-CI lädt N-01 noch nicht automatisch; ihr Erfolg allein prüft diesen Patch nicht. R-01 ist inzwischen in PR #9 verfügbar. Die sechs zusätzlichen zentralen Dateireservierungen aus requests/R-01-test-loader.json fehlen dort noch; der echte Loader muss N derzeit vor Zielerzeugung abweisen.

Aus einem sauberen Zielcheckout bei Basis `997b15c9d60dd293e9c436663e90a95140ab13af` einen neuen externen M-Baum erzeugen:

```bash
export HBM_CHECK_ROOT=/absolute/external/new-nuclear-check
export HBM_JAVA21=/absolute/toolchains/jdk-21
export HBM_JAVA17=/absolute/toolchains/jdk-17
python3 tools/integrate_modernized.py "$HBM_CHECK_ROOT/modernized" --phase5
```

Historischer manueller Prüfpfad der bisherigen N-Läufe (keine Freigabe des zentralen R-01-Loaders): Nur den Bereichspatch und die exakt gelisteten eigenen Klassen installieren. Das folgende Skript aus dem Zielcheckout starten; `HBM_CHECK_ROOT` muss außerhalb öffentlicher Worktrees liegen. Es verweigert das Überschreiben bereits vorhandener Overlay-/Testklassen. Der M-HEAD bleibt am Pin, keine Änderungen in M committen.

```bash
python3 - <<'PY'
import os, shutil, subprocess
from pathlib import Path
area = Path('tools/modernized/parallel/nuclear').resolve()
checkout = Path(os.environ['HBM_CHECK_ROOT']).resolve() / 'modernized'
subprocess.run(['git', '-C', str(checkout), 'apply', '--check', str(area/'changes.patch')], check=True)
subprocess.run(['git', '-C', str(checkout), 'apply', str(area/'changes.patch')], check=True)
for relative in (
    'overlay/com/hbm_m/inventory/recipes/BreederRecipes.java',
    'overlay/com/hbm_m/item/nuclear/BreedingRodItem.java',
    'overlay/com/hbm_m/blockentity/machines/ResearchReactorFluxSource.java',
    'gametest/com/hbm/integration/nuclear/BreederGameTests.java',
):
    prefix, path = relative.split('/', 1)
    target = checkout / ('src/main/java' if prefix == 'overlay' else 'integration/src/gametest/java') / path
    if target.exists():
        raise RuntimeError('Refusing overwrite: ' + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(area/relative, target)
PY
```

Danach die G2-Befehle aus `docs/PARALLEL_DEVELOPMENT.md` ausführen: zweimal `runData` mit Ressourcenmanifestvergleich, getrennt `build sourcesJar`, Produktions-JAR auditieren und hashen, erst anschließend `runGameTestServer`. **Jeder** Buildaufruf muss `--gradle-arg=-Pdeps.forge=47.4.23` erhalten. Build-JDK 21, Mod-/Test-JDK 17, Gradle 9.3.1. Das Testprofil benötigt zusätzlich `--gradle-arg=-Pmodernized.gameTests=true`. Hier wurde `--trust-store /etc/ssl/certs/java/cacerts` benutzt, ohne Proxy oder TLS-Prüfung auszuschalten.

Zusätzlich zum gemeinsamen JAR-Audit den ganzen Pfad `com/hbm/integration/nuclear/` und alle `nuclear_test_flux_source`-Einträge ausschließen. Die ausschließlich im Testprofil ergänzten Stäbe/Schwertstufen und der konstante Testquellenblock sind keine Produktionslieferung. Die echte Forschungsquelle bleibt ausschließlich N-05 vorbehalten. `BreederTestContent` registriert fehlende Testitems erst nach normalen Produktionsregistrierungen; der Pflicht-Test darf erst nach tatsächlicher Produktionslieferung grün werden.

G4 erfordert die Produktions-JAR, zwei reguläre Serverstarts und relevante Inventar-/NBT-Abfragen nach Neustart. G5 erfordert zwei echte Produktionsclients und mindestens zehn Minuten gemeinsame Verbindung. G6 erfordert normales Entladen/Laden ohne Forcechunks, Dimensionen/Reconnect und Singleplayer-Kopie. G7 erfordert getrennte Messungen der fixierten 1.7.10-Laufzeit; G8 den gemeinsamen zweistündigen Betrieb nach Integration aller Lieferungen. Diese Nachweise werden durch Testfixtures oder historische Phase-5-Ergebnisse nicht ersetzt. Keine JAR, Welt, generierten Ressourcen oder vollständigen Quellbäume veröffentlichen.

## Neuer R-01-Vertrag

`area.json` und `rights.json` entsprechen dem konkreten Schema von R-Commit `c63be0f5bcf43ff1d1f8b4febb25f831a15fc047`: eingefrorene `baseline`, exakte `files` mit Vor-/Nachbildhashes, `payloads`, acht required `tests` und per Payload freigegebene Herkunftsakte. Die ausführliche Quellherkunft liegt in `evidence/provenance.json`. Die Testfixture ist jetzt eine öffentliche statische Unterklasse der einzigen Testquelldatei. Es gibt keine Testquelldatei ohne deklarierte GameTests. Der Patch benötigt keine eigene Git-Attributdatei; die resultierenden drei Java-Dateien bleiben bytegleich zum bereits gebauten Produktionsstand.

Bis R die sechs exakten Einträge in seiner zentralen Policy übernommen hat, bleibt die Bereichsintegration blockiert. Der aktuelle unveränderte R-Loader darf nicht durch eine privat gelockerte Policy als bestanden ausgegeben werden. Eine rein lesende hypothetische Schemaanalyse mit genau den angefragten Einträgen ist als solche gekennzeichnet; sie ist keine erfolgreiche Integration.

Nach R-Reservierungslieferung: den geprüften R-Werkzeugcommit und den geprüften N-Liefercommit lokal verfügbar machen, beide SHAs festhalten und ausschließlich diese vollen SHAs auswählen. Beispiel aus dem R-Werkzeugcheckout:

```bash
python3 tools/integrate_modernized.py "$HBM_CHECK_ROOT/modernized" --phase5 \
  --delivery "nuclear@$HBM_NUCLEAR_DELIVERY"
```

Für den gemeinsamen JUnit-Reporter zusätzlich die passende geprüfte Rendering-Lieferung explizit auswählen. Das ergibt 24 required Tests (14 Basis, 2 R, 8 N). Danach Produktionsprofil `--profile production` verwenden und alle Gates auf dem tatsächlich integrierten Stand erneut prüfen. Produktionsbindungen und echte N-05-Quelle bleiben auch nach einer Policyänderung zwingend erforderlich.
