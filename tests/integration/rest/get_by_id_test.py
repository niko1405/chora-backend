# ruff: noqa: S101, D103, I001  # noqa: RUF100
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

"""Tests fuer GET mit Pfadparametern bei Songs eines Artists."""

from http import HTTPStatus
from typing import Final
from httpx import get
from pytest import mark
from tests.integration.common_test import ctx, REST_URL, SONG_REST_URL


ARTIST_ID_ADMIN: Final = 1000
ARTIST_ID_ALICE: Final = 1010
SONG_ID_ADMIN: Final = 3000
SONG_ID_ALICE_FIRST: Final = 3010


@mark.rest
@mark.get_request
def test_get_artist_by_id() -> None:
    """Teste GET-Anfrage mit vorhandener Artist-ID."""
    # act
    response: Final = get(
        f"{REST_URL}/{ARTIST_ID_ADMIN}",
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body.get("id") == ARTIST_ID_ADMIN


@mark.rest
@mark.get_request
def test_get_artist_by_id_not_found() -> None:
    """Teste GET-Anfrage mit nicht vorhandener Artist-ID."""
    response: Final = get(
        f"{REST_URL}/999999",
        verify=ctx,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
def test_get_song_by_id() -> None:
    """Teste GET-Anfrage mit vorhandener Song-ID."""
    # act
    response: Final = get(
        f"{SONG_REST_URL}/{SONG_ID_ADMIN}",
        params={"artist_id": ARTIST_ID_ADMIN},
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body.get("id") == SONG_ID_ADMIN
    assert ARTIST_ID_ADMIN in response_body.get("artist_ids", [])


@mark.rest
@mark.get_request
def test_get_songs_by_artist_id() -> None:
    """Teste GET-Anfrage mit vorhandener Artist-ID."""
    response: Final = get(
        SONG_REST_URL,
        params={"artist_id": ARTIST_ID_ALICE},
        verify=ctx,
    )
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    content = response_body.get("content")
    assert isinstance(content, list)
    assert len(content) >= 1
    song_ids = {song.get("id") for song in content}
    assert SONG_ID_ALICE_FIRST in song_ids


@mark.rest
@mark.get_request
def test_get_songs_by_artist_id_not_found() -> None:
    """Teste GET-Anfrage mit nicht vorhandener Artist-ID."""
    response: Final = get(
        SONG_REST_URL,
        params={"artist_id": 999999},
        verify=ctx,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("artist_id,song_id", [(999999, 1000), (1000, 999999)])
def test_get_song_by_id_not_found(artist_id: int, song_id: int) -> None:
    """Teste GET-Anfrage mit nicht vorhandener Artist-ID oder Song-ID."""
    response: Final = get(
        f"{SONG_REST_URL}/{song_id}",
        params={"artist_id": artist_id},
        verify=ctx,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
