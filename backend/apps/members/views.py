from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Member
from .serializers import MemberSerializer


class MemberViewSet(ReadOnlyModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Member.objects.filter(sort_order__gt=0).order_by("sort_order", "name").prefetch_related("educations", "experiences")
