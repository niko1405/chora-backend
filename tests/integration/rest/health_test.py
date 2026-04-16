# ruff: noqa: S101, D103  # noqa: RUF100
# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Tests für GET mit QUery-Parameter."""

from http import HTTPStatus
from typing import Any, Final

from httpx import get
from pytest import mark

from tests.integration.common_test import ctx, HEALTH_URL


@mark.rest
@mark.health
def test_liveness() -> None:
    """Test für die Liveness-Endpoint."""
    # act
    response: Final = get(f"{HEALTH_URL}/liveness", verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    status: Final[Any | None] = response_body.get("status")
    assert status == "up"


@mark.rest
@mark.health
def test_readiness() -> None:
    """Test für die Readiness-Endpoint."""
    # act
    response: Final = get(f"{HEALTH_URL}/readiness", verify=ctx)

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    status: Final[Any | None] = response_body.get("db")
    assert status == "up"
