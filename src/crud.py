from .models import UserToken
import requests
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import mongoengine

cred = credentials.Certificate("snap-msg-firebase-adminsdk-k7p33-b70464c53b.json")
firebase_admin.initialize_app(cred)

async def create_token(user_id: str, token: str):
    try:
        existing_token = UserToken.objects(user_id=user_id).first()

        if existing_token:
            existing_token.update(set__token=token)
        else:
            UserToken(user_id=user_id, token=token).save()

    except mongoengine.errors.MongoEngineException as e:
        print(f"Error al guardar el token: {e}")
        raise

def send_push_notification(token: str, title: str, body: str):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        response = messaging.send(message)
        return response  
    except Exception as e:
        print(f"Error sending notification: {e}")
        raise

async def notify_follow(follower_name: str, followed_id: str):
    try:
        followed_user_token = UserToken.objects(user_id=followed_id).first()
        if followed_user_token:
            status_code, response_text = send_push_notification(
                followed_user_token.token,
                "New Follow",
                f"{follower_name} started following you."
            )
            return {"message": "Follow Notification sent successfully", "status_code": status_code, "response": response_text}
        else:
            raise ValueError("Token not found")
    except Exception as e:
        print(f"Error in notify_follow: {e}")
        return {"error": str(e)}
    
async def get_tokens():
    return UserToken.objects().all()

async def get_user_token(user_id: str):
    return UserToken.objects(user_id=user_id).first()
    