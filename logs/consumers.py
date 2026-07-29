from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LogsConsumer(AsyncWebsocketConsumer):
    async def connect(self):        
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'You are connected!'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        print(message)

        await self.send(text_data=json.dumps({
            'message': f"SecurityForce Logs: - {message}"
        }))
    