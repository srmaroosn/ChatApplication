from django.urls import path
from chat import consumers

ASGI_urlpatterns=[
    path("websocket/<int:id>", consumers.ChatConsumer.as_asgi()),   #we include the link of the connection i.e websocket
]
