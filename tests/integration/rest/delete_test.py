# ruff: noqa: S101, D103  # noqa: RUF100
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

from httpx import delete
from pytest import mark

from tests.integration.common_test import ARTIST_ALICE_ID, ctx, login, REST_URL


@mark.rest
@mark.delete_request
def test_delete() -> None:
    """Teste erfolgreichen DELETE eines vorhandenen Artists."""
    # act
    token: Final = login()
    response: Final = delete(
        f"{REST_URL}/{ARTIST_ALICE_ID}",
        headers={"Authorization": f"Bearer {token}"},
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT


@mark.rest
@mark.delete_request
def test_delete_not_found() -> None:
    """Teste DELETE eines nicht vorhandenen Artists."""
    # arrange
    artist_id: Final = 999999

    # act
    token: Final = login()
    response: Final = delete(
        f"{REST_URL}/{artist_id}",
        headers={"Authorization": f"Bearer {token}"},
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
