from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.config import settings


class TokenService:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = "HS256"

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=1))

        to_encode.update({
            "exp": expire,
        })

        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)


    def decode_token(self, token: str):
        try:
            return jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM],
            )
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None


    def create_reset_token(self, data: dict):
        return self.create_access_token(data, timedelta(minutes=15))