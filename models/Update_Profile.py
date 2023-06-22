import models
from datetime import datetime

"""
    class Querys and update Users-Profile activities in Redis DB
"""

class update_redis_profile:
    def __init__(self, ID):
        self.id = ID
        self.data = models.redis_storage.get_list_dict("Users-Profile")
        self.idx = None
        self.item = None
        self.value = None
        if self.data:
            for idx, profile in enumerate(self.data):
                for key, value in profile.items():
                    if key == ID:
                        self.idx = idx
                        self.item = profile
                        self.value = value

    @property
    def get(self):
        if self.value:
            return self.value
        return {}

    def save(self):
        models.redis_storage.update_list_dict("Users-Profile", self.idx, self.item)

    def save_chatbot_history(self, conversation):
        if self.value is None: 
            return
        self.value["chat_bot"].append(conversation)
        self.item[self.id] = self.value
        self.save()

    def clear_chatbot_history(self):
        if self.value is None: 
            return
        self.value["chat_bot"].clear()
        self.item[self.id] = self.value
        self.save()

    def update_last_seen(self):
        if self.value is None: 
            return
        self.value["last_seen"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.item[self.id] = self.value
        self.save()

    def delete_user_profile(self):
        data = models.redis_storage.delete_list_dict_item("Users-Profile", self.idx, self.id)
        return data

