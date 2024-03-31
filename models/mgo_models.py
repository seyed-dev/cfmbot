from mongoengine import Document, StringField, IntField, BooleanField, ListField, ReferenceField

class User(Document):
    telegram_id = IntField(required=True, unique=True)
    full_name = StringField()
    username = StringField()
    wallet = IntField(min_value=0, default=0)
    invites = IntField(min_value=0, default=0)
    inviter = IntField()
    is_premium = BooleanField()

    meta = {
        'collection': 'users',
        'indexes': [
            'telegram_id',
            'username'
        ]
    }


class ClassRecord(Document):
    title = StringField(required=True)
    description = StringField()
    video_path = StringField()
    users = ListField(ReferenceField(User))
    is_active = BooleanField(default=True)
    is_downloadable = BooleanField(default=True)

    meta = {
        'collection': 'class.record',
        'indexes': [
            'title',
            'is_active',
            'is_downloadable'
        ]
    }