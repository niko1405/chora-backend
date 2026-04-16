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

"""Tests fuer GET mit Query-Parametern bei Artists."""

from http import HTTPStatus
from typing import Final
from httpx import get
from pytest import mark
from tests.integration.common_test import (
    ARTIST_ALICE_EMAIL,
    ARTIST_BRUNO_EMAIL,
    ctx,
    REST_URL,
)


@mark.rest
@mark.get_request
@mark.parametrize("email", [ARTIST_ALICE_EMAIL, ARTIST_BRUNO_EMAIL])
def test_get_by_email(email: str) -> None:
    """Teste GET-Anfrage mit vorhandener Email."""
    params = {"email": email}

    # act
    response: Final = get(REST_URL, params=params, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    artist_response = content[0]
    assert artist_response is not None
    assert artist_response.get("email") == email
    assert artist_response.get("id") is not None


@mark.rest
@mark.get_request
@mark.parametrize("email", ["nicht@vorhanden.com", "nobody@example.org"])
def test_get_by_email_not_found(email: str) -> None:
    """Teste GET-Anfrage mit nicht vorhandener Email."""
    params = {"email": email}

    # act
    response: Final = get(REST_URL, params=params, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
@mark.parametrize("name", ["Admin", "Alice", "Bruno"])
def test_get_by_name(name: str) -> None:
    """Teste GET-Anfrage mit vorhandenem Namen."""
    params = {"name": name}

    # act
    response: Final = get(REST_URL, params=params, verify=ctx)

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
@mark.parametrize("name", ["NotFound", "XYZ"])
def test_get_by_name_not_found(name: str) -> None:
    """Teste GET-Anfrage mit nicht vorhandenem Namen."""
    params = {"name": name}
    response: Final = get(REST_URL, params=params, verify=ctx)
    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.get_request
def test_get_with_pagination_disjoint_pages() -> None:
    """Pagination muss disjunkte Seiten ohne doppelte IDs liefern."""
    first_page_response: Final = get(
        REST_URL,
        params={"page": 0, "size": 5},
        verify=ctx,
    )
    second_page_response: Final = get(
        REST_URL,
        params={"page": 1, "size": 5},
        verify=ctx,
    )

    assert first_page_response.status_code == HTTPStatus.OK
    assert second_page_response.status_code == HTTPStatus.OK

    first_body: Final = first_page_response.json()
    second_body: Final = second_page_response.json()

    first_ids: Final = [artist["id"] for artist in first_body["content"]]
    second_ids: Final = [artist["id"] for artist in second_body["content"]]

    assert len(first_ids) == 5
    assert len(second_ids) == 1
    assert set(first_ids).isdisjoint(second_ids)
    assert len(set(first_ids + second_ids)) == first_body["page"]["total_elements"]
