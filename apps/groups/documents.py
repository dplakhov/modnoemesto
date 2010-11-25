from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, ReferenceField
from apps.social.documents import Account

class Group(Document):
    name = StringField(required=True, unique=True)
    members = ListField(ReferenceField('Account'))

    def add_member(self, user):
        Group.objects(id=self.id).update_one(add_to_set__members=user)
        Account.objects(id=user.id).update_one(add_to_set__groups=self)

    def remove_member(self, user):
        Group.objects(id=self.id).update_one(pull__members=user)
        Account.objects(id=user.id).update_one(pull__groups=self)

