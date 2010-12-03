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
    public = BooleanField(default=False)

    @property
    def members(self):
        return [i.user for i in GroupUser.objects(group=self).only('user')]

    def add_member(self, user, is_admin=None):
        obj = GroupUser(group=self,
                        user=user,
                        is_admin=is_admin)
        try:
            obj.save()
        except OperationError:
            pass

    def remove_member(self, user):
        GroupUser.objects(group=self, user=user).delete()

    def is_admin(self, user):
        return GroupUser.objects(group=self, user=user).only('is_admin').first()


class GroupTheme(Document):
    name = StringField(required=True, unique=True)

    meta = {
        'ordering': [
            'name',
        ]
    }


class GroupType(Document):
    name = StringField(required=True, unique=True)

    meta = {
        'ordering': [
            'name',
        ]
    }


class GroupUser(Document):
    group = ReferenceField('Group')
    user = ReferenceField('User', unique_with='group')
    is_admin = BooleanField(default=False)