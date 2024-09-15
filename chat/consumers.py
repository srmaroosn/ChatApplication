from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync   #doing this to create the group of channels ans layers are asynchronous
import json
from .import models
from django.contrib.auth.models import User
import datetime

class ChatConsumer(WebsocketConsumer):
    #firstly accepting the connection
    def connect(self):
        self.accept()


        try:
            user_channel= models.UserChannel.objects.get(user=self.scope.get("user"))
            user_channel.channel_name= self.channel_name
            user_channel.save() 

        except:
            user_channel= models.UserChannel()
            user_channel.user= self.scope.get("user")
            user_channel.channel_name= self.channel_name
            user_channel.save()


        self.person_id= self.scope.get("url_route").get("kwargs").get("id") #getting the id from url routes from chat person and geeting it as kwargs
        
        # self.send('{"type":"accept", "status":"accepted"}')
        # async_to_sync(self.channel_layer.group_add)("test", self.channel_name)
        # print(self.scope.get("user"))
        # print(self.scope.get("url_route").get("kwargs"))
        
        # print(self.channel_name)
        # print(self.channel_layer.channels)
        # async_to_sync(self.channel_layer.group_add)("my_group", self.channel_name) #creating the group of channels with value group name and channels name
        
        # print(self.channel_layer.groups)


        #sending the message into the individaul channel

        # data={
        #     "type":"receiver_function",  #name of the receiver function
        #     "message":"Hi my name is roshan."
        # }
        # async_to_sync(self.channel_layer.send)(self.channel_name, data) #send  takes channel name i.e where to send and the data to be send

    # sending the message to the user
    #def send(self, text_data=None):
    #     self.send('{"type":"accept", "status":"accepted"}')
        

    #taking event from the client
    def receive(self, text_data):
        text_data= json.loads(text_data, strict= False) #we get dictionary data
        other_user = User.objects.get(id= self.person_id)
        if text_data.get("type") == "new_message":
            
            now =datetime.datetime.now()
            date= now.date()
            time=now.time()

            new_message= models.Message()
            new_message.from_who= self.scope.get("user")
            new_message.to_who= other_user
            new_message.message= text_data.get("message")
            new_message.date= date
            new_message.time= time
            new_message.has_been_seen= False
            new_message.save()
        

            
            try:
                user_channel_name = models.UserChannel.objects.get(user= other_user )
                data = {"type":"receiver_function",
                "type_of_data":"new_message",
                "data":text_data.get("message")}
                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)
        
            except:
                pass
        elif text_data.get("type") == "i_have_seen_the_messages":
            try:
                user_channel_name = models.UserChannel.objects.get(user= other_user )
                data = {"type":"receiver_function",
                "type_of_data":"the_message_has_been_seen_from_other",} 
            


                async_to_sync(self.channel_layer.send)(user_channel_name.channel_name, data)
        
            except:
                pass
        # self.send('{"type":"sucessfully received", "status":"received"}')

    

    # #we also can use disconnet function
    # def disconnect(self, code):
    #     print(code)
    #     print("The connection is disconnected")
        

    #there are lots of message in the layers this function picks up message which are meant for them
    def receiver_function(self, the_data_from_the_layer):
        
        data= json.dumps(the_data_from_the_layer)#as data is dictionary we convert it in json to send to client
        self.send(data)