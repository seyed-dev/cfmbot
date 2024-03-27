from mongoengine import Document, StringField, IntField

class User(Document):
    name = StringField()
    username = StringField()
    wallet = IntField(min_value=0, default=0)


