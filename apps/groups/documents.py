from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, ReferenceField

class Group(Document):
    name = StringField(required=True, unique=True)
    members = ListField(ReferenceField('User'))

    def add_member(self, user):
        from apps.social.documents import User
        Group.objects(id=self.id).update_one(add_to_set__members=user)
        User.objects(id=user.id).update_one(add_to_set__groups=self)

    def remove_member(self, user):
        from apps.social.documents import User
        Group.objects(id=self.id).update_one(pull__members=user)
        User.objects(id=user.id).update_one(pull__groups=self)

