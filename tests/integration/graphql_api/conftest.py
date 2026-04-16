# noqa: RUF100
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

"""Fixture für pytest: Neuladen der Datenbank."""

from pytest import fixture

from tests.integration.common_test import (  # ty:ignore[unresolved-import]
    check_readiness,
    db_populate,
    keycloak_populate,
)

# Erläuterung der Fixtures in tests\test\conftest.py


SESSION_SCOPE = "session"
FUNCTION_SCOPE = "function"


@fixture(scope=SESSION_SCOPE, autouse=True)
def check_readiness_per_session() -> None:
    """Fixture, um die Readiness des Appservers zu prüfen."""
    check_readiness()
    # Ausgabe in report.html im Wurzelverzeichnis des Projekts
    print("Appserver ist 'ready'")


@fixture(scope=FUNCTION_SCOPE, autouse=True)
def populate_per_test() -> None:
    """Fixture, um DB und Keycloak vor jedem Test neu zu laden."""
    db_populate()
    print("DB ist neu geladen")
    keycloak_populate()
    print("Keycloak ist neu geladen")
