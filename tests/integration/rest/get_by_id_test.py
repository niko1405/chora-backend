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

"""Tests fuer GET mit Pfadparametern bei Songs eines Artists."""

from http import HTTPStatus
from typing import Final

from tests.integration.common_test import create_artist_payload, ctx, rest_url
from httpx import get, post
from pytest import mark


@mark.rest
@mark.get_request
def test_get_song_by_id() -> None:
    # arrange
    artist = create_artist_payload(marker="songbyid")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED

    list_response: Final = get(rest_url, params={"email": artist["email"]}, verify=ctx)
    assert list_response.status_code == HTTPStatus.OK
    artist_response: Final = list_response.json()["content"][0]
    artist_id: Final = artist_response["id"]
    song_id: Final = artist_response["songs"][0]["id"]

    # act
    response: Final = get(
        f"{rest_url}/{artist_id}/songs/{song_id}",
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body.get("id") == song_id
    assert response_body.get("artist_id") == artist_id


@mark.rest
@mark.get_request
@mark.parametrize("artist_id,song_id", [(999999, 1000), (1000, 999999)])
def test_get_song_by_id_not_found(artist_id: int, song_id: int) -> None:
    response: Final = get(
        f"{rest_url}/{artist_id}/songs/{song_id}",
        verify=ctx,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
