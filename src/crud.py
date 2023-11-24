
# src/crud.py
from .models import UserToken
from firebase_admin import messaging

async def create_token(user_id: str, token: str):
    existing_token = UserToken.objects(user_id=user_id).first()

    if existing_token:
        existing_token.update(set__token=token)
    else:
        UserToken(user_id=user_id, token=token).save()

def send_push_notification(token: str, title: str, body: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )

    response = messaging.send(message)
    return response


async def notify_user_follow(follower_name: str, followed_id: str):
    followed_user_token = UserToken.objects(user_id=followed_id).first()

    if followed_user_token:
        send_push_notification(
            followed_user_token.token,
            "New Follow",
            f"{follower_name}."
        )
    else:
        raise ValueError("Token not found")