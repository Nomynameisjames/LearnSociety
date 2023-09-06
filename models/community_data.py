import os
from . import redis_storage
from .Update_Profile import update_redis_profile
from typing import Union, List
from dotenv import load_dotenv

load_dotenv()
default_picture = os.getenv("DEFAULT_PICTURE")


class CommunityData:
    """
        class holds all logic involved in manipulating the community data
        saved in the redis data base
    """
    def __init__(self, community_id=None):
        """
            gets the community_id to return information about a particular
            community defualts to None to return all communities
        """
        self.community_id = community_id
        self.__data = None
        self.__community_profile = {}
        if not self.__data:
            self.__data = redis_storage.get_list_dict("community")

    @property
    def get_community(self):
        """
            returns the community profile of a particular community
            if community_id is not None else returns an empty dictionary
        """
        if not self.__data:
            return None
        for item in self.__data:
            for key, value in item.items():
                if self.community_id is not None and self.community_id in key:
                    self.__community_profile = value
        return self.__community_profile

    @property
    def get_all_community(self):
        """
            returns a list of all communities
        """
        return self.__data

    @classmethod
    def edit_community_profile(cls, room_code: str, username: str, **kwargs)\
            -> bool:
        """
            edits the profile of a community if the user is a member of the
            community and has admin privileges
        """
        all_community = cls().get_all_community
        if not all_community:
            return False
        for idx, item in enumerate(all_community):
            for key, value in item.items():
                if value["code"] == room_code.strip() and\
                        value["admin"] == username.strip():
                    if kwargs:
                        value["name"] = kwargs.get("new_name")
                        value["description"] = kwargs.get("description")
                    else:
                        value["chat"].clear()
                    item[key] = value
                    redis_storage.update_list_dict("community", idx, item)
                    return True
        return False

    def join_community(self, username: str, room_code: str)\
            -> Union[dict, None]:
        """
            adds a user to a community if the user is not already a member
            also validates the room_code to ensure that the user is joining
            the right community
        """
        all_community = self.get_all_community
        payload = {}
        if not all_community:
            return None
        for idx, item in enumerate(all_community):
            for key, value in item.items():
                if username not in value["users"] and str(room_code)\
                        == value["code"]:
                    value["users"].append(username)
                    item[key] = value
                    redis_storage.update_list_dict("community", idx, item)
                    payload = {
                            "room": value["name"],
                            "id": key,
                            "username": username,
                            "code": value["code"]
                            }
                    break
        return payload

    def leave_community(self, username: str, room_id: str) -> Union[str, None]:
        """
            removes a user from a community
        """
        all_community = self.get_all_community
        room_code = None
        if not all_community:
            return None
        for idx, item in enumerate(all_community):
            for key, value in item.items():
                if username in value["users"] and str(room_id)\
                        == value["code"]:
                    room_code = value["code"]
                    value["users"].remove(username)
                    item[key] = value
                    redis_storage.update_list_dict("community", idx, item)
                    break
            return room_code

    def update_chat_history(self, username: str, room_id: str, **payload)\
            -> Union[str, None]:
        """
            updates the chat history of a particular community
            username: the username of the user sending the message
            room_id: the id of the community
            payload: the message to be sent
            returns the room code
        """
        all_community = self.get_all_community
        code = None
        if not all_community:
            return None
        for idx, item in enumerate(all_community):
            for key, value in item.items():
                if username in value["users"] and str(room_id) == key:
                    payload.pop("sender_id", None)
                    payload.pop("profile_pic", None)
                    value["chat"].append(payload)
                    item[key] = value
                    code = value["code"]
                    redis_storage.update_list_dict("community", idx, item)
                    break
        return code

    def get_chat_history(self):
        """
            returns the chat history of a particular community
        """
        if not self.__community_profile:
            return None
        return self.__community_profile.get("chat")

    def get_members(self):
        """
            returns the members of a particular community
        """
        if not self.__community_profile:
            return None
        return self.__community_profile.get("users")

    def get_members_profile(self, current_user: str)\
            -> Union[List[dict], None]:
        """
            returns the profile of all members of a particular community
            current_user: the username of the user requesting the profile
        """
        if not self.__community_profile:
            return None
        members_profile = {}
        active_chat = self.get_chat_history()
        if not active_chat:
            return None
        # Iterate through the chat history
        for item in active_chat:
            name = item["name"]
            if name != current_user and name not in members_profile:
                unique_data = update_redis_profile.find_user(name, None)
                if unique_data:
                    if unique_data.get("profile_picture") == "":
                        unique_data["profile_picture"] = default_picture
                    members_profile[name] = {
                        "username": unique_data.get("username"),
                        "profile_picture": unique_data.get("profile_picture"),
                    }
        # Convert the dictionary to a list of unique profiles
        unique_data_list = [
                {"username": data["username"],
                 "profile_picture": data["profile_picture"]
                 } for data in members_profile.values()
                ]
        return unique_data_list
