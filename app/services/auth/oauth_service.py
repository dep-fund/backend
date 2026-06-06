import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.enums import AuthProvider, UserType
from app.models.user import StandardUser, User
from app.services.jwt_token_service import TokenService
from app.services.role_service import RoleService
from app.services.users.user_service import UserService
from app.schemas.auth import TokenResponse
from app.exceptions.auth.auth import UserBlocked, AccountNotActivated
from sqlalchemy import select


class OAuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_google_redirect_url(self) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
        }
        query = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{settings.GOOGLE_AUTH_URL}?{query}"

    async def handle_google_callback(self, code: str) -> TokenResponse:
        google_user = await self._fetch_google_user(code)
        user = await self._get_or_create_user(google_user)

        if user.blocked:
            raise UserBlocked()
        if not user.activated:
            raise AccountNotActivated()

        token = TokenService().create_access_token({
            "sub": user.username,
            "user_id": str(user.id),
            "type": user.type.value,
            "token_kind": "user",
        })
        return TokenResponse(access_token=token)

    async def _fetch_google_user(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(settings.GOOGLE_TOKEN_URL, data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            })
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]

            userinfo_response = await client.get(
                settings.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            userinfo_response.raise_for_status()
            return userinfo_response.json()

    async def _get_or_create_user(self, google_user: dict) -> User:
        user_service = UserService(self.session)
        google_id = google_user["sub"]
        email = google_user["email"]

        user = await self.session.scalar(
            select(User).where(User.google_id == google_id)
        )
        if user:
            return user

        user = await user_service.get_by_email(email)
        if user:
            user.google_id = google_id
            user.auth_provider = AuthProvider.GOOGLE
            await self.session.commit()
            await self.session.refresh(user)
            return user

        role = await RoleService(self.session).get_by_type(UserType.STANDARD)
        base_username = email.split("@")[0]
        username = await self._unique_username(base_username, user_service)

        user = User(
            username=username,
            name=google_user.get("given_name", ""),
            last_name=google_user.get("family_name", ""),
            email=email,
            password=None,
            image=google_user.get("picture"),
            google_id=google_id,
            auth_provider=AuthProvider.GOOGLE,
            type=UserType.STANDARD,
            role_id=role.id,
        )
        self.session.add(user)
        await self.session.flush()
        self.session.add(StandardUser(id=user.id))
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def _unique_username(self, base: str, user_service: UserService) -> str:
        username = base
        counter = 1
        while await user_service.get_by_username(username):
            username = f"{base}{counter}"
            counter += 1
        return username