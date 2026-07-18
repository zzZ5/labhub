import pytest
from django.contrib.auth import get_user_model

from .models import UserProfile
from .ordering import annotate_member_order


User = get_user_model()


@pytest.mark.django_db
def test_member_order_prioritizes_active_status_then_school_identity():
    fixtures = [
        ("former-pi", UserProfile.SchoolIdentity.PI, UserProfile.MembershipStatus.FORMER),
        ("active-master", UserProfile.SchoolIdentity.MASTER, UserProfile.MembershipStatus.ACTIVE),
        ("active-postdoc", UserProfile.SchoolIdentity.POSTDOC, UserProfile.MembershipStatus.ACTIVE),
        ("active-pi", UserProfile.SchoolIdentity.PI, UserProfile.MembershipStatus.ACTIVE),
        ("active-phd", UserProfile.SchoolIdentity.PHD, UserProfile.MembershipStatus.ACTIVE),
    ]
    for username, identity, membership in fixtures:
        user = User.objects.create_user(username=username)
        user.profile.school_identity = identity
        user.profile.membership_status = membership
        user.profile.save(update_fields=["school_identity", "membership_status"])

    usernames = list(
        annotate_member_order(User.objects.select_related("profile"))
        .order_by("_membership_rank", "_identity_rank", "username")
        .values_list("username", flat=True)
    )

    assert usernames == ["active-pi", "active-postdoc", "active-phd", "active-master", "former-pi"]
