# Modernized-Basis von HBM Complete Port

Der vollständige Import erfolgt vorerst **in einem externen Checkout**. Modell-, Audio- und weitere Herkunftsfragen sind offen; dieser Ordner enthält deshalb keine fremden Spielquellen oder Assets. Der aktive Integrationsbuild ist Minecraft **1.20.1**, Forge **47.4.20**, Mod-ID **`hbm_m`**, Gradle **9.3.1** mit JDK **21** und Java **17** für Mod und Minecraft.

```bash
# Neues Verzeichnis außerhalb dieses Repositorys; vollständige JDKs vorausgesetzt.
export HBM_PHASE4_ROOT=/tmp/hbm-phase4
export JAVA21_HOME=/path/to/jdk-21
export JAVA17_HOME=/path/to/jdk-17
python3 tools/integrate_modernized.py "$HBM_PHASE4_ROOT/modernized"
python3 tools/modernized_build.py run "$HBM_PHASE4_ROOT/modernized" runData \
  --gradle-home "$HBM_PHASE4_ROOT/gradle-home" --log-dir "$HBM_PHASE4_ROOT/logs"
python3 tools/modernized_build.py run "$HBM_PHASE4_ROOT/modernized" build sourcesJar \
  --gradle-home "$HBM_PHASE4_ROOT/gradle-home" --log-dir "$HBM_PHASE4_ROOT/logs"
```

Unter dem externen `modernized/` liegen unveränderte Upstreamdateien am festgelegten Commit, die beiden dokumentierten Patches, `integration/src/main/java` für die Foundation-Anbindung, `integration/src/gametest/java` für das gesonderte Testprofil und `integration/notices`. `integration/provenance.json` dokumentiert jeden Upstream-Blob mit SHA256 sowie Overlay und Patchstände. Gradlecache, Logs und isolierter Testserver liegen daneben. Es gibt genau einen aktiven `@Mod`-Einstieg in `com.hbm.HbmPort`; `ForgeEntrypoint.initialize` registriert Modernizeds Inhalte. Die leeren Foundation-Register werden nicht zusätzlich angemeldet.

Der Root-Wrapper baut weiterhin nur das historische Foundation-Gerüst mit Forge 47.4.10. Seine leere JAR ist kein Integrationsartefakt. Bestehende Dateien und die Original-Feature-Matrix bleiben erhalten. Der spätere Wechsel auf `hbm` ist in dieser Phase ausdrücklich aufgeschoben.

Rechteentscheidung, tatsächliche Testergebnisse, JAR-Pfad/Hash und vollständige Reproduktion: [Integrationsbericht](../docs/INTEGRATION_REPORT.md), [Buildstatus](../docs/BUILD_STATUS.md), [offene Punkte](../docs/REMAINING_ISSUES.md).
