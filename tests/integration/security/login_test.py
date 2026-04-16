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

"""Tests für Login."""

from http import HTTPStatus
from logging import getLogger
from typing import Final

from httpx import post
from pytest import mark

from tests.integration.common_test import (  # ty:ignore[unresolved-import]
    BASE_URL,
    TIMEOUT,
    TOKEN_PATH,
    USERNAME_ADMIN,
    ctx,
    login,
)

# fuer hypercorn: INFO statt DEBUG
getLogger("hpack.hpack").setLevel(level="INFO")
getLogger("hpack.table").setLevel(level="INFO")


@mark.login
def test_login_admin() -> None:
    """Teste Login mit Admin-Benutzer."""
    # act
    token: Final = login()

    # then
    assert isinstance(token, str)
    assert token


@mark.login
def test_login_falsches_passwort() -> None:
    """Teste Login mit falschem Passwort."""
    # arrange
    login_data: Final = {"username": USERNAME_ADMIN, "password": "FALSCHES_PASSWORT"}

    # act
    response: Final = post(
        f"{BASE_URL}{TOKEN_PATH}",
        json=login_data,
        verify=ctx,
        timeout=TIMEOUT,
    )

    # then
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@mark.login
def test_login_ohne_daten() -> None:
    """Teste Login ohne Benutzerdaten."""
    # arrange
    login_data: dict[str, str] = {}

    # act
    response: Final = post(
        f"{BASE_URL}{TOKEN_PATH}",
        json=login_data,
        verify=ctx,
        timeout=TIMEOUT,
    )

    # then
    assert response.status_code == HTTPStatus.UNAUTHORIZED
