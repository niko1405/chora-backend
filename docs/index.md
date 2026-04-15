# Chora Dokumentation

Diese Dokumentation beschreibt die FastAPI-Anwendung Chora mit ihrer REST-
Schnittstelle, GraphQL-Schnittstelle, dem PostgreSQL-Datenmodell sowie der
Authentifizierung und Autorisierung über Keycloak.

## Einstieg

- [Schichtenarchitektur](schichtenarchitektur.md)
- [Komponentendiagramm](komponentendiagramm.md)
- [ER-Diagramm](er-diagramm.md)
- [Use Cases](use-cases.md)

## API-Module

- [Paket chora](modules/__init__.md)
- [Konfiguration](modules/config.md)
- [Entity](modules/entity.md)
- [REST](modules/rest.md)
- [GraphQL](modules/graphql.md)
- [Repository](modules/repository.md)
- [Service](modules/service.md)
- [Security](modules/security.md)

## HTML-Generierung

Die Dokumentation kann mit MkDocs als HTML generiert werden:

```bash
uv run mkdocs serve
uv run mkdocs build
```
