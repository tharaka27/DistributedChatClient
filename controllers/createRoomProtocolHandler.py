from models import serverstate 
from models.userSession import UserSession
from models.localroominfo import LocalRoomInfo
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import FastBully 
from algorithms.bully import Bully
import json
import time

class createRoomProtocolHandler:
    def __init__(self, identity, json_data):
        self._protocol = "createroom"
        self._identity = identity
        self._roomid = json_data["roomid"]
        self._bully_instance = FastBully._instance
        #self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        self._local_server_name = serverstate.LOCAL_SERVER_CONFIGURATION.getServerName()
        
    def handle(self):
        print("[INFO] Handling create room request started.")

        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return False, self._roomid, self._message_builder.coordinatorNotAlive(self._protocol)

        # imposing strict rules for creating room
        isOtherChatRoomOwned = False
        for room in serverstate.ALL_CHAT_ROOMS:
            if room.getOwner() == self._identity:
                isOtherChatRoomOwned = True
        
        if isOtherChatRoomOwned:
            return False,self._roomid, self._message_builder.newChatRoom(self._roomid,"False")

        # check whether I am coordinator
        if serverstate.AMICOORDINATOR:
            print("[INFO] Handling new identity inside AMICOORDINATOR.")
            
            # the room exists
            isRoomExist = False
            for room in serverstate.ALL_CHAT_ROOMS:
                if room.getChatRoomId() == self._roomid:
                    isRoomExist = True
                    
            if isRoomExist :
                return False, self._roomid, self._message_builder.newChatRoom(self._roomid,"False")

            else:
                # create new chat room instance
                chat_room_instance = LocalRoomInfo()
                chat_room_instance.setChatRoomID(self._roomid)
                chat_room_instance.setOwner(self._identity)
                chat_room_instance.setCoordinator(self._local_server_name)
                chat_room_instance.addMember(self._identity)

                # add to the local chat rooms list
                serverstate.LOCAL_CHAT_ROOMS.append(chat_room_instance)

                # add to the global chat room list
                serverstate.ALL_CHAT_ROOMS.append(chat_room_instance)

                # distribute to the other servers
                message = { "type" : "create_chat_room" , "identity" : self._identity,\
                 "server": self._local_server_name, "roomid" : self._roomid}
                try:
                    self._bully_instance.task_list.append(message)
                except :
                    print("[Error] Error occured while distributing the new chatroom")

                return True, self._roomid, self._message_builder.newChatRoom(self._roomid,"True") 

        else:
            # forward the message to the coordinator
            print("[INFO] Forwarding the create_identity request to coordinator")
            message = { "type" : "create_chat_room" , "identity" : self._identity,\
                 "server": self._local_server_name, "roomid" : self._roomid}
            
            self._bully_instance.send_buffer.append(message)

            while(len(self._bully_instance.receive_buffer) == 0):
                time.sleep(1)
            
            print("[Received]", end="")
            message = json.loads(self._bully_instance.receive_buffer.pop(0))
            print(type(message))
            
            try:
                if message["approved"] == "True" :
                    
                    # create new chat room instance
                    chat_room_instance = LocalRoomInfo()
                    chat_room_instance.setChatRoomID(self._roomid)
                    chat_room_instance.setOwner(self._identity)
                    chat_room_instance.setCoordinator(self._local_server_name)
                    chat_room_instance.addMember(self._identity)

                    # add to the local chat rooms list
                    serverstate.LOCAL_CHAT_ROOMS.append(chat_room_instance)
                    
                    return True, self._roomid, self._message_builder.newChatRoom(self._roomid,"True")  
                else:
                    return False, self._roomid, self._message_builder.newChatRoom(self._roomid,"False") 
            except Exception as e :
                print(e)