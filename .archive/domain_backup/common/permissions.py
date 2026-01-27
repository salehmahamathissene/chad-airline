from typing import Set
from domain.common.authority import AuthorityRole
from domain.common.errors import InvariantViolation


PERMISSIONS = {
    "ISSUE_TICKET": {AuthorityRole.SYSTEM},
    "PAY_TICKET": {AuthorityRole.PASSENGER, AuthorityRole.FINANCE},
    "CHECK_IN": {AuthorityRole.CHECKIN_AGENT},
    "BOARD": {AuthorityRole.GATE_AGENT},
    "CLOSE_TICKET": {AuthorityRole.SYSTEM},
    "OVERRIDE_BOARDING": {AuthorityRole.CAPTAIN, AuthorityRole.SECURITY},
}
