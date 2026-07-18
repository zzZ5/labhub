from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Member
from .ordering import ordered_members
from .serializers import MemberSerializer


class MemberViewSet(ReadOnlyModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Member.objects.filter(sort_order__gt=0).prefetch_related("educations", "experiences")
        return ordered_members(queryset)
