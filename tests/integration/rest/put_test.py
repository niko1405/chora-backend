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
    ARTIST_ALICE_EMAIL,
    ARTIST_ALICE_ID,
    ARTIST_BRUNO_EMAIL,
    ARTIST_BRUNO_ID,
    ARTIST_CLEO_EMAIL,
    ARTIST_CLEO_ID,
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


@mark.rest
@mark.put_request
def test_put_email_exists() -> None:
    """Teste Ablehnung bei doppelter E-Mail."""
    # arrange
    # Aktualisiere Bruno mit Alices Email
    artist_id: Final = ARTIST_BRUNO_ID
    
    # Get current version
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    # Versuche Bruno mit Alices Email zu aktualisieren (sollte fehlschlagen)
    updated_artist: Final = {
        "name": "Bruno Echo",
        "username": "bruno",
        "email": ARTIST_ALICE_EMAIL,  # Alice's Email
        "geburtsdatum": "1992-07-23",
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
    assert response.status_code == HTTPStatus.CONFLICT
    assert ARTIST_ALICE_EMAIL in response.text


@mark.rest
@mark.put_request
def test_put_ohne_versionsnr() -> None:
    """Teste Ablehnung ohne If-Match Header."""
    # arrange
    artist_id: Final = ARTIST_CLEO_ID
    
    updated_artist: Final = {
        "name": "Cleo Drift Updated",
        "username": "cleo",
        "email": ARTIST_CLEO_EMAIL,
        "geburtsdatum": "1998-11-05",
    }
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}  # Kein If-Match!

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=updated_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@mark.rest
@mark.put_request
def test_put_alte_versionsnr() -> None:
    """Teste 412-Fehler bei alter Versionsnummer."""
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
        "email": "alice.old.version@acme.de",
        "geburtsdatum": "1995-03-12",
    }
    token: Final = login()
    # Verwende alte Version (um 1 gesenkt)
    old_version = max(0, current_version - 1) if current_version > 0 else 0
    headers = {"If-Match": f'"{old_version}"', "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=updated_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@mark.rest
@mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    """Teste 412-Fehler bei ungültiger Versionsnummer."""
    # arrange
    artist_id: Final = ARTIST_BRUNO_ID
    
    updated_artist: Final = {
        "name": "Bruno Echo Updated",
        "username": "bruno",
        "email": "bruno.invalid.version@acme.de",
        "geburtsdatum": "1992-07-23",
    }
    token: Final = login()
    headers = {"If-Match": '"invalid-version"', "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=updated_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@mark.rest
@mark.put_request
def test_put_versionsnr_ohne_quotes() -> None:
    """Teste 412-Fehler bei Versionsnummer ohne Anführungszeichen."""
    # arrange
    artist_id: Final = ARTIST_CLEO_ID
    
    # Get current version
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    updated_artist: Final = {
        "name": "Cleo Drift Updated",
        "username": "cleo",
        "email": "cleo.no.quotes@acme.de",
        "geburtsdatum": "1998-11-05",
    }
    token: Final = login()
    # Ohne Anführungszeichen um die Version
    headers = {"If-Match": str(current_version), "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=updated_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
