from fastapi import FastAPI

import mongoengine
from . import crud
from .models import *
from typing import List

app = FastAPI()

config = {
    "db" : "messagesdb",
    "host" : "messages-db-mongodb",
    "port" : 27017,
    "username" : "root",
    "password" : "snapmsg",
    "authentication_source" : "admin",
    "connectTimeoutMS" : 2000,
    "serverSelectionTimeoutMS" : 2000

}
url = "mongodb://snapmsg:snapmsg@messages-db-mongodb:27017/messagesdb"
mongoengine.connect(**config)

@app.get("/")
async def root():
    return {"message": "messages microsevice"}

@app.post("/register-token")
async def register_token(token_data: TokenData):
    await crud.create_token(token_data.user_id, token_data.token)
    return {"message": "Token registered successfully"}

@app.post("/send-notification")
async def send_notification(notification: Notification):
    await crud.send_push_notification(notification.token, notification.title, notification.body)
    return {"message": "Notification sent successfully"}

@app.get("/get-user-tokens/{user_id}",response_model=TokenResponse)
async def get_user_tokens(user_id: str):
    return await crud.get_user_token(user_id)

@app.get("/get-users", response_model=List[TokenResponse])
async def get_users_endpoint():
    return await crud.get_users()

@app.post("/notify-follow/{follower_name}/{followed_id}")
async def notify_follow(follower_name: str, followed_id: str):
        await crud.notify_follow(follower_name, followed_id)
        return {"message": "Follow Notification sent successfully"}

@app.post("/notify-message")
async def notify_message(notification: MessageNotification):
    response = await crud.notify_message(notification.receiver_id, 
                                         "New Message",  # Título fijo
                                         notification.message_content, 
                                         notification.sender_alias)
    return {"message": "Message Notification sent successfully", "response": response}

@app.post("/notify-mention")
async def notify_mention(notification: MentionNotification):
    response = await crud.notify_mention(notification.mentioned_user_ids, 
                                         notification.mentioning_user_id,
                                         notification.message_content)
    return {"message": "Mention Notifications sent successfully", "response": response}
