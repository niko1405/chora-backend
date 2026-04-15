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

"""Tests fuer PUT bei Artists."""

from http import HTTPStatus
from typing import Final

from httpx import get, post, put
from pytest import mark

from tests.integration.common_test import create_artist_payload, ctx, login, rest_url

EMAIL_UPDATE: Final = "artist.update@acme.de"
SONG_ID_ALICE_FIRST: Final = 3010


@mark.rest
@mark.put_request
def test_put() -> None:
    # arrange
    artist = create_artist_payload(marker="putok")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    # Get current version
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    geaenderter_artist: Final = {
        "name": "Artistput",
        "username": "artist-putok",
        "email": EMAIL_UPDATE,
        "geburtsdatum": "1990-01-09",
        "songs": [SONG_ID_ALICE_FIRST],
    }
    token: Final = login()
    headers = {"If-Match": f'"{current_version}"', "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=geaenderter_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@mark.rest
@mark.put_request
def test_put_invalid() -> None:
    # arrange
    artist = create_artist_payload(marker="putinvalid")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    # Get current version
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    geaenderter_artist_invalid: Final = {
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
        json=geaenderter_artist_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "name" in response.text
    assert "email" in response.text
    assert "geburtsdatum" in response.text


@mark.rest
@mark.put_request
def test_put_nicht_vorhanden() -> None:
    # arrange
    artist_id: Final = 999999
    if_match: Final = '"0"'
    geaenderter_artist: Final = {
        "name": "Artistput",
        "username": "artist-notfound",
        "email": EMAIL_UPDATE,
        "geburtsdatum": "1990-01-03",
    }
    token: Final = login()
    headers = {"If-Match": if_match, "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=geaenderter_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.put_request
def test_put_email_exists() -> None:
    # arrange
    artist_a = create_artist_payload(marker="puta")
    artist_b = create_artist_payload(marker="putb")
    create_a: Final = post(rest_url, json=artist_a, verify=ctx)
    create_b: Final = post(rest_url, json=artist_b, verify=ctx)
    assert create_a.status_code == HTTPStatus.CREATED
    assert create_b.status_code == HTTPStatus.CREATED
    location_b = create_b.headers.get("Location")
    assert location_b is not None
    artist_b_id: Final = int(location_b.rsplit("/", maxsplit=1)[-1])

    geaenderter_artist: Final = {
        "name": "ArtistConflict",
        "email": artist_a["email"],
        "geburtsdatum": "1990-01-09",
    }
    token: Final = login()
    headers = {"If-Match": '"0"', "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_b_id}",
        json=geaenderter_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert artist_a["email"] in response.text


@mark.rest
@mark.put_request
def test_put_ohne_versionsnr() -> None:
    # arrange
    artist = create_artist_payload(marker="putnoversion")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    geaenderter_artist: Final = {
        "name": "Aliceput",
        "username": "artist-noversion",
        "email": EMAIL_UPDATE,
        "geburtsdatum": "1990-01-03",
    }


@mark.rest
@mark.put_request
def test_put_alte_versionsnr() -> None:
    # arrange
    artist = create_artist_payload(marker="putoldversion")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    if_match: Final = '"-1"'
    geaenderter_artist: Final = {
        "name": "Aliceput",
        "username": "artist-oldversion",
        "email": EMAIL_UPDATE,
        "geburtsdatum": "1990-01-03",
    }


@mark.rest
@mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    # arrange
    artist = create_artist_payload(marker="putinvalidversion")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    if_match: Final = '"xy"'
    geaenderter_artist: Final = {
        "name": "Aliceput",
        "username": "artist-invalidversion",
        "email": EMAIL_UPDATE,
        "geburtsdatum": "1990-01-03",
    }
    token: Final = login()
    headers = {"If-Match": if_match, "Authorization": f"Bearer {token}"}

    # act
    response: Final = put(
        f"{rest_url}/{artist_id}",
        json=geaenderter_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
    assert not response.text


@mark.rest
@mark.put_request
def test_put_versionsnr_ohne_quotes() -> None:
    # arrange
    artist = create_artist_payload(marker="putnoquotes")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    if_match: Final = "0"
    geaenderter_artist: Final = {
        "name": "Aliceput",
        "username": "artist-noquotes",
        "email": EMAIL_UPDATE,
        "geburtsdatum": "1990-01-03",
    }
