from fastapi import Header, HTTPException

ROLES = {"admin", "operator", "analyst", "viewer"}


def require_role(*allowed: str):
    allowed_set = set(allowed)

    def _guard(x_role: str = Header(default="viewer")) -> str:
        role = x_role.strip().lower()
        if role not in ROLES:
            raise HTTPException(status_code=400, detail="invalid role header")
        if role not in allowed_set:
            raise HTTPException(status_code=403, detail="insufficient role")
        return role

    return _guard
