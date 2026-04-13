# ruff: noqa: S101, D103
# Copyright (C) 2026 - present Juergen Zimmermann, Hochschule Karlsruhe

"""Tests fuer POST/PUT/DELETE bei Song-Endpunkten."""

from http import HTTPStatus
from typing import Final

from httpx import delete, post, put
from pytest import mark

from tests.integration.common_test import create_artist_payload, ctx, login, rest_url


@mark.rest
@mark.post_request
def test_post_song() -> None:
    # arrange
    artist = create_artist_payload(marker="songpost")
    create_artist_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_artist_response.status_code == HTTPStatus.CREATED
    artist_location = create_artist_response.headers.get("Location")
    assert artist_location is not None
    artist_id: Final = int(artist_location.rsplit("/", maxsplit=1)[-1])

    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}
    song_payload = {
        "titel": "Signal Flow",
        "genres": ["ROCK", "POP"],
        "erscheinungsdatum": "2024-06-01",
        "dauer": 210,
    }

    # act
    response: Final = post(
        f"{rest_url}/{artist_id}/songs",
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
    # arrange
    artist = create_artist_payload(marker="songput")
    create_artist_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_artist_response.status_code == HTTPStatus.CREATED
    artist_location = create_artist_response.headers.get("Location")
    assert artist_location is not None
    artist_id: Final = int(artist_location.rsplit("/", maxsplit=1)[-1])

    token: Final = login()
    auth_headers = {"Authorization": f"Bearer {token}"}

    create_song_response: Final = post(
        f"{rest_url}/{artist_id}/songs",
        json={
            "titel": "Old Song",
            "genres": ["ROCK"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 190,
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
        f"{rest_url}/{artist_id}/songs/{song_id}",
        json={
            "titel": "Updated Song",
            "genres": ["JAZZ"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 222,
        },
        headers=auth_headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT


@mark.rest
@mark.delete_request
def test_delete_song() -> None:
    # arrange
    artist = create_artist_payload(marker="songdelete")
    create_artist_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_artist_response.status_code == HTTPStatus.CREATED
    artist_location = create_artist_response.headers.get("Location")
    assert artist_location is not None
    artist_id: Final = int(artist_location.rsplit("/", maxsplit=1)[-1])

    token: Final = login()
    auth_headers = {"Authorization": f"Bearer {token}"}

    create_song_response: Final = post(
        f"{rest_url}/{artist_id}/songs",
        json={
            "titel": "Delete Song",
            "genres": ["METAL"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 199,
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
        f"{rest_url}/{artist_id}/songs/{song_id}",
        headers=auth_headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT


@mark.rest
@mark.post_request
def test_post_song_artist_not_found() -> None:
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = post(
        f"{rest_url}/999999/songs",
        json={
            "titel": "Ghost Song",
            "genres": ["ROCK"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 200,
        },
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.put_request
def test_put_song_not_found() -> None:
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = put(
        f"{rest_url}/1000/songs/999999",
        json={
            "titel": "Missing Song",
            "genres": ["ROCK"],
            "erscheinungsdatum": "2024-01-01",
            "dauer": 222,
        },
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@mark.rest
@mark.delete_request
def test_delete_song_not_found() -> None:
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    response: Final = delete(
        f"{rest_url}/1000/songs/999999",
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
