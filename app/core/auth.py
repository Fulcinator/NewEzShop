import os
from fastapi import HTTPException, Security, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user_type import UserType

security = HTTPBearer()


API_TOKEN = os.getenv("API_TOKEN", "secret-token")




def require_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Dependency: require a valid bearer token. Raises 401 if token invalid."""
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Invalid auth scheme")
    token = credentials.credentials
    if token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token


def require_roles(*allowed_roles: UserType):
    """
    Dependency which enforces the table-of-rights from documentation.
    """
    async def _checker(
        request: Request,
        _token: str = Depends(require_token),
    ):
        user = getattr(request.state, "user", None)
        if user is None:
            # Raise error when middleware did not attach a user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated",
            )

        if user.type not in allowed_roles:
            # Raise error when user does not have sufficient rights
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has not the rights to perform this operation",
            )

        return user

    return _checker