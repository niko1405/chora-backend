# ruff: noqa: S101, D103  # noqa: RUF100
# Copyright (C) 2026 - present Juergen Zimmermann, Hochschule Karlsruhe

"""Tests fuer POST/PUT/DELETE bei Song-Endpunkten - verwendet Testdaten aus CSV."""

from http import HTTPStatus
from typing import Final

from httpx import delete, post, put
from pytest import mark

from tests.integration.common_test import (
    ARTIST_ALICE_ID,
    ARTIST_BRUNO_ID,
    ARTIST_CLEO_ID,
    ctx,
    login,
    SONG_REST_URL,
)


@mark.rest
@mark.post_request
def test_post_song() -> None:
    """Teste Song-Erstellung mit CSV-Artist."""
    # arrange
    artist_id: Final = ARTIST_ALICE_ID

    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}
    song_payload = {
        "titel": "Signal Flow",
        "genres": ["Rock", "Pop"],
        "erscheinungsdatum": "2024-06-01",
        "dauer": 210,
        "artist_ids": [artist_id],
    }

    # act
    response: Final = post(
        SONG_REST_URL,
        json=song_payload,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location = response.headers.get("Location")
    assert location is not None


@mark.rest
@mark.put_request
def test_put_song() -> None:
    """Teste Song-Update mit CSV-Artist."""
    # arrange
    artist_id: Final = ARTIST_BRUNO_ID

    token: Final = login()
    auth_headers = {"Authorization": f"Bearer {token}"}

    create_song_response: Final = post(
        SONG_REST_URL,
        json={
            "titel": "Old Song",
            "genres": ["Rock"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 190,
            "artist_ids": [artist_id],
        },
        headers=auth_headers,
        verify=ctx,
    )
    assert create_song_response.status_code == HTTPStatus.CREATED
    song_location = create_song_response.headers.get("Location")
    assert song_location is not None
    song_id: Final = int(song_location.rsplit("/", maxsplit=1)[-1])

    # act
    response: Final = put(
        f"{SONG_REST_URL}/{song_id}",
        json={
            "titel": "Updated Song",
            "genres": ["Jazz"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 222,
            "artist_ids": [artist_id],
        },
        headers=auth_headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT


@mark.rest
@mark.delete_request
def test_delete_song() -> None:
    """Teste Song-Löschung mit CSV-Artist."""
    # arrange
    artist_id: Final = ARTIST_CLEO_ID

    token: Final = login()
    auth_headers = {"Authorization": f"Bearer {token}"}

    create_song_response: Final = post(
        SONG_REST_URL,
        json={
            "titel": "Delete Song",
            "genres": ["Metal"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 199,
            "artist_ids": [artist_id],
        },
        headers=auth_headers,
        verify=ctx,
    )
    assert create_song_response.status_code == HTTPStatus.CREATED
    song_location = create_song_response.headers.get("Location")
    assert song_location is not None
    song_id: Final = int(song_location.rsplit("/", maxsplit=1)[-1])

    # act
    response: Final = delete(
        f"{SONG_REST_URL}/{song_id}",
        headers=auth_headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT


@mark.rest
@mark.post_request
def test_post_song_artist_not_found() -> None:
    """Teste Song-Erstellung mit nicht vorhandenem Artist."""
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = post(
        SONG_REST_URL,
        json={
            "titel": "Ghost Song",
            "genres": ["Rock"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 200,
            "artist_ids": [999999],
        },
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.post_request
def test_post_song_titel_exists() -> None:
    """Teste Song-Erstellung mit bereits vorhandenem Titel."""
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = post(
        SONG_REST_URL,
        json={
            "titel": "Glass Horizon",
            "genres": ["Rock"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 200,
            "artist_ids": [1010],
        },
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@mark.rest
@mark.put_request
def test_put_song_not_found() -> None:
    """Teste Song-Update mit nicht vorhandener Song-ID."""
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = put(
        f"{SONG_REST_URL}/999999",
        json={
            "titel": "Missing Song",
            "genres": ["Rock"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 222,
            "artist_ids": [1000],
        },
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.put_request
def test_put_song_titel_exists() -> None:
    """Teste Song-Update mit bereits vorhandenem Titel."""
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = put(
        f"{SONG_REST_URL}/3020",
        json={
            "titel": "Glass Horizon",
            "genres": ["Rock"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 200,
            "artist_ids": [1010],
        },
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@mark.rest
@mark.delete_request
def test_delete_song_not_found() -> None:
    """Teste Song-Löschung mit nicht vorhandener Song-ID."""
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = delete(
        f"{SONG_REST_URL}/999999",
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
