from django.db.models import Case, IntegerField, Value, When

from .models import UserProfile


IDENTITY_ORDER = [
    UserProfile.SchoolIdentity.PI,
    UserProfile.SchoolIdentity.POSTDOC,
    UserProfile.SchoolIdentity.PHD,
    UserProfile.SchoolIdentity.MASTER,
    UserProfile.SchoolIdentity.UNDERGRADUATE,
    UserProfile.SchoolIdentity.OTHER,
]


def annotate_member_order(queryset, profile_path="profile"):
    membership_field = f"{profile_path}__membership_status"
    identity_field = f"{profile_path}__school_identity"
    identity_cases = [
        When(**{identity_field: identity}, then=Value(rank))
        for rank, identity in enumerate(IDENTITY_ORDER)
    ]
    return queryset.annotate(
        _membership_rank=Case(
            When(**{membership_field: UserProfile.MembershipStatus.ACTIVE}, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        _identity_rank=Case(
            *identity_cases,
            default=Value(len(IDENTITY_ORDER)),
            output_field=IntegerField(),
        ),
    )
