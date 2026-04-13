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

"""Tests für DELETE."""

from http import HTTPStatus
from typing import Final

from httpx import delete, post
from pytest import mark

from tests.integration.common_test import create_artist_payload, ctx, login, rest_url


@mark.rest
@mark.delete_request
def test_delete() -> None:
    # arrange
    artist = create_artist_payload(marker="delete")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    # act
    token: Final = login()
    response: Final = delete(
        f"{rest_url}/{artist_id}",
        headers={"Authorization": f"Bearer {token}"},
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT


@mark.rest
@mark.delete_request
def test_delete_not_found() -> None:
    # arrange
    artist_id: Final = 999999

    # act
    token: Final = login()
    response: Final = delete(
        f"{rest_url}/{artist_id}",
        headers={"Authorization": f"Bearer {token}"},
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
