import models
import os
from datetime import datetime
from typing import Dict, List, Union
from models.Schedule import Create_Schedule as schedule
from models.baseModel import user_id

default_picture = os.getenv("DEFAULT_PICTURE")
"""
    class Querys and update Users-Profile activities in Redis DB
"""


def SQL_data(ID: str) -> dict:
    courses = schedule(ID)
    user_data = models.storage.access(ID, 'id', user_id)
    available_courses = ["Python", "Javascript", "React", "C"]
    all_courses = []
    active_courses = set()
    for item in available_courses:
        if courses.View(None, item) != {}:
            all_courses.append(courses.View(None, item))

    unique_courses = [
            v['Course'] for item in all_courses for _, v in
            item.items() if (v['Course'] not in active_courses)
            and not active_courses.add(v['Course'])
            ]

    if user_data:
        profile = {
                "Created": user_data.Created_at.strftime("%d %B %Y"),
                "Active_courses": unique_courses
                }
        return profile
    return {}


def get_communities(username: str) -> list:
    community = models.redis_storage.get_list_dict("community")
    my_community = [
            v['name'] for item in community for _, v in item.items()
            if username in v["users"]
            ]
    if my_community:
        return my_community
    return []


class update_redis_profile:
    def __init__(self, ID: str) -> None:
        self.id = ID
        self.data = models.redis_storage.get_list_dict("Users-Profile")
        self.idx = None
        self.item = {}
        self.value = None
        if self.data:
            for idx, profile in enumerate(self.data):
                for key, value in profile.items():
                    if key == ID:
                        self.idx = idx
                        self.item = profile
                        self.value = value

    @property
    def get(self) -> dict:
        if self.value:
            return self.value
        return {}

    @classmethod
    def find_user(cls, username: Union[str, None], ID=None)\
            -> Union[Dict, None]:
        found_user = False
        profile = {}
        for item in models.redis_storage.get_list_dict("Users-Profile"):
            for k, v in item.items():
                if v["username"] == str(username) or k == str(ID)\
                        and v["is_active"]:
                    if v["online_id"] == "":
                        presence = False
                    else:
                        presence = True
                    profile = {
                            "id": k,
                            "username": v["username"],
                            "profile_picture": v["profile_picture"],
                            "Status": v["status"],
                            "online": presence
                            }
                    found_user = True
                    break
        if found_user:
            return profile
        else:
            return

    @classmethod
    def send_friend_request(cls, username: str, ID: str) -> bool:
        for idx, item in enumerate(
                models.redis_storage.get_list_dict("Users-Profile")):
            for k, v in item.items():
                if v["username"] == username and ID not in\
                        v["friend_requests"] and v["is_active"]:
                    v["friend_requests"].append(ID)
                    item[k] = v
                    models.redis_storage.update_list_dict("Users-Profile",
                                                          idx, item)
                    return True
        return False

    @classmethod
    def accept_friend_requests(cls, sender_id: str, reciever_id: str) -> None:
        for idx, item in enumerate(
                models.redis_storage.get_list_dict("Users-Profile")):
            for k, v in item.items():
                if sender_id == k:
                    v["friends"].append(reciever_id)
                    item[sender_id] = v
                    models.redis_storage.update_list_dict("Users-Profile",
                                                          idx, item)

    def save(self) -> None:
        if self.idx is not None:
            models.redis_storage.update_list_dict("Users-Profile", self.idx,
                                                  self.item)

    def save_chatbot_history(self, conversation: dict) -> None:
        if self.value is None:
            return
        self.value["chat_bot"].append(conversation)
        self.item[self.id] = self.value
        self.save()

    def save_userchat_history(self, user_id: str, **kwargs) -> None:
        if self.value is None:
            return
        user_found = False
        for item in self.value["messages"]:
            if item is not None and user_id in item["sender"]:
                item["messages"].append(kwargs)
                user_found = True
                self.item[self.id] = self.value
                self.save()
                break
        if not user_found:
            self.value["messages"].append({"sender": user_id,
                                           "messages": [kwargs]})
            self.item[self.id] = self.value
            self.save()

    def save_profile_picture(self, picture: str) -> None:
        if self.value is None:
            return
        self.value["profile_picture"] = picture
        self.item[self.id] = self.value
        self.save()

    def clear_chatbot_history(self) -> None:
        if self.value is None:
            return
        self.value["chat_bot"].clear()
        self.item[self.id] = self.value
        self.save()

    def update_friends(self, friend_id: str) -> Union[bool, None]:
        if self.value is None:
            return
        if friend_id not in self.value["friends"] or self.value["blocked"] or\
                self.value["is_active"] is not False:
            self.value["friends"].append(friend_id)
            self.item[self.id] = self.value
            self.save()
            return True
        else:
            return False

    def friend_request_remove(self, friend_id: str) -> Union[bool, None]:
        if self.value is None or friend_id not in\
                self.value["friend_requests"]:
            return
        else:
            self.value["friend_requests"].remove(friend_id)
            self.item[self.id] = self.value
            self.save()
            return True

    def view_all_friends(self) -> Union[List, None]:
        friends_list = []
        if self.value is None:
            return
        for item in self.data:
            for k, v in item.items():
                if k in self.value["blocked"] or self.id in v["blocked"]:
                    continue
                if k in self.value["friends"]:
                    users_file = SQL_data(k)
                    communities = get_communities(v["username"])
                    friends = {
                            "id": k,
                            "username": v["username"],
                            "profile_picture": v["profile_picture"],
                            "Status": v["status"],
                            "Created": users_file["Created"],
                            "Active_courses": users_file["Active_courses"],
                            "is_active": v["is_active"],
                            "Communities": communities
                            }
                    friends_list.append(friends)
        return friends_list

    def view_online_friends(self) -> Union[List, None]:
        friends_list = []
        if self.value is None:
            return
        for item in self.data:
            for k, v in item.items():
                if k in self.value["blocked"] or self.id in v["blocked"]:
                    continue
                if k in self.value["friends"] and v["online_id"] != "":
                    users_file = SQL_data(k)
                    communities = get_communities(v["username"])
                    friends = {
                            "id": k,
                            "username": v["username"],
                            "profile_picture": v["profile_picture"],
                            "Status": v["status"],
                            "Created": users_file["Created"],
                            "Active_courses": users_file["Active_courses"],
                            "is_active": v["is_active"],
                            "Communities": communities
                            }
                    friends_list.append(friends)
        return friends_list

    def update_last_seen(self) -> None:
        if self.value is None:
            return
        self.value["last_seen"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.item[self.id] = self.value
        self.save()

    def update_status(self, status: str) -> None:
        if self.value is None:
            return
        self.value["status"] = status
        self.item[self.id] = self.value
        self.save()

    def update_online_id(self, online_id: str) -> Union[bool, None]:
        if self.value is None:
            return
        else:
            self.value["online_id"] = online_id
            self.item[self.id] = self.value
            self.save()
            return True

    def delete_user_profile(self) -> Union[bool, None]:
        if self.value is None:
            return
        self.value["is_active"] = False
        self.value["status"] = "User account deleted"
        self.value["profile_picture"] = default_picture
        self.value["friends"].clear()
        self.value["blocked"].clear()
        self.value["friend_requests"].clear()
        self.value["chat_bot"].clear()
        self.value["messages"].clear()
        self.item[self.id] = self.value
        self.save()
        return True

    def delete_user_chat_history(self, friend_id: str) -> Union[bool, None]:
        """
            method deletes a users conversation history from the database
            based on the ID of the user and the friend they are chatting with
        """
        if self.value is None:
            return
        else:
            for item in self.value["messages"]:
                if item is not None and friend_id in item["sender"]:
                    item["messages"].clear()
                    self.item[self.id] = self.value
                    self.save()
                    return True

    def block_user(self, friend_id: str) -> Union[bool, None]:
        if self.value is None or friend_id not in self.value["friends"]:
            return
        else:
            self.value["friends"].remove(friend_id)
            self.value["blocked"].append(friend_id)
            self.item[self.id] = self.value
            self.save()
            return True

    def unblock_user(self, friend_id: str) -> Union[bool, None]:
        if self.value is None or friend_id not in self.value["blocked"]:
            return
        else:
            self.value["blocked"].remove(friend_id)
            self.value["friends"].append(friend_id)
            self.value["friends"] = list(set(self.value["friends"]))
            self.item[self.id] = self.value
            self.save()
            return True
