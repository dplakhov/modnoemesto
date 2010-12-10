from apps.cam.documents import Camera


class PlaceBoxMiddleware:
    def process_request(self, request):
        request.places = Camera.objects(is_view_public=True,
                                        is_view_enabled=True
                                        ).order_by('-date_created')
        request.places_all_count = Camera.objects.count()
        