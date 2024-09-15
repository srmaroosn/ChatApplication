from django.test import TestCase

# Create your tests here.
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from django.contrib.auth.models import User
from asgiref.testing import ApplicationCommunicator
from .consumers import ChatConsumer
from .models import UserChannel, Message
from channels.layers import get_channel_layer
import json

class ChatConsumerTest(TestCase):
    
    def setUp(self):
        # Setting up test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

        # Set up channel layer (in-memory channel layer for testing)
        self.channel_layer = get_channel_layer()
        
    async def test_connect(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Check that a UserChannel was created
        user_channel = UserChannel.objects.filter(user=self.user1).first()
        self.assertIsNotNone(user_channel)
        self.assertEqual(user_channel.channel_name, communicator.channel_name)

        await communicator.disconnect()

    async def test_receive_new_message(self):
        # Connect user1 to WebSocket
        communicator1 = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
        await communicator1.connect()

        # Simulate user1 sending a message to user2
        message = {"type": "new_message", "message": "Hello user2!"}
        await communicator1.send_json_to(message)

        # Check if the message is saved in the database
        new_message = Message.objects.filter(from_who=self.user1, to_who=self.user2).first()
        self.assertIsNotNone(new_message)
        self.assertEqual(new_message.message, "Hello user2!")

        await communicator1.disconnect()

    

    async def test_disconnect(self):
        # Test disconnect
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
        await communicator.connect()
        await communicator.disconnect()
        # Add any additional checks if you have logic for disconnects

    async def test_error_handling(self):
        # Connect user1 to WebSocket
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
        await communicator.connect()

        # Send invalid data to test error handling
        invalid_message = {"invalid_key": "value"}
        await communicator.send_json_to(invalid_message)
        
        # Ensure the consumer does not crash and can handle invalid messages
        response = await communicator.receive_from()
        self.assertIsNotNone(response)

        await communicator.disconnect()

