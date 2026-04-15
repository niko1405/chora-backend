# Hinweise zur Dokumentation

Die Dokumentation basiert auf MkDocs, MkDocstrings und PlantUML.

## PlantUML

Die PlantUML-Quellen liegen unter `docs/diagramme/src`.
Beim MkDocs-Build werden daraus die Diagramme für die HTML-Dokumentation erzeugt.

## HTML-Generierung

Die Doku kann lokal als HTML angezeigt oder gebaut werden:

```bash
uv run mkdocs serve
uv run mkdocs build
```

`uv run mkdocs serve` startet einen lokalen Webserver, `uv run mkdocs build` erzeugt
die statische HTML-Dokumentation im Ausgabeordner `site/`.
