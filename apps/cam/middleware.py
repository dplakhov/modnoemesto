from apps.cam.documents import Camera
from apps.utils.paginator import paginate
from django.core.urlresolvers import reverse


class PlaceBoxMiddleware:
    def process_request(self, request):
        request.places = paginate(request,
                                  Camera.objects(is_view_public=True, is_view_enabled=True).order_by('-view_count'),
                                  Camera.objects(is_view_public=True, is_view_enabled=True).count(),
                                  10,
                                  reverse('cam:place_update', args=['time', 'asc']))
        request.places_all_count = Camera.objects.count()
        