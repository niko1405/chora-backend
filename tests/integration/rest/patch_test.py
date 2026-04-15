# ruff: noqa: S101, D103
# Copyright (C) 2026 - present Juergen Zimmermann, Hochschule Karlsruhe

"""Tests fuer PATCH bei Artists."""

from http import HTTPStatus
from typing import Final

from httpx import patch, post
from pytest import mark

from tests.integration.common_test import create_artist_payload, ctx, login, rest_url


@mark.rest
@mark.patch_request
def test_patch_artist_email() -> None:
    # arrange
    artist = create_artist_payload(marker="patchok")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    # Get current version
    from httpx import get
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    token: Final = login()
    headers = {"If-Match": f'"{current_version}"', "Authorization": f"Bearer {token}"}
    patch_payload = {"email": "artist.patch@acme.de"}

    # act
    response: Final = patch(
        f"{rest_url}/{artist_id}",
        json=patch_payload,
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT


@mark.rest
@mark.patch_request
def test_patch_artist_without_if_match() -> None:
    # arrange
    artist = create_artist_payload(marker="patchnomatch")
    create_response: Final = post(rest_url, json=artist, verify=ctx)
    assert create_response.status_code == HTTPStatus.CREATED
    location = create_response.headers.get("Location")
    assert location is not None
    artist_id: Final = int(location.rsplit("/", maxsplit=1)[-1])

    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = patch(
        f"{rest_url}/{artist_id}",
        json={"email": "artist.patch2@acme.de"},
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@mark.rest
@mark.patch_request
def test_patch_artist_not_found() -> None:
    token: Final = login()
    headers = {"If-Match": '"0"', "Authorization": f"Bearer {token}"}

    response: Final = patch(
        f"{rest_url}/999999",
        json={"email": "artist.patch3@acme.de"},
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
