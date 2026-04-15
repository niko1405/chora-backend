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

"""Tests fuer Queries mit GraphQL - verwendet Testdaten aus CSV."""

from http import HTTPStatus
from typing import Final

from httpx import post
from pytest import mark

from tests.integration.common_test import (
    ARTIST_ALICE_EMAIL,
    ARTIST_ALICE_ID,
    ctx,
    graphql_url,
    login_graphql,
)


@mark.graphql
@mark.query
def test_query_id() -> None:
    """Teste GraphQL Query mit Artist ID (aus CSV)."""
    # arrange
    artist_id = ARTIST_ALICE_ID

    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query_str = """
        {
            artist(artistId: "__ARTIST_ID__") {
                id
                version
                name
                email
                geburtsdatum
                username
                vertrag {
                    id
                    firma
                    dauer
                }
            }
        }
    """.replace("__ARTIST_ID__", str(artist_id))
    query: Final = {"query": query_str}

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    data: Final = response_body["data"]
    assert data is not None
    artist_response: Final = data["artist"]
    assert isinstance(artist_response, dict)
    assert artist_response["id"] == artist_id
    assert artist_response["email"] == ARTIST_ALICE_EMAIL
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_id_notfound() -> None:
    """Teste GraphQL Query für nicht vorhandene ID."""
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                artist(artistId: "999999") {
                    name
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"]["artist"] is None
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_artists_by_email() -> None:
    """Teste GraphQL Query nach E-Mail (aus CSV)."""
    # arrange
    email = ARTIST_ALICE_EMAIL

    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query_str = """
        {
            artists(suchparameter: {email: "__EMAIL__"}) {
                id
                version
                name
                email
                geburtsdatum
                username
            }
        }
    """.replace("__EMAIL__", email)
    query: Final = {"query": query_str}

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    artists: Final = response_body["data"]["artists"]
    assert isinstance(artists, list)
    assert len(artists) > 0
    assert artists[0]["email"] == email
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_artists_by_email_notfound() -> None:
    """Teste GraphQL Query nach nicht vorhandener E-Mail."""
    # arrange
    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                artists(suchparameter: {email: "not.found@acme.com"}) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    artists: Final = response_body["data"]["artists"]
    assert isinstance(artists, list)
    assert len(artists) == 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_artists_by_name() -> None:
    """Teste GraphQL Query nach Name (aus CSV)."""
    # arrange
    # Alice Neon enthält "Neon" oder "Alice"
    search_name = "Alice"

    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query_str = """
        {
            artists(suchparameter: {name: "__NAME__"}) {
                id
                version
                name
                email
                geburtsdatum
                username
            }
        }
    """.replace("__NAME__", search_name)
    query: Final = {"query": query_str}

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    artists: Final = response_body["data"]["artists"]
    assert isinstance(artists, list)
    assert len(artists) > 0
    # Mindestens Alice sollte gefunden werden
    artist_names = [a["name"] for a in artists]
    assert any("Alice" in name for name in artist_names)
    assert response_body.get("errors") is None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                artists(suchparameter: {name: "Nichtvorhanden"}) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, headers=headers, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    artists: Final = response_body["data"]["artists"]
    assert isinstance(artists, list)
    assert len(artists) == 0
