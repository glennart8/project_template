"""Vem användaren är och vad hen får göra, ur Entra Application Proxys headers.

⚠ Headerna är vanlig text. De bevisar något bara om appens port är stängd för
allt utom proxyn — annars kan vem som helst skriva dem själv.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

from config import settings

# Måste stämma med Enterprise-appen i Entra (Single sign-on → Headers).
USERNAME_HEADER = "x-control-header"  # sAMAccountName, t.ex. HEPI02
DISPLAYNAME_HEADER = "x-control-displayname-header"
GROUP_HEADER = "x-control-group-header"  # gruppernas ObjectId, kommaseparerade


class CurrentUser(BaseModel):
    username: str
    name: str
    roles: set[str]


def _roles(groups: set[str]) -> set[str]:
    """Entra-grupper → appens roller. Grupp-id:na står i config.py."""
    group_by_role = {"admin": settings.ADMIN_GROUP}
    return {role for role, group in group_by_role.items() if group and group in groups}


def get_current_user(request: Request) -> CurrentUser:
    """401 utan inloggning."""
    if settings.AUTH_MODE == "mock":
        return CurrentUser(
            username=settings.MOCK_USER,
            name=settings.MOCK_USER,
            roles=_roles(set(settings.MOCK_GROUPS)),
        )

    username = request.headers.get(USERNAME_HEADER, "").strip()
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Ingen inloggning. Appen ska nås via Entra Application Proxy.",
        )
    groups = {
        group.strip()
        for value in request.headers.getlist(GROUP_HEADER)
        for group in value.split(",")
        if group.strip()
    }
    return CurrentUser(
        username=username,
        name=request.headers.get(DISPLAYNAME_HEADER, "").strip(),
        roles=_roles(groups),
    )


# Användaren hämtas alltid ur inloggningen, aldrig ur en parameter i anropet.
# Vad användaren får göra prövar servicen, utifrån user.roles.
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
