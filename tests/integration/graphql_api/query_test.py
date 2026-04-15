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

"""Tests fuer Queries mit GraphQL."""

from http import HTTPStatus
from typing import Final

from tests.integration.common_test import (
    create_artist_payload,
    ctx,
    graphql_url,
    login_graphql,
    rest_url,
)
from httpx import post
from pytest import mark

@mark.graphql
@mark.query
def test_query_id() -> None:
    # arrange
    artist = create_artist_payload(marker="gqlid")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id = int(location.rsplit("/", maxsplit=1)[-1])

    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query_str = """
        {
            artist(artistId: \"__ARTIST_ID__\") {
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
    assert artist_response["email"] == artist["email"]
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_id_notfound() -> None:
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
    # arrange
    artist = create_artist_payload(marker="gqlemail")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    email = artist["email"]

    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query_str = """
        {
            artists(suchparameter: {email: \"__EMAIL__\"}) {
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
    assert artists[0]["email"] == artist["email"]
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_artists_by_email_notfound() -> None:
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
    # arrange
    artist = create_artist_payload(marker="gqlname")
    artist["name"] = "Graph Artist"
    artist["username"] = "graph-artist"
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED

    token: Final = login_graphql()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    query: Final = {
        "query": """
            {
                artists(suchparameter: {name: "Graph"}) {
                    id
                    version
                    name
                    email
                    geburtsdatum
                    username
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
    assert len(artists) > 0
    assert response_body.get("errors") is None


@mark.graphql
@mark.query
def test_query_artists_by_name_notfound() -> None:
    # arrange
    token: Final = login_graphql()
    assert token is not None
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
