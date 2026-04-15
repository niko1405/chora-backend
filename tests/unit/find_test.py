# ruff: noqa: S101, D103, ARG005
# pylint: disable=redefined-outer-name

"""Unit-Tests fuer find() von ArtistService."""

from datetime import date

from pytest import fixture, mark, raises

from chora.entity.artist import Artist
from chora.entity.vertrag import Vertrag
from chora.repository.pageable import Pageable
from chora.repository.slice import Slice
from chora.service.exceptions import NotFoundError


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


def _artist(*, artist_id: int, name: str, email: str) -> Artist:
    artist = Artist(
        id=artist_id,
        name=name,
        email=email,
        geburtsdatum=date(1995, 1, 31),
        username="mock",
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
@mark.unit_find
def test_find_by_name(artist_service, session_mock) -> None:
    name = "Mock Artist"
    artist = _artist(artist_id=1, name=name, email="mock@email.test")
    queryparams = {"name": "Mock"}
    pageable = Pageable(size=5, number=0)

    session_mock.commit.return_value = None
    artist_slice = Slice(content=(artist,), total_elements=1)
    artist_service.repo.find = lambda **_: artist_slice

    result = artist_service.find(suchparameter=queryparams, pageable=pageable)

    assert len(result.content) == 1
    assert result.content[0].name == name


@mark.unit
@mark.unit_find
def test_find_by_name_not_found(artist_service, session_mock) -> None:
    queryparams = {"name": "Notfound"}
    pageable = Pageable(size=5, number=0)

    session_mock.commit.return_value = None
    artist_service.repo.find = lambda **_: Slice(content=(), total_elements=0)

    with raises(NotFoundError) as err:
        artist_service.find(suchparameter=queryparams, pageable=pageable)

    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.get("name") == "Notfound"


@mark.unit
@mark.unit_find
def test_find_by_email(artist_service, session_mock) -> None:
    email = "mock@email.test"
    artist = _artist(artist_id=1, name="Mock Artist", email=email)
    queryparams = {"email": email}
    pageable = Pageable(size=5, number=0)

    session_mock.commit.return_value = None
    artist_service.repo.find = lambda **_: Slice(content=(artist,), total_elements=1)

    result = artist_service.find(suchparameter=queryparams, pageable=pageable)

    assert len(result.content) == 1
    assert result.content[0].email == email


@mark.unit
@mark.unit_find
def test_find_by_email_not_found(artist_service, session_mock) -> None:
    email = "not@found.mock"
    queryparams = {"email": email}
    pageable = Pageable(size=5, number=0)

    session_mock.commit.return_value = None
    artist_service.repo.find = lambda **_: Slice(content=(), total_elements=0)

    with raises(NotFoundError) as err:
        artist_service.find(suchparameter=queryparams, pageable=pageable)

    assert str(err.value) == "Not Found"
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.get("email") == email
