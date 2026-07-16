from apps.accounts.models import RoleCode
from apps.accounts.services import can_write_internal_data, user_has_role

from .models import Instrument, InstrumentTrainingRecord


def user_can_manage_instrument(user, instrument: Instrument | None = None) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not can_write_internal_data(user):
        return False
    if instrument and instrument.manager_id == user.id:
        return True
    return user_has_role(user, RoleCode.ADMIN, RoleCode.INSTRUMENT_MANAGER)


def user_has_training(user, instrument: Instrument) -> bool:
    if not instrument.need_training:
        return True
    if user_can_manage_instrument(user, instrument):
        return True
    return InstrumentTrainingRecord.objects.filter(instrument=instrument, user=user, is_passed=True).exists()
