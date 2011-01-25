from apps.cam.documents import Camera, CameraTag
from apps.utils.paginator import paginate
from django.core.urlresolvers import reverse


class PlaceBoxMiddleware:
    def process_request(self, request):
        params = dict(
            is_view_public=True,
            is_view_enabled=True,
        )
        private_tags = [i.id for i in CameraTag.objects(is_private=True)]
        params.update(dict(tags__not__in=private_tags))
        request.places = paginate(request,
                                  Camera.objects(**params).order_by('-view_count'),
                                  Camera.objects(**params).count(),
                                  10,
                                  reverse('cam:place_update', args=['time', 'asc']))
        request.places_all_count = Camera.objects.count()
