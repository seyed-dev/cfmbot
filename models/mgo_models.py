from mongoengine import Document, StringField, IntField, BooleanField

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


