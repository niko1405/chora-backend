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

"""Fixture fuer pytest: Repository und Artist(Write)Service."""

# pylint: disable=redefined-outer-name

from pytest import fixture
from pytest_mock import MockerFixture

from chora.repository.artist_repository import ArtistRepository
from chora.repository.song_repository import SongRepository
from chora.service.artist_service import ArtistService
from chora.service.artist_write_service import ArtistWriteService

# "Fixtures" sind Funktionen, die vor den Test-Funktionen ausgefuehrt werden, um z.B.
# wiederholt benoetigte Daten bereitzustellen (URLs, DB-Verbindungen usw.).
# Vgl.: @BeforeEach und @BeforeAll bei JUnit
# Ein Fixture ist eine Funktion, die i.a. in conftest.py implementiert wird und fuer
# alle Test-Funktionen im gleichen Verzeichnis verwendet werden kann.
# Eine Fixture-Funktion wir dann als erstes Argument an die Test-Funktion übergeben
# oder hat das Argument autouse=True fuer die implizite Uebergabe.
# Jedes Fixture hat einen Scope: function (= default), class, module, package, session.
# Die Reihenfolge ist: session > package > module > class > function (~ BeforeEach).
# module: 1x die Fixture-Funktionen pro Datei mit Test-Funktionen aufrufen
# session: 1x die Fixture-Funktionen in diesem Verzeichnis aufrufen
# session verwendet man fuer aufwaendige Operationen, z.B. Test-DB laden.

# https://docs.pytest.org/en/stable/explanation/fixtures.html
# https://docs.pytest.org/en/stable/how-to/fixtures.html
# Anzeige aller fixtures ausgehend vom Wurzelverzeichnis:   uv run pytest --fixtures


@fixture(name="artist_repository")
def _artist_repository() -> ArtistRepository:
    """Fixture fuer ArtistRepository."""
    return ArtistRepository()


@fixture(name="song_repository")
def _song_repository() -> SongRepository:
    """Fixture fuer SongRepository."""
    return SongRepository()


@fixture(name="artist_service")
def _artist_service(artist_repository: ArtistRepository) -> ArtistService:
    """Fixture fuer ArtistService."""
    return ArtistService(artist_repository)


@fixture(name="user_service_mock")
def _user_service_mock(mocker: MockerFixture):
    """Fixture fuer einen gemockten UserService."""
    service = mocker.Mock()
    service.username_exists.return_value = False
    service.email_exists.return_value = False
    service.create_user.return_value = "12345678-1234-1234-1234-123456789012"
    service.delete_user.return_value = None
    service.update_user.return_value = None
    return service


@fixture(name="artist_write_service")
def _artist_write_service(
    artist_repository: ArtistRepository,
    song_repository: SongRepository,
    user_service_mock,
) -> ArtistWriteService:
    """Fixture fuer ArtistWriteService."""
    return ArtistWriteService(artist_repository, song_repository, user_service_mock)
