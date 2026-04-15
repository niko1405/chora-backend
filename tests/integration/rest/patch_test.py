# ruff: noqa: S101, D103
# Copyright (C) 2026 - present Juergen Zimmermann, Hochschule Karlsruhe

"""Tests fuer PATCH bei Artists."""

from http import HTTPStatus
from typing import Final

from httpx import get, patch
from pytest import mark

from tests.integration.common_test import (
    ARTIST_ALICE_ID,
    ARTIST_BRUNO_ID,
    ctx,
    login,
    rest_url,
)


@mark.rest
@mark.patch_request
def test_patch_artist_email() -> None:
    """Teste Teilaktualisierung mit neuer E-Mail."""
    # arrange
    artist_id: Final = ARTIST_ALICE_ID
    
    # Get current version
    get_response: Final = get(f"{rest_url}/{artist_id}", verify=ctx)
    assert get_response.status_code == HTTPStatus.OK
    artist_data = get_response.json()
    current_version: Final = artist_data.get("version", 0)

    token: Final = login()
    headers = {"If-Match": f'"{current_version}"', "Authorization": f"Bearer {token}"}
    patch_payload = {"email": "alice.patch@acme.de"}

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
    """Teste Ablehnung ohne If-Match Header."""
    # arrange
    artist_id: Final = ARTIST_BRUNO_ID
    
    token: Final = login()
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = patch(
        f"{rest_url}/{artist_id}",
        json={"email": "bruno.patch@acme.de"},
        headers=headers,
        verify=ctx,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@mark.rest
@mark.patch_request
def test_patch_artist_not_found() -> None:
    """Teste PATCH auf nicht vorhandenen Artist."""
    token: Final = login()
    headers = {"If-Match": '"0"', "Authorization": f"Bearer {token}"}

    response: Final = patch(
        f"{rest_url}/999999",
        json={"email": "notfound.patch@acme.de"},
        headers=headers,
        verify=ctx,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
