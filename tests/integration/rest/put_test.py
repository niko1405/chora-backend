# ruff: noqa: S101, D103
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

"""Tests fuer PUT bei Artists - verwendet Testdaten aus CSV."""

from http import HTTPStatus
from typing import Final

from httpx import get, put
from pytest import mark

from tests.integration.common_test import (
    ARTIST_ALICE_ID,
    ARTIST_BRUNO_ID,
    SONG_ID_1,
    SONG_ID_2,
    ctx,
    login,
    rest_url,
)

EMAIL_UPDATE: Final = "artist.update@acme.de"


@mark.rest
@mark.put_request
def test_put() -> None:
    """Teste erfolgreiche Aktualisierung eines vorhandenen Artists."""
    # arrange
    artist_id: Final = ARTIST_ALICE_ID

    # Get current version
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    updated_artist: Final = {
        "name": "Alice Neon Updated",
        "username": "alice",
        "email": "alice.updated@acme.de",
        "geburtsdatum": "1995-03-12",
        "vertrag": {
            "startdatum": "2026-01-01",
            "enddatum": "2028-12-31",
            "dauer": 36,
            "firma": "Sony",
            "gehalt": 180000.0
        },
        "songs": [SONG_ID_1, SONG_ID_2],
    }
    token: Final = login()
    headers = {"If-Match": f'"{current_version}"', "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=updated_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@mark.rest
@mark.put_request
def test_put_invalid() -> None:
    """Teste Ablehnung ungültiger Daten beim Update."""
    # arrange
    artist_id: Final = ARTIST_BRUNO_ID

    # Get current version
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    invalid_artist: Final = {
        "name": "falscher_name_123",
        "username": "invalid-user",
        "email": "falsche_email_put@",
        "geburtsdatum": "2035-02-04",
    }
    token: Final = login()
    headers = {"If-Match": f'"{current_version}"', "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=invalid_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    response_text = response.text.lower()
    # Fehler für ungültige Felder sollten vorhanden sein
    assert any(field in response_text for field in ["name", "email", "geburtsdatum"])


@mark.rest
@mark.put_request
def test_put_nicht_vorhanden() -> None:
    """Teste 404-Fehler für nicht vorhandenen Artist."""
    # arrange
    artist_id: Final = 999999
    if_match: Final = '"0"'
    updated_artist: Final = {
        "name": "Nonexistent Artist",
        "username": "nonexistent",
        "email": "nonexistent@acme.de",
        "geburtsdatum": "1990-01-03",
        "vertrag": {
            "startdatum": "2026-01-01",
            "enddatum": "2028-12-31",
            "dauer": 36,
            "firma": "Sony",
            "gehalt": 180000.0
        },
        "songs": []
    }
    token: Final = login()
    headers = {"If-Match": if_match, "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=updated_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND
