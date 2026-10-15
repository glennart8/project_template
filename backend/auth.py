"""Den inloggade användaren, ur Entra Application Proxys headers.

⚠ Headerna är vanlig text. De bevisar något bara om appens port är stängd för
allt utom proxyn — annars kan vem som helst skriva dem själv.
"""

from fastapi import HTTPException, Request
from pydantic import BaseModel

from config import settings

# Måste stämma med Enterprise-appen i Entra (Single sign-on → Headers).
USERNAME_HEADER = "x-control-header"  # sAMAccountName, t.ex. HEPI02
DISPLAYNAME_HEADER = "x-control-displayname-header"
GROUP_HEADER = "x-control-group-header"  # gruppernas ObjectId, kommaseparerade


class CurrentUser(BaseModel):
    username: str
    name: str
    # Entra-gruppernas ObjectId. Appen översätter dem till egna roller.
    groups: set[str]


def get_current_user(request: Request) -> CurrentUser:
    """401 utan inloggning. Vad användaren får göra avgör appen utifrån groups."""
    if settings.AUTH_MODE == "mock":
        return CurrentUser(
            username=settings.MOCK_USER,
            name=settings.MOCK_USER,
            groups=set(settings.MOCK_GROUPS),
        )

    username = request.headers.get(USERNAME_HEADER, "").strip()
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Ingen inloggning. Appen ska nås via Entra Application Proxy.",
        )
    return CurrentUser(
        username=username,
        name=request.headers.get(DISPLAYNAME_HEADER, "").strip(),
        groups={
            group.strip()
            for value in request.headers.getlist(GROUP_HEADER)
            for group in value.split(",")
            if group.strip()
        },
    )
