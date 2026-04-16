# ruff: noqa: S101  # noqa: RUF100
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

from httpx import post
from pytest import mark

from tests.integration.common_test import (  # ty:ignore[unresolved-import]
    GRAPHQL_URL,
    ctx,
)


@mark.graphql
@mark.mutation
def test_login_mutation() -> None:
    """Teste GraphQL Mutation fuer Login."""
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
    response: Final = post(GRAPHQL_URL, json=query, verify=ctx)

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
    """Teste GraphQL Mutation mit invaliden Daten."""
    # arrange
    query: Final = {
        "query": """
            mutation {
                create(
                    artistInput: {
                        name: "Invalid"
                        geburtsdatum: "invalid"
                        email: "falsche_email@"
                        vertrag: {
                            startdatum: "2026-01-01"
                            enddatum: "2026-12-31"
                            dauer: 12
                            firma: "Invalid Firma"
                            gehalt: 50000.0
                        }
                        songs: [3010]
                        username: "invalid"
                    }
                ) {
                    id
                }
            }
        """,
    }

    # act
    response: Final = post(GRAPHQL_URL, json=query, verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    assert response_body["data"] is None
    errors: Final = response_body["errors"]
    assert isinstance(errors, list)
    assert len(errors) >= 1
