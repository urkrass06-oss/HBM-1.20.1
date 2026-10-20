# Herkunft der Modernized-Integrationshinweise

Der vollständige Importmanifestdatensatz steht unter [docs/integration/import-manifest.json](../docs/integration/import-manifest.json). Die drei in Phase 4 ergänzten Lizenztexte wurden unverändert kopiert; vorhandene Forge-, Gradle-, GPL- und LGPL-Texte bleiben erhalten.

| Text | Quelle |
| --- | --- |
| `MODERNIZED_GPL-3.0.txt` | Raptor324/HBM-Modernized, `0365cef5956016913095eeeb9366f26c601ca9a0`, `LICENSE`. |
| `MIXINCONSTRAINTS_LICENSE.txt` | Moulberry/MixinConstraints, `07544882c2473ac282976f290b023c28d12c539b`, `LICENSE`; MIT, Copyright (c) 2023 Moulberry. Maven-Version 1.1.0: 19/19 Java-Quellen bytegleich zugeordnet. |
| `ARCHITECTURY_LICENSE.md` | architectury/architectury-api, `22caa2810877d03f0653cbcd0e1ea0114fcf6dd0`, `LICENSE.md`; LGPLv3-Lizenzdokument. Kein Beleg eines exakten 9.2.14-Releasecommits. |

Die beiden Patches unter `tools/modernized/` enthalten Kontext aus Modernizeds GPLv3-Bestand am genannten Pin. Änderungen: Phase-3-Build-/Datagen-/Mixin-Verpackungskorrekturen und Phase-4-Einstieg, Testprofil, Metadaten und Notices, jeweils 19. Oktober 2026. Die eigenständigen Python-Helfer, Foundation-Anpassungen und neuen GameTests behalten ihre angegebenen LGPL-3.0-only-Vermerke. Die externe Modernized-Gesamtintegration ist GPLv3.

Modernized nennt RaptorDev, TRFFuchs, razchexlitiel und HyperiO als Autoren; Mitwirkende: ThePhoenixKnight, boryu._. (ko_kr), hexagon_inc (.dae parser), kami_no_samurai (fr_fr). Die README würdigt The Bobcat als Original-HBM-Autor und Raptor324 für die Modernisierung. Diese Nennungen ersetzen keine Einzeldatei-/Assetrechte. Vorhandene individuelle Header werden im externen Checkout erhalten.

Die ungeklärten Spielquellen und Assets sowie Bibliotheksbinärdateien werden nicht in diesen PR übernommen. Eine spätere Distribution benötigt die vollständigen individuellen Nachweise und zugehörigen Quellen gemäß [Importcheckliste](../docs/MODERNIZED_IMPORT_CHECKLIST.md).
