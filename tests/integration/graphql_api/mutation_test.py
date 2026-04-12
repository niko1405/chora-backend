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

"""Tests fuer Mutations mit GraphQL."""

from http import HTTPStatus
from typing import Final

from tests.integration.common_test import ctx, graphql_url
from httpx import post
from pytest import mark


@mark.graphql
@mark.mutation
def test_login_mutation() -> None:
    # arrange
    query: Final = {
        "query": """
            mutation {
                login(username: "admin", password: "p") {
                    token
                    roles
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, verify=ctx)

    # assert
    assert response is not None
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    login_data = response_body["data"]["login"]
    assert isinstance(login_data["token"], str)
    assert len(login_data["token"]) > 0
    assert isinstance(login_data["roles"], list)
    assert response_body.get("errors") is None


@mark.graphql
@mark.mutation
def test_create_invalid() -> None:
    # arrange
    query: Final = {
        "query": """
            mutation {
                create(
                    artistInput: {
                        name: "Invalid"
                        genre: "Rock"
                        alter: 20
                        email: "falsche_email@"
                        vertrag: {
                            artistId: 1
                            agentId: 1
                            startDate: "2026-01-01"
                            endDate: "2026-12-31"
                        }
                        songs: [
                            {
                                title: "MySong"
                                duration: 120
                            }
                        ]
                        username: "invalid"
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(graphql_url, json=query, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"] is None
    errors: Final = response_body["errors"]
    assert isinstance(errors, list)
    assert len(errors) >= 1
