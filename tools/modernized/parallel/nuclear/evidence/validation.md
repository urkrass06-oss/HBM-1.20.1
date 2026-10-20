# N-01 – Prüfstand

Diese Lieferung bleibt Draft/blockiert. Der finale Prüfbericht wird nach dem laufenden Testdurchgang ergänzt. Der implementierte Prozess verwendet ausschließlich den fixierten O-Fluxprozess; fehlende Produktionsbindungen und die fehlende N-05-Forschungsquelle werden nicht durch Testfixtures freigegeben.

Forge 47.4.23: zwei bytegleiche Datagenläufe (7.952 Ressourcen), getrenntes `build sourcesJar`, Java-17-/Jar-in-Jar-/Ressourcen-/Ein-Einstieg-Audit bestanden. Produktions-JAR SHA256 `8b449e2272fa28369cbb46f8752ebbdbec83e9196d55d9d13db84722c00a18d0`. Keine nuklearen Testklassen in Produktion.

Erster GameTest-Durchgang: 22 required Tests ausgeführt, 21 bestanden, `breederRequiresProductionBindings` meldet fehlende Produktionsbindungen. Finale Testfassung wird nach Verschärfung des unabhängigen Quad-Sollwerts erneut geprüft. G3 ist ausdrücklich nicht bestanden. G4–G8 bleiben offen. Reproduktion: [reproduction.md](reproduction.md).
