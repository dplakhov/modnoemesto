from apps.cam.documents import Camera


class PlaceBoxMiddleware:
    def process_request(self, request):
        request.places = Camera.objects
        request.places = list(request.places)
        request.places_all_count = Camera.objects.count()
        