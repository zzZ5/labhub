from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import ContactInfo, HomeBanner, ResearchDirection, SiteSetting
from .serializers import ContactInfoSerializer, HomeBannerSerializer, ResearchDirectionSerializer, SiteSettingSerializer


class ResearchDirectionViewSet(ReadOnlyModelViewSet):
    serializer_class = ResearchDirectionSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return ResearchDirection.objects.filter(is_active=True)


class HomeBannerViewSet(ReadOnlyModelViewSet):
    serializer_class = HomeBannerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return HomeBanner.objects.filter(is_active=True)


@api_view(["GET"])
@permission_classes([AllowAny])
def site_setting(request):
    setting = SiteSetting.objects.order_by("-updated_at").first()
    return Response(SiteSettingSerializer(setting).data if setting else {})


@api_view(["GET"])
@permission_classes([AllowAny])
def contact_info(request):
    contact = ContactInfo.objects.order_by("-updated_at").first()
    return Response(ContactInfoSerializer(contact).data if contact else {})
