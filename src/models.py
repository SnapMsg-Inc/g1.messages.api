from pydantic import BaseModel
from mongoengine import Document, StringField

class TokenData(BaseModel):
    user_id: str
    token: str

class UserToken(Document):
    user_id = StringField(required=True)
    token = StringField(required=True)

class Notification(BaseModel):
    token: str
    title: str
    body: str

class TokenResponse(BaseModel):
    user_id: str
    token: str


