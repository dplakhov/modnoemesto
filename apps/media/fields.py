from django.core.exceptions import ValidationError
from django.forms.fields import FileField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from apps.media.documents import File
from apps.media.transformations.image import ImageResize
from apps.media.tasks import apply_file_transformations
from apps.utils.stringio import StringIO
from ImageFile import Parser as ImageFileParser


class ImageField(FileField):
    default_error_messages = {
        'invalid_image': _(u"Upload a valid image. The file you uploaded was either not an image or a corrupted image."),
    }

    def __init__(self, *args, **kwargs):
        self.sizes = kwargs.pop('sizes', None)
        self.task_name = kwargs.pop('task_name', None)
        super(ImageField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF, JPG,
        PNG, possibly others -- whatever the Python Imaging Library supports).
        """
        f = super(ImageField, self).to_python(data)
        if f is None:
            return None

        buffer = StringIO()
        for chunk in data.chunks():
            buffer.write(chunk)

        buffer.reset()
        try:
            parser = ImageFileParser()
            parser.feed(buffer.read())
            parser.close()
        except Exception:
            raise ValidationError(self.error_messages['invalid_image'])
        self.buffer = buffer
        self.content_type = f.content_type
        return data

    def save(self, type='image', sizes=None, task_name=None):
        self.sizes = sizes or self.sizes
        self.task_name = task_name or self.task_name

        screen = File(type=type)
        self.buffer.reset()
        screen.file.put(self.buffer, content_type=self.content_type)
        screen.save()

        transformations = [ ImageResize(name=name, format='png', **params) for name, params in self.sizes.items() ]

        if settings.TASKS_ENABLED.get(self.task_name):
            args = [ screen.id, ] + transformations
            apply_file_transformations.apply_async(args=args)
        else:
            screen.apply_transformations(*transformations)
        return screen


class VideoField(FileField):
    default_error_messages = {
        'invalid_video':
            _(u"Upload a valid video. The file you uploaded was either not an video or a corrupted video."),
    }

    def __init__(self, *args, **kwargs):
        self.sizes = kwargs.pop('sizes', None)
        self.task_name = kwargs.pop('task_name', None)
        super(VideoField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid video file
        """
        f = super(VideoField, self).to_python(data)
        if f is None:
            return None

        buffer = StringIO()
        for chunk in data.chunks():
            buffer.write(chunk)

        buffer.reset()
        try:
            parser = ImageFileParser()
            parser.feed(buffer.read())
            parser.close()
        except Exception:
            raise ValidationError(self.error_messages['invalid_video'])
        self.buffer = buffer
        self.content_type = f.content_type
        return data

    def save(self, type='image', sizes=None, task_name=None):
        self.sizes = sizes or self.sizes
        self.task_name = task_name or self.task_name

        screen = File(type=type)
        self.buffer.reset()
        screen.file.put(self.buffer, content_type=self.content_type)
        screen.save()

        transformations = [ ImageResize(name=name, format='png', **params) for name, params in self.sizes.items() ]

        if settings.TASKS_ENABLED.get(self.task_name):
            args = [ screen.id, ] + transformations
            apply_file_transformations.apply_async(args=args)
        else:
            screen.apply_transformations(*transformations)
        return screen
