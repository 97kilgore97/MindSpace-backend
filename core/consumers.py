import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time peer chat rooms.

    Connect:  ws://host/ws/chat/<room_id>/
    Headers:  Authorization: Bearer <access_token>

    Client sends:  { "type": "message", "content": "Hello" }
    Server sends:  { "type": "message", "message": { ...ChatMessage fields } }
    """

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group = f'chat_{self.room_id}'
        self.user = self.scope.get('user')

        # Reject unauthenticated connections
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Check room exists and user is a member
        room = await self.get_room(self.room_id)
        if not room:
            await self.close(code=4004)
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        logger.info(f'WS connected: user={self.user.id} room={self.room_id}')

        # Notify room of new presence
        await self.channel_layer.group_send(self.room_group, {
            'type': 'presence',
            'user': self.user.display_name,
            'event': 'joined',
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group'):
            await self.channel_layer.group_send(self.room_group, {
                'type': 'presence',
                'user': getattr(self.user, 'display_name', 'Someone'),
                'event': 'left',
            })
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON.')
            return

        msg_type = data.get('type')

        if msg_type == 'message':
            content = (data.get('content') or '').strip()
            if not content:
                await self.send_error('Message content cannot be empty.')
                return
            if len(content) > 2000:
                await self.send_error('Message too long (max 2000 chars).')
                return

            # Persist to DB (runs safety check inside)
            message = await self.save_message(content)

            # Broadcast to room (excluding flagged messages)
            if not message.is_flagged:
                await self.channel_layer.group_send(self.room_group, {
                    'type': 'chat_message',
                    'message': {
                        'id': str(message.id),
                        'content': message.text,
                        'sender': {
                            'id': str(self.user.id),
                            'display_name': self.user.display_name,
                            'is_anonymous': self.user.is_anonymous,
                        },
                        'sent_at': message.sent_at.isoformat(),
                    },
                })
            else:
                # Notify only the sender their message was flagged
                await self.send(text_data=json.dumps({
                    'type': 'flagged',
                    'message': (
                        'Your message has been held for review by our safety team. '
                        'If you need immediate help, please call 0800 720 199.'
                    ),
                }))

        elif msg_type == 'typing':
            await self.channel_layer.group_send(self.room_group, {
                'type': 'typing_indicator',
                'user': self.user.display_name,
                'is_typing': bool(data.get('is_typing', False)),
            })

        else:
            await self.send_error(f'Unknown message type: {msg_type}')

    # ── Group event handlers ───────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
        }))

    async def presence(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'user': event['user'],
            'event': event['event'],  # 'joined' | 'left'
        }))

    async def typing_indicator(self, event):
        # Don't send typing indicator back to the typer themselves
        if event['user'] != self.user.display_name:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user': event['user'],
                'is_typing': event['is_typing'],
            }))

    # ── Helpers ───────────────────────────────────────────

    async def send_error(self, detail: str):
        await self.send(text_data=json.dumps({'type': 'error', 'detail': detail}))

    @database_sync_to_async
    def get_room(self, room_id):
        from groups.models import SupportGroup
        try:
            return SupportGroup.objects.get(id=room_id)
        except SupportGroup.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content: str):
        from groups.models import ChatMessage
        msg = ChatMessage.objects.create(
            group_id=self.room_id,
            sender=self.user,
            text=content,
            is_anonymous=self.user.is_anonymous if hasattr(self.user, 'is_anonymous') else False,
        )
        return msg
        