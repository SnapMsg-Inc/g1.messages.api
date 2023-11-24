from fastapi import FastAPI

import mongoengine
from . import crud
from .models import *

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

@app.post("/notify-follow/{follower_name}/{followed_id}")
async def notify_follow(follower_name: str, followed_id: str):
        await crud.notify_user_follow(follower_name, followed_id)
        return {"message": "Follow Notification sent successfully"}

@app.get("/get-tokens")
async def get_tokens():
    return await crud.get_tokens()

@app.get("/get-user-tokens/{user_id}")
async def get_user_tokens(user_id: str):
    return await crud.get_user_tokens(user_id)
