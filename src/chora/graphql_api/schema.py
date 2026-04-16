"""Schema für GraphQL durch Strawberry."""

from collections.abc import Sequence
from typing import Final

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from chora.config import graphql_ide
from chora.graphql_api.graphql_types import (
    ArtistInput,
    CreatePayload,
    LoginResult,
    Suchparameter,
)
from chora.repository.artist_repository import ArtistRepository, Pageable
from chora.repository.song_repository import SongRepository
from chora.router.artist_model import ArtistModel
from chora.security import Role, TokenService, UserService
from chora.service import (
    ArtistDTO,
    ArtistService,
    ArtistWriteService,
    NotFoundError,
)

__all__ = ["graphql_router"]

_repo: Final = ArtistRepository()
_song_repo: Final = SongRepository()
_service: ArtistService = ArtistService(repo=_repo)
_user_service: UserService = UserService()
_write_service: ArtistWriteService = ArtistWriteService(
    repo=_repo, song_repo=_song_repo, user_service=_user_service
)
_token_service: Final = TokenService()


@strawberry.type
class Query:
    """GraphQL Query, um Artistdaten zu lesen."""

    @strawberry.field
    def artist(self, artist_id: strawberry.ID, info: Info) -> ArtistDTO | None:
        """Gibt einen Artist zurück.

        :param artist_id: ID des Artists
        :param info: GraphQL Info Objekt
        :return: Artist Objekt
        :rtype ArtistDTO | None
        :raises NotFoundError: Wenn kein Artist mit der angegebenen ID gefunden wird
        """
        logger.debug("artist_id={}", artist_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            artist_dto: Final = _service.find_by_id(artist_id=int(artist_id), user=user)
        except NotFoundError:
            return None
        logger.debug("artist_dto={}", artist_dto)
        return artist_dto

    @strawberry.field
    def artists(self, suchparameter: Suchparameter, info: Info) -> Sequence[ArtistDTO]:
        """Artist durch Suchparameter finden.

        :param suchparameter: Suchparameter für die Suche
        :param info: GraphQL Info Objekt
        :return: Liste von Artist Objekten
        :rtype list[ArtistDTO]
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        suchparameter_dict: Final[dict[str, str]] = dict(vars(suchparameter))
        suchparameter_filtered = {
            key: value
            for key, value in suchparameter_dict.items()
            if value is not None and value
        }
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            artists_dto: Final = _service.find(
                suchparameter=suchparameter_filtered, pageable=pageable
            )
        except NotFoundError:
            return []
        logger.debug("{}", artists_dto)
        return artists_dto.content


@strawberry.type
class Mutation:
    """GraphQL Mutation, um Artistdaten zu schreiben."""

    @strawberry.mutation
    def create(self, artist_input: ArtistInput) -> CreatePayload:
        """Einen Artist erstellen.

        :param artist_input: Input Daten für die Erstellung eines Artists
        :return: Payload mit der ID des erstellten Artists
        :rtype CreatePayload
        raises UsernameExistsError: Wenn der Username bereits existiert
        """
        logger.debug("artist_input={}", artist_input)

        artist_dict = artist_input.__dict__
        artist_dict["vertrag"] = artist_input.vertrag.__dict__
        artist_dict["songs"] = artist_input.songs

        artist_model: Final = ArtistModel.model_validate(artist_dict)

        artist_dto: Final = _write_service.create(
            artist=artist_model.to_artist(),
            song_ids=artist_model.songs,
        )
        payload: Final = CreatePayload(id=artist_dto.id)
        logger.debug("payload={}", payload)
        return payload

    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginResult:
        """Einen Token zu Benutzername und Passwort ermitteln.

        :param username: Benutzername
        :param password: Passwort
        :rtype: LoginResult
        """
        logger.debug("username={}, password={}", username, password)
        token_mapping = _token_service.token(username=username, password=password)

        token = token_mapping["access_token"]
        user = _token_service.get_user_from_token(token)
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        roles: Final = [role.value for role in user.roles]
        return LoginResult(token=token, expiresIn="1d", roles=roles)


schema: Final = strawberry.Schema(query=Query, mutation=Mutation)


Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema, context_getter=get_context, graphql_ide=graphql_ide
)
