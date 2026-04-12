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

"""Tests fuer GET mit Query-Parametern bei Artists."""

from http import HTTPStatus
from typing import Final

from tests.integration.common_test import create_artist_payload, ctx, rest_url
from httpx import get, post
from pytest import mark


@mark.rest
@mark.get_request
@mark.parametrize("marker", ["mailone", "mailtwo"])
def test_get_by_email(marker: str) -> None:
    # arrange
    artist = create_artist_payload(marker=marker)
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    params = {"email": artist["email"]}

    # act
    response: Final = get(rest_url, params=params, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    artist_response = content[0]
    assert artist_response is not None
    assert artist_response.get("email") == artist["email"]
    assert artist_response.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("email", ["nicht@vorhanden.com", "nobody@example.org"])
def test_get_by_email_not_found(email: str) -> None:
    params = {"email": email}

    # act
    response: Final = get(rest_url, params=params, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("name", ["Alpha Artist", "Beta Artist"])
def test_get_by_name(name: str) -> None:
    # arrange
    artist = create_artist_payload()
    artist["name"] = name
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    params = {"name": name.split()[0]}

    # act
    response: Final = get(rest_url, params=params, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    content: Final = response_body["content"]
    assert len(content) >= 1
    for artist_response in content:
        name_response = artist_response.get("name")
        assert name_response is not None and isinstance(name_response, str)
        assert params["name"].lower() in name_response.lower()
        assert artist_response.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("name", ["NotFound", "XYZ"],)
def test_get_by_name_not_found(name: str) -> None:
    params = {"name": name}
    response: Final = get(rest_url, params=params, verify=ctx)
    assert response.status_code == HTTPStatus.NOT_FOUND
