# ruff: noqa: S101, S106, D103, ARG005
# pylint: disable=redefined-outer-name

"""Unit-Tests fuer find_by_id() von ArtistService."""

from dataclasses import asdict
from datetime import date

from pytest import fixture, mark, raises

from chora.entity.artist import Artist
from chora.entity.vertrag import Vertrag
from chora.security.role import Role
from chora.security.user import User
from chora.service.artist_dto import ArtistDTO
from chora.service.artist_service import ArtistService
from chora.service.exceptions import ForbiddenError, NotFoundError


@fixture(name="session_mock")
def _session_mock(mocker):
    session = mocker.Mock()
    mocker.patch(
        "chora.service.artist_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


def _user(*, username: str, roles: list[Role]) -> User:
    return User(
        username=username,
        email="mock@email.test",
        nachname="Mock",
        vorname="Mock",
        roles=roles,
        password="mockpass",
    )


def _artist(*, artist_id: int, username: str) -> Artist:
    artist = Artist(
        id=artist_id,
        name="Mock Artist",
        email="mock@email.test",
        geburtsdatum=date(1995, 1, 31),
        username=username,
        songs=[],
        vertrag=None,
        version=0,
        erzeugt=None,
        aktualisiert=None,
    )
    artist.vertrag = Vertrag(
        id=artist_id,
        startdatum=date(2020, 1, 1),
        enddatum=date(2030, 1, 1),
        dauer=120,
        firma="Mock Records",
        gehalt=100_000.0,
        artist_id=artist_id,
        artist=artist,
    )
    return artist


@mark.unit
@mark.unit_find_by_id
def test_find_by_id(artist_service, session_mock) -> None:
    artist_id = 1
    username = "mocktest"
    user = _user(username=username, roles=[Role.ADMIN])
    artist = _artist(artist_id=artist_id, username=username)
    artist_dto_expected = ArtistDTO(artist)

    session_mock.commit.return_value = None
    artist_service.repo.find_by_id = lambda **_: artist

    artist_dto = artist_service.find_by_id(artist_id=artist_id, user=user)

    assert asdict(artist_dto) == asdict(artist_dto_expected)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found(artist_service: ArtistService, session_mock) -> None:
    _ = session_mock
    artist_id = 999
    user = _user(username="mocktest", roles=[Role.ADMIN])

    artist_service.repo.find_by_id = lambda **_: None

    with raises(NotFoundError) as err:
        artist_service.find_by_id(artist_id=artist_id, user=user)

    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"
    assert err.value.artist_id == artist_id


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_found_not_admin(
    artist_service: ArtistService,
    session_mock,
) -> None:
    _ = session_mock
    artist_id = 999
    user = _user(username="mocktest", roles=[])

    artist_service.repo.find_by_id = lambda **_: None

    with raises(ForbiddenError) as err:
        artist_service.find_by_id(artist_id=artist_id, user=user)

    assert err.type == ForbiddenError


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_not_admin_same_user(artist_service, session_mock) -> None:
    artist_id = 1
    username = "mocktest"
    user = _user(username=username, roles=[Role.USER])
    artist = _artist(artist_id=artist_id, username=username)
    artist_dto_expected = ArtistDTO(artist)

    session_mock.commit.return_value = None
    artist_service.repo.find_by_id = lambda **_: artist

    artist_dto = artist_service.find_by_id(artist_id=artist_id, user=user)

    assert asdict(artist_dto) == asdict(artist_dto_expected)


@mark.unit
@mark.unit_find_by_id
def test_find_by_id_other_user_forbidden(artist_service, session_mock) -> None:
    _ = session_mock
    artist_id = 1
    user = _user(username="other", roles=[Role.USER])
    artist = _artist(artist_id=artist_id, username="mocktest")

    artist_service.repo.find_by_id = lambda **_: artist

    with raises(ForbiddenError) as err:
        artist_service.find_by_id(artist_id=artist_id, user=user)

    assert err.type == ForbiddenError
