from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions.token import (
    InsufficientAvailableSupply,
    TokenAlreadyExists,
    TokenNotFound,
    TokenProjectAlreadyExists,
    TokenProjectNotFound,
)
from app.models.token import Token
from app.models.token_project import TokenProject
from app.schemas.token import TokenProjectResponse, TokenResponse


class TokenContractService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_token(
        self,
        name: str,
        suffix: str,
        contract_address: str,
    ) -> TokenResponse:
        existing = await self.session.scalar(
            select(Token).where((Token.name == name) | (Token.suffix == suffix))
        )
        if existing:
            raise TokenAlreadyExists()

        token = Token(name=name, suffix=suffix, contract_address=contract_address)
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)

        return TokenResponse.model_validate(token)

    async def get_token(self, token_id: UUID) -> TokenResponse:
        token = await self.session.scalar(select(Token).where(Token.id == token_id))
        if not token:
            raise TokenNotFound()

        return TokenResponse.model_validate(token)

    async def get_all_tokens(self) -> list[TokenResponse]:
        tokens = await self.session.scalars(select(Token))
        return [TokenResponse.model_validate(t) for t in tokens]

    async def create_token_project(
        self,
        token_id: UUID,
        project_id: UUID,
        total_supply: Decimal,
    ) -> TokenProjectResponse:
        token = await self.session.scalar(select(Token).where(Token.id == token_id))
        if not token:
            raise TokenNotFound()

        existing = await self.session.scalar(
            select(TokenProject).where(TokenProject.project_id == project_id)
        )
        if existing:
            raise TokenProjectAlreadyExists()

        token_project = TokenProject(
            token_id=token_id,
            project_id=project_id,
            total_supply=total_supply,
            available_supply=total_supply,
        )
        self.session.add(token_project)
        await self.session.commit()
        await self.session.refresh(token_project)

        return await self._get_token_project_with_token(token_project.id)

    async def get_token_project_by_project(
        self, project_id: UUID
    ) -> TokenProjectResponse:
        token_project = await self.session.scalar(
            select(TokenProject)
            .options(selectinload(TokenProject.token))
            .where(TokenProject.project_id == project_id)
        )
        if not token_project:
            raise TokenProjectNotFound()

        return TokenProjectResponse.model_validate(token_project)

    async def reduce_available_supply(
        self, project_id: UUID, amount: Decimal
    ) -> TokenProjectResponse:
        token_project = await self.session.scalar(
            select(TokenProject)
            .options(selectinload(TokenProject.token))
            .where(TokenProject.project_id == project_id)
        )
        if not token_project:
            raise TokenProjectNotFound()

        if token_project.available_supply < amount:
            raise InsufficientAvailableSupply()

        token_project.available_supply -= amount
        await self.session.commit()
        await self.session.refresh(token_project)

        return TokenProjectResponse.model_validate(token_project)

    async def _get_token_project_with_token(
        self, token_project_id: UUID
    ) -> TokenProjectResponse:
        token_project = await self.session.scalar(
            select(TokenProject)
            .options(selectinload(TokenProject.token))
            .where(TokenProject.id == token_project_id)
        )
        return TokenProjectResponse.model_validate(token_project)
