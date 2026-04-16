# ruff: noqa: S101, D103  # noqa: RUF100
# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Allgemeine Daten für die Tests."""

from http import HTTPStatus
from pathlib import Path
from ssl import create_default_context
from typing import Any, Final

from httpx import get, post

__all__ = [
    "ARTIST_ADMIN_ID",
    "ARTIST_ALICE_EMAIL",
    "ARTIST_ALICE_ID",
    "ARTIST_BRUNO_EMAIL",
    "ARTIST_BRUNO_ID",
    "ARTIST_CLEO_EMAIL",
    "ARTIST_CLEO_ID",
    "BASE_URL",
    "DB_POPULATE_PATH",
    "GRAPHQL_PATH",
    "GRAPHQL_URL",
    "HEALTH_URL",
    "KEYCLOAK_POPULATE_PATH",
    "PASSWORD_ADMIN",
    "REST_PATH",
    "REST_URL",
    "SONG_ID_1",
    "SONG_ID_2",
    "SONG_ID_3",
    "SONG_ID_4",
    "SONG_REST_PATH",
    "SONG_REST_URL",
    "TIMEOUT",
    "TOKEN_PATH",
    "USERNAME_ADMIN",
    "create_artist_payload",
    "ctx",
    "db_populate",
    "keycloak_populate",
    "login",
    "login_graphql",
]

SCHEMA: Final = "https"
PORT: Final = 8000
# Fallback IPv6 -> IPv4 insbesondere bei Windows vermeiden; deshalb kein "localhost"
HOST: Final = "127.0.0.1"
BASE_URL: Final = f"{SCHEMA}://{HOST}:{PORT}"
REST_PATH: Final = "/rest/artists"
REST_URL: Final = f"{BASE_URL}{REST_PATH}"
SONG_REST_PATH: Final = "/rest/songs"
SONG_REST_URL: Final = f"{BASE_URL}{SONG_REST_PATH}"
HEALTH_URL: Final = f"{BASE_URL}/health"
GRAPHQL_PATH: Final = "/graphql"
GRAPHQL_URL: Final = f"{BASE_URL}/graphql"
TOKEN_PATH: Final = "/auth/token"  # noqa: S105
DB_POPULATE_PATH: Final = "/dev/db_populate"
KEYCLOAK_POPULATE_PATH: Final = "/dev/keycloak_populate"
USERNAME_ADMIN: Final = "admin"
PASSWORD_ADMIN: Final = "p"  # noqa: S105  # NOSONAR
TIMEOUT: Final = 2
# timeout: Final = 5
CERTIFICATE: Final = str(Path("tests") / "integration" / "certificate.crt")
ctx = create_default_context(cafile=CERTIFICATE)


def check_readiness() -> None:
    """Pruefe, ob die Anwendung bereit ist, Anfragen zu bearbeiten."""
    response: Final = get(f"{HEALTH_URL}/readiness", verify=ctx)
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"readiness mit Statuscode {response.status_code}")
    response_body: Final = response.json()
    if not isinstance(response_body, dict):
        raise RuntimeError("readiness ohne Dictionary im Response-Body")
    status: Final[Any | None] = response_body.get("db")
    if status != "up":
        raise RuntimeError(f"readiness mit Meldungstext {status}")


def login(
    username: str = USERNAME_ADMIN,
    password: str = PASSWORD_ADMIN,  # NOSONAR
) -> str:
    """Hole ein JWT-Token für die Authentifizierung."""
    login_data: Final = {"username": username, "password": password}
    response: Final = post(
        f"{BASE_URL}{TOKEN_PATH}",
        json=login_data,
        verify=ctx,
        timeout=TIMEOUT,
    )
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"login() mit Statuscode {response.status_code}")
    response_body: Final = response.json()
    token: Final = response_body.get("token")
    if token is None or not isinstance(token, str):
        raise RuntimeError(f"login() mit ungueltigem Token: type={type(token)}")
    return token


def login_graphql(
    username: str = USERNAME_ADMIN,
    password: str = PASSWORD_ADMIN,  # NOSONAR
) -> str:
    """Hole ein JWT-Token für die Authentifizierung."""
    login_query: Final = {
        "query": f'mutation {{ login(username: "{username}", password: "{password}") {{ token }} }}'  # noqa: E501
    }
    response: Final = post(
        f"{BASE_URL}{GRAPHQL_PATH}",
        json=login_query,
        verify=ctx,
        timeout=TIMEOUT,
    )
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"login() mit Statuscode {response.status_code}")
    response_body: Final = response.json()
    token: Final = response_body.get("data").get("login").get("token")
    if token is None or not isinstance(token, str):
        raise RuntimeError(f"login_query() mit ungueltigem Token: type={type(token)}")
    return token


def db_populate() -> None:
    """Populiere die Datenbank mit Testdaten."""
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}
    response: Final = post(
        f"{BASE_URL}{DB_POPULATE_PATH}",
        headers=headers,
        verify=ctx,
    )
    assert response.status_code == HTTPStatus.OK


def keycloak_populate() -> None:
    """Populiere Keycloak mit Testdaten."""
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}
    response: Final = post(
        f"{BASE_URL}{KEYCLOAK_POPULATE_PATH}",
        headers=headers,
        verify=ctx,
    )
    assert response.status_code == HTTPStatus.OK


# Test-Daten aus den CSV-Dateien (db_populate)
ARTIST_ADMIN_ID: Final = 1000
ARTIST_ALICE_ID: Final = 1010
ARTIST_ALICE_EMAIL: Final = "alice.neon@acme.de"
ARTIST_BRUNO_ID: Final = 1020
ARTIST_BRUNO_EMAIL: Final = "bruno.echo@acme.de"
ARTIST_CLEO_ID: Final = 1030
ARTIST_CLEO_EMAIL: Final = "cleo.drift@acme.de"

SONG_ID_1: Final = 3000  # Control Room
SONG_ID_2: Final = 3010  # Glass Horizon
SONG_ID_3: Final = 3020  # Night Transit
SONG_ID_4: Final = 3030  # Signal Bloom


def create_artist_payload() -> dict[str, Any]:
    """Erzeuge gueltige Testdaten fuer einen neuen Artist (für POST/DELETE Tests)."""
    return {
        "name": "Test Artist",
        "email": "test.artist@acme.de",
        "geburtsdatum": "1995-01-01",
        "username": "test-artist",
        "vertrag": {
            "startdatum": "2020-01-01",
            "enddatum": "2030-01-01",
            "dauer": 120,
            "firma": "Test Records",
            "gehalt": 75000,
        },
        "songs": [],
    }
