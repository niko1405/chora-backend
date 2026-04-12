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

"""Tests fuer POST bei Artists."""

from http import HTTPStatus
from re import search
from typing import Final

from tests.integration.common_test import create_artist_payload, ctx, rest_url
from httpx import post
from pytest import mark

@mark.rest
@mark.post_request
def test_post() -> None:
    # arrange
    neuer_artist: Final = create_artist_payload(marker="postok")
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location: Final = response.headers.get("Location")
    assert location is not None
    int_pattern: Final = "[1-9][0-9]*$"
    assert search(int_pattern, location) is not None
    assert not response.text


@mark.rest
@mark.post_request
def test_post_invalid() -> None:
    # arrange
    neuer_artist_invalid: Final = {
        "name": "falscher_name_123",
        "email": "falsche_email@",
        "geburtsdatum": "2030-02-01",
        "vertrag": {
            "startdatum": "2030-01-01",
            "enddatum": "2029-01-01",
            "dauer": 0,
            "firma": "",
            "gehalt": -1,
        },
        "songs": [
            {
                "titel": "Titel123",
                "genres": ["ROCK"],
                "erscheinungsdatum": "2030-01-01",
                "dauer": 0,
            }
        ],
        "username": "testrestinvalid",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_artist_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.text
    assert "name" in body
    assert "email" in body
    assert "dauer" in body
    assert "gehalt" in body


@mark.rest
@mark.post_request
def test_post_email_exists() -> None:
    # arrange
    neuer_artist: Final = create_artist_payload(marker="emailexists")
    headers = {"Content-Type": "application/json"}
    first_response: Final = post(
        rest_url,
        json=neuer_artist,
        headers=headers,
        verify=ctx,
    )
    assert first_response.status_code == HTTPStatus.CREATED

    # act
    response: Final = post(
        rest_url,
        json=neuer_artist,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert neuer_artist["email"] in response.text


@mark.rest
@mark.post_request
def test_post_invalid_json() -> None:
    # arrange
    json_invalid: Final = '{"name" "Artist"}'
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=json_invalid,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "should be a valid dictionary" in response.text
