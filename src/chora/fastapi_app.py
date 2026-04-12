"""FastAPI application for the Songs API.

This module provides a simple REST API for songwriting workspace management.
"""
from pathlib import Path
from typing import Final

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse
from loguru import logger

from chora.config import (
    dev_db_populate,
    dev_keycloak_populate,
)
from chora.config.dev.db_populate_router import router as db_populate_router
from chora.config.dev.keycloak_populate_router import (
    router as keycloak_populate_router,
)
from chora.graphql_api import graphql_router
from chora.problem_details import create_problem_details
from chora.router import (
    artist_write_router,
    auth_router,
    health_router,
    shutdown_router,
    song_router,
    song_write_router,
)
from chora.security.exceptions import AuthorizationError, LoginError
from chora.service.exceptions import (
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)

# Instanz der App erstellen
app = FastAPI(title="Songs API", description="Songwriting Workspace", version="1.0.0")

# --------------------------------------------------------------------------------------
# R E S T
# --------------------------------------------------------------------------------------
app.include_router(artist_write_router, prefix="/rest/artists")
app.include_router(song_router, prefix="/rest/artists")
app.include_router(song_write_router, prefix="/rest/artists")
app.include_router(auth_router, prefix="/auth")
app.include_router(health_router, prefix="/health")
app.include_router(shutdown_router, prefix="/admin")

if dev_db_populate:
    app.include_router(db_populate_router, prefix="/dev")
if dev_keycloak_populate:
    app.include_router(keycloak_populate_router, prefix="/dev")


# --------------------------------------------------------------------------------------
# G r a p h Q L
# --------------------------------------------------------------------------------------
app.include_router(graphql_router, prefix="/graphql")


# --------------------------------------------------------------------------------------
# F a v i c o n
# --------------------------------------------------------------------------------------
@app.get("/favicon.ico")
def favicon() -> FileResponse:
    """facicon.ico ermitteln.

    :return: Response-Objekt mit favicon.ico
    :rtype: FileResponse
    """
    src_path: Final = Path("src")
    file_name: Final = "favicon.ico"
    favicon_path: Final = Path("patient") / "static" / file_name
    file_path: Final = src_path / favicon_path if src_path.is_dir() else favicon_path
    logger.debug("file_path={}", file_path)
    return FileResponse(
        path=file_path,
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


# --------------------------------------------------------------------------------------
# E x c e p t i o n   H a n d l e r
# --------------------------------------------------------------------------------------
@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, _err: NotFoundError) -> Response:
    """Errorhandler für NotFoundError.

    :param _err: NotFoundError aus der Geschäftslogik
    :return: Response mit Statuscode 404
    :rtype: Response
    """
    return create_problem_details(status_code=status.HTTP_404_NOT_FOUND)


@app.exception_handler(ForbiddenError)
def forbidden_error_handler(_request: Request, _err: ForbiddenError) -> Response:
    """Errorhandler für ForbiddenError.

    :param _err: ForbiddenError vom Überprüfen der erforderlichen Rollen
    :return: Response mit Statuscode 403
    :rtype: Response
    """
    return create_problem_details(status_code=status.HTTP_403_FORBIDDEN)


@app.exception_handler(AuthorizationError)
def authorization_error_handler(
    _request: Request,
    _err: AuthorizationError,
) -> Response:
    """Errorhandler für AuthorizationError.

    :param _err: AuthorizationError vom Extrahieren der Benutzerkennung aus dem
        Authorization-Header
    :return: Response mit Statuscode 401
    :rtype: Response
    """
    return create_problem_details(status_code=status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(LoginError)
# pylint: disable-next=invalid-name
def login_error_handler(_request: Request, err: LoginError) -> Response:
    """Exception-Handler, wenn der Benutzername oder das Passwort fehlerhaft ist.

    :param _exc: LoginError
    :return: Response-Objekt mit Statuscode 401
    :rtype: Response
    """
    return create_problem_details(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err)
    )


@app.exception_handler(EmailExistsError)
def email_exists_error_handler(_request: Request, err: EmailExistsError) -> Response:
    """Exception-Handling für EmailExistsError.

    :param err: Exception, falls die Emailadresse des neuen oder zu ändernden Patienten
        bereits existiert
    :return: Response mit Statuscode 422
    :rtype: Response
    """
    return create_problem_details(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(err),
    )


@app.exception_handler(UsernameExistsError)
def username_exists_error_handler(
    _request: Request,
    err: UsernameExistsError,
) -> Response:
    """Exception-Handling für UsernameExistsError.

    :param err: Exception, falls der Username für den neuen Patienten bereits existiert
    :return: Response mit Statuscode 422
    :rtype: Response
    """
    return create_problem_details(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(err),
    )


@app.exception_handler(VersionOutdatedError)
def version_outdated_error_handler(
    _request: Request,
    err: VersionOutdatedError,
) -> Response:
    """Exception-Handling für VersionOutdatedError.

    :param _err: Exception, falls die Versionsnummer zum Aktualisieren veraltet ist
    :return: Response mit Statuscode 412
    :rtype: Response
    """
    return create_problem_details(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        detail=str(err),
    )
