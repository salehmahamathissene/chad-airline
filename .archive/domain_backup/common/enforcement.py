from domain.common.authority import Authority
from domain.common.permissions import PERMISSIONS
from domain.common.errors import InvariantViolation


def assert_authorized(action: str, authority: Authority) -> None:
    allowed_roles = PERMISSIONS.get(action)

    if not allowed_roles:
        raise InvariantViolation(
            f"Action '{action}' is not registered in permission matrix"
        )

    if authority.role not in allowed_roles:
        raise InvariantViolation(
            f"Authority {authority.role} is not permitted to perform {action}"
        )
