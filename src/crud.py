from .models import UserToken
import requests
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import mongoengine
from .models import TokenResponse
from typing import List, Optional


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

async def get_tokens():
    return UserToken.objects().all()

async def get_user_token(user_id: str):
    return UserToken.objects(user_id=user_id).first()

async def get_users():
    users = UserToken.objects().distinct('user_id')
    response = []

    for user_id in users:
        # Suponiendo que quieres el último token para cada usuario
        token_data = UserToken.objects(user_id=user_id).order_by('-id').first()
        if token_data:
            # Convierte directamente a un diccionario y luego a TokenResponse
            response.append(TokenResponse(**token_data.to_mongo().to_dict()))

    return response

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

async def notify_message(receiver_id: str, title: str, message_content: str, sender_alias: str):
    try:
        # Obtener el token del dispositivo del usuario receptor
        user_token = UserToken.objects(user_id=receiver_id).first()
        if not user_token:
            raise Exception(f"No token found for user {receiver_id}")

        # Preparar el contenido de la notificación
        body = f"{sender_alias}: {message_content}"

        # Crear el mensaje de la notificación
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=user_token.token,
        )

        # Enviar la notificación
        response = messaging.send(message)
        return response
    except Exception as e:
        # Manejo de errores
        raise e

async def notify_mention(mentioned_user_ids: List[str], mentioning_user_id: Optional[str], message_content: str):
    try:
        # Obtener los tokens de los dispositivos de los usuarios mencionados
        user_tokens = [user_token.token for user_token in UserToken.objects(user_id__in=mentioned_user_ids)]

        # Preparar el contenido de la notificación
        title = "Has sido mencionado!"
        body = f"{mentioning_user_id if mentioning_user_id else 'Alguien'} te mencionó: {message_content}"
        
        
        # Crear un mensaje multicast
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=user_tokens,
        )

        # Enviar el mensaje multicast
        response = messaging.send_multicast(message)
        return response.success_count  # Retorna la cantidad de mensajes enviados exitosamente
    except Exception as e:
        # Manejo de errores
        raise e