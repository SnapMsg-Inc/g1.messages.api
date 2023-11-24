
# src/crud.py

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from .models import UserToken
import requests

def get_access_token():
    SERVICE_ACCOUNT_FILE = '../snap-msg-firebase-adminsdk-k7p33-b70464c53b.json'
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    credentials.refresh(Request())

    return credentials.token

async def create_token(user_id: str, token: str):
    existing_token = UserToken.objects(user_id=user_id).first()

    if existing_token:
        existing_token.update(set__token=token)
    else:
        UserToken(user_id=user_id, token=token).save()

async def send_push_notification(token: str, title: str, body: str):
    access_token = get_access_token()

    url = 'https://fcm.googleapis.com/v1/projects/snap-msg/messages:send'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json; UTF-8',
    }

    message = {
        'message': {
            'token': token,
            'notification': {
                'title': title,
                'body': body
            }
        }
    }

    response = requests.post(url, headers=headers, json=message)
    return response.status_code, response.text


async def notify_follow(follower_name: str, followed_id: str):
    try:
        followed_user_token = UserToken.objects(user_id=followed_id).first()
        if followed_user_token:
            status_code, response_text = await send_push_notification(
                followed_user_token.token,
                "New Follow",
                f"{follower_name} started following you."
            )
            return {"message": "Follow Notification sent successfully", "status_code": status_code, "response": response_text}
        else:
            raise ValueError("Token not found")
    except Exception as e:
        return {"error": str(e)}
    
async def get_tokens():
    return UserToken.objects.all()

async def get_token(user_id: str):
    return UserToken.objects(user_id=user_id).first()
    