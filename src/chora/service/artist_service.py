"""Geschäftslogik für die Künstlerverwaltung."""
from chora.repository.artist_repository import ArtistRepository

from typing import Final, Mapping

from loguru import logger

from chora.repository.pageable import Pageable
from chora.repository.session_factory import Session
from chora.repository.slice import Slice
from chora.service.artist_dto import ArtistDTO

__all__: list[str] = ["ArtistService"]


class ArtistService:
    """Service-Klasse für die Geschäftslogik der Künstlerverwaltung."""

    def __init__(self, repo: ArtistRepository) -> None:
        """Initialisierung des ArtistService mit einem Repository.

        :param repo: Repository für die Künstlerverwaltung
        """
        self.repo: ArtistRepository = repo

    def find_by_id(self, artist_id: int, user: User) -> ArtistDTO:
        """Suche mit der Künstler-ID.

        :param artist_id: ID für die Suche
        :param user: User aus dem Token
        :return: Der gefundene Künstler
        :rtype: ArtistDTO
        :raises NotFoundError: Falls kein Künstler gefunden
        :raises ForbiddenError: Falls die Künstlerdaten nicht gelesen werden dürfen
        """
        logger.debug("artist_id={}, user={}", artist_id, user)

        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            if (
                artist := self.repo.find_by_id(artist_id=artist_id, session=session)
            ) is None:
                if user_is_admin:
                    message: Final = f"Kein Künstler mit der ID {artist_id}"
                    logger.debug("NotFoundError: {}", message)
                    # "Throw Exceptions Instead of Returning Errors"
                    raise NotFoundError(artist_id=artist_id)
                logger.debug("Keine Berechtigung für die Suche nach Künstler mit ID {}", artist_id)
                raise ForbiddenError
                # TODO Exception Klassen implementieren

            if artist.username != user.username and not user_is_admin:
                logger.debug(
                    "artist.username={}, user.username={}, user.roles={}",
                    artist.username,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            artist_dto: Final = ArtistDTO(artist=artist)
            session.commit()

        logger.debug("{}", artist_dto)
        return artist_dto

    def find(
            self,
            queryparams: Mapping[str, str],
            pageable: Pageable
    ) -> Slice[ArtistDTO]:
        """Suche mit optionalen Query-Parametern und Pagination.

        :param queryparams: Mapping mit den Query-Parametern für die Suche
        :param pageable: Pageable-Objekt mit den Pagination-Parametern
        :return: Slice mit den gefundenen Künstlern als DTOs
        :rtype: Slice[ArtistDTO]
        """
        logger.debug("queryparams={}, pageable={}", queryparams, pageable)

        with Session() as session:
            artists_slice: Final = self.repo.find(
                queryparams=queryparams,
                pageable=pageable,
                session=session,
            )

            if len(artists_slice.content) == 0:
                raise NotFoundError(queryparams=queryparams)

            artist_dtos: Final = tuple(
                ArtistDTO(artist=artist) for artist in artists_slice.content
            )

            session.commit()

        # TODO Ggf. Excelsheet erstellen mit den Suchergebnissen
        logger.debug("{}", artist_dtos)
        return Slice(content=artist_dtos, total_elements=artists_slice.total_elements)

# TODO Weitere Methoden für die Geschäftslogik implementieren, zB find.
