from mongoengine.document import Document
from mongoengine.fields import StringField, ReferenceField, URLField, BooleanField
from mongoengine.queryset import OperationError


class Group(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    theme = ReferenceField('GroupTheme')
    type = ReferenceField('GroupType')
    site = URLField()
    country = StringField()
    city = StringField()
    public = BooleanField(default=True)

    @property
    def members(self):
        return [i.user for i in GroupUser.objects(group=self).only('user')]

    def add_member(self, user):
        obj = GroupUser(group=self, user=user)
        try:
            obj.save()
        except OperationError:
            pass

    def remove_member(self, user):
        GroupUser.objects(group=self, user=user).delete()


class GroupTheme(Document):
    name = StringField(required=True, unique=True)

class GroupType(Document):
    name = StringField(required=True, unique=True)


class GroupUser(Document):
    group = ReferenceField('Group')
    user = ReferenceField('User', unique_with='group')
    is_admin = BooleanField(default=False)