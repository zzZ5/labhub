from apps.accounts.models import RoleCode
from apps.accounts.services import can_write_internal_data, user_has_role

from .models import Instrument


def user_can_manage_instrument(user, instrument: Instrument | None = None) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not can_write_internal_data(user):
        return False
    return user_has_role(user, RoleCode.ADMIN, RoleCode.INSTRUMENT_MANAGER)
