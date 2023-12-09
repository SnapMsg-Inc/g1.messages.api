from pydantic import BaseModel
from mongoengine import Document, StringField
from typing import List, Optional


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

class MessageNotification(BaseModel):
    receiver_id: str
    title: str 
    message_content: str 

class MessageNotification(BaseModel):
    sender_alias: str  # Alias del usuario que envía el mensaje
    receiver_id: str   # ID del usuario que recibe el mensaje
    message_content: str  # Contenido del mensaje

class MentionNotification(BaseModel):
    mentioned_user_ids: List[str]  # Lista de IDs de usuarios mencionados
    mentioning_user_id: Optional[str] = None
    message_content: str
    