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

    def add_member(self, user, is_admin=False, is_invite=False):
        return GroupUser.objects.get_or_create(group=self,
                                               user=user,
                                               is_admin=is_admin,
                                               is_invite=is_invite)[0]

    def remove_member(self, user):
        GroupUser.objects(group=self, user=user).delete()

    def is_admin(self, user):
        info = GroupUser.objects(group=self, user=user).only('is_admin').first()
        return info and info.is_admin


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
    is_invite = BooleanField(default=False)