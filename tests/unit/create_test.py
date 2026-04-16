# ruff: noqa: S101, D103, ARG005  # noqa: RUF100
# pylint: disable=redefined-outer-name

"""Unit-Tests fuer create() von ArtistWriteService."""

from datetime import date

from pytest import fixture, mark, raises

from chora.entity.artist import Artist
from chora.entity.vertrag import Vertrag
from chora.service.exceptions import EmailExistsError, UsernameExistsError


@fixture(name="session_mock")
def _session_mock(mocker):
    """Stellt einen Mock für die Session bereit,kein echter DB-Zugriff."""
    session = mocker.Mock()
    mocker.patch(
        "chora.service.artist_write_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


def _artist(
    email: str = "mock@email.test",
    username: str | None = "mocktest",
) -> Artist:
    artist = Artist(
        id=None,
        name="Mock Artist",
        email=email,
        geburtsdatum=date(1999, 1, 31),
        username=username,
        songs=[],
        vertrag=None,
        version=0,
        erzeugt=None,
        aktualisiert=None,
    )
    artist.vertrag = Vertrag(
        id=1,
        startdatum=date(2020, 1, 1),
        enddatum=date(2030, 1, 1),
        dauer=120,
        firma="Mock Records",
        gehalt=100_000.0,
        artist_id=1,
        artist=artist,
    )
    return artist


@mark.unit
@mark.unit_create
def test_create(artist_write_service, session_mock, mocker) -> None:
    """Teste Erstellung eines Artists."""
    artist = _artist()

    session_mock.add.return_value = None

    def flush_side_effect() -> None:
        artist.id = 1

    session_mock.flush.side_effect = flush_side_effect
    mocker.patch("chora.service.artist_write_service.send_mail", return_value=None)

    artist_dto = artist_write_service.create(artist=artist)

    assert artist_dto.id == 1


@mark.unit
@mark.unit_create
def test_create_username_none(artist_write_service) -> None:
    """Teste Erstellung eines Artists mit None als Username."""
    artist = _artist(username=None)

    with raises(ValueError) as err:
        artist_write_service.create(artist=artist)

    assert err.type is ValueError


@mark.unit
@mark.unit_create
def test_create_username_exists(artist_write_service, user_service_mock) -> None:
    """Teste Erstellung eines Artists mit bereits vorhandenem Username."""
    artist = _artist()
    user_service_mock.username_exists.return_value = True

    with raises(UsernameExistsError) as err:
        artist_write_service.create(artist=artist)

    assert err.type is UsernameExistsError


@mark.unit
@mark.unit_create
def test_create_email_exists(artist_write_service, user_service_mock) -> None:
    """Teste Erstellung eines Artists mit bereits vorhandener Email."""
    artist = _artist(email="exists@email.test")
    user_service_mock.username_exists.return_value = False
    user_service_mock.email_exists.return_value = True

    with raises(EmailExistsError) as err:
        artist_write_service.create(artist=artist)

    assert err.type is EmailExistsError
