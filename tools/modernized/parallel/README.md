# Bereichslieferungen (R-01)

Gemeinsame Basis: `997b15c9d60dd293e9c436663e90a95140ab13af`.
`policy.json` friert O/M, drei Patches und die bisherigen Overlays/Tests ein.
Die exakte `owners`-Liste reserviert zunächst die Dateien aus M-01, N-01,
W-01 und R-01/02. Neue Produktions- und Testdateien benötigen vor Änderung
einen zentral geprüften Eintrag; ein Bereich kann sich keine Rechte im eigenen
Manifest geben. Zentrale Register bleiben bei Rendering. Keine Familienglob-Rechte.

```bash
python3 -m unittest discover -s tools -p 'test_modernized_*.py' -v
python3 tools/integrate_modernized.py /external/new-checkout --phase5 \
  --delivery rendering@FULL_DELIVERY_COMMIT \
  --delivery machines@FULL_DELIVERY_COMMIT
```

Jeder ausgewählte Commit muss im lokalen Zielrepository verfügbar sein und vom
gemeinsamen Basiscommit abstammen. Der Loader liest ausschließlich Git-Blobs aus
`tools/modernized/parallel/AREA/`; uncommittete Änderungen sind keine Lieferung.
Keine automatische Auswahl, Branchauflösung oder Nachladung von Abhängigkeiten.
Alle referenzierten Liefercommits werden explizit ausgewählt. Ihre `api_version`
muss exakt passen. Unabhängige Lieferungen werden alphabetisch sortiert,
`kind: central` vor `kind: area`, ansonsten gilt der Abhängigkeitsgraph.
Nur Rendering darf zentrale Requestlieferungen anbieten. Zyklen sind Fehler.

`area.json` (Schema 1) enthält:

- `area`, `kind`, `tasks`, `features`, `api_version` und `baseline` (exakte Kopie
  des eingefrorenen Policy-Basisteils, einschließlich `target_base` und Hashes).
- `requires`: Liste `{area, commit, api_version}` mit vollen Git-SHAs.
- `payloads`: exakte Zuordnung jedes anderen Lieferpfads zu SHA256. Zusätzliche,
  fehlende, symbolische oder ausführbare Dateien sind verboten.
- `patch`: relativer Patchpfad oder `null`. Nur gewöhnliche UTF-8-Unified-Diffs
  auf vorhandene Dateien; kein Binary, Rename, Delete, Moduswechsel oder neues
  Patchziel. Kontext ist Teil der Rechteprüfung. Erst `git apply --check`, dann
  ohne Fuzz-/Reject-Fortsetzung anwenden.
- `files`: exakte externe Ziele `{target, source, before_sha256, sha256}`.
  Bei Patchzielen ist `source: null`; Vor- und Nachbildhash sind verpflichtend.
  Neue eigene Java-Dateien kommen aus `overlay/`, haben `before_sha256: null`
  und dürfen kein vorhandenes Ziel ersetzen. Tests kommen aus
  `gametest/com/hbm/integration/AREA/` und gehen ausschließlich nach
  `integration/src/gametest/java/`.
- `tests`: `{id, source, required: true}` für jeden neuen GameTest.
- `registrations`: zentrale Requests `{registry, id, class, bindings,
  initialization, resources, tests, request}`; Identität ist `(registry, id)`.
  Namespace `hbm_m`, keine doppelten Identitäten. Ohne Registeränderung `[]`.
- `requests`: optionale Liste gehashter JSON-Aufträge unter `requests/`.
  Jeder Registryeintrag verweist auf einen solchen geprüften Auftrag. Aufträge
  werden dokumentiert, nicht als Code ausgeführt. Bereits als Literal in der
  jeweiligen zentralen Basisdatei vorhandene IDs werden vor Anwendung abgewiesen;
  dynamisch konstruierte Registrierungen erfordern zusätzlich fachliches Review
  und den Forge-Laufzeittest.
- `evidence`: nichtleere Liste gehashter Textbelege unter `evidence/`.

`rights.json` enthält für jeden Payload außer den beiden administrativen
JSON-Dateien `{sha256, origin, source_commit, authors, license, notices, review,
publication_status}`. Nur `publication_status: cleared` wird angenommen. Das ist
ein technisches Gate für dokumentierte Prüfung, keine automatische Lizenzfreigabe.
Jede Beurteilung muss einschließlich Patchkontext inhaltlich überprüft werden.
Die vorhandene externe Modernized-Rechteentscheidung bleibt unverändert.

Alle Lieferungen werden zuerst rein lesend geprüft. Danach entsteht ein
temporärer externer Checkout: Phase 3 → 4 → 5 → zentrale Requests → Bereiche.
Fehler hinterlassen kein Ziel. Erst der erfolgreiche Gesamtlauf veröffentlicht
das neue Ziel; existierende Ziele werden abgewiesen. M-HEAD bleibt unverändert.
`integration/provenance.json` enthält Liefercommits, Manifest-/Payloadhashes,
Rechteakten und sämtliche Arbeitsdateien mit SHA256, auch neue und weiterhin
ungeklärte Dateien. Der eigene generierte Testvertrag bleibt im Testprofil.

Die Miniaturtests verwenden selbst geschriebene Daten und benötigen weder
Minecraft, Modernized, JDK noch Netzwerk. Volle Spielbäume, generierte Ressourcen
und Evaluations-JARs verbleiben extern; keine CI-Artefaktuploads.
