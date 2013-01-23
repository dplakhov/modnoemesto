from django.core.management.base import BaseCommand, CommandError
from apps.social.documents import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        i = 0
        for user in User.objects:
            cam = user.get_camera()
            if cam and cam.type.is_default:
                user.cam = None
                user.save()
                cam.delete()
                i += 1
        print "Del count %i" % i