from apps.cam.documents import Camera


class PlaceBoxMiddleware:
    def process_request(self, request):
        request.places = Camera.objects(is_view_public=True,
                                        is_view_enabled=True
                                        ).order_by('date_created')[:6]
        request.places = list(request.places)
        request.places_all_count = Camera.objects.count()
        