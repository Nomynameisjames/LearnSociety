#!/usr/bin/python3i
from models.Schedule import Create_Schedule
from .baseModel import user_id
import os
import models
import openai
import json
import yaml
import logging


class Checker:
    """
        class method uses the openAI API to invoke a text-davinci-3 chatbot
        to handle user quiz session and a chatGPT-3 chatbot to handle
        user help session
    """
    task_ID = None

    def __init__(self, my_id, table=None):
        """
            init method takes in the user id and the table name as parameters
            table name results to default for self customised tasks and if none
            the specified user automated schedule is queried from the database
            to establish a quiz session
        """
        self.my_id = my_id
        self.table = table
        self.schedule = Create_Schedule(self.my_id)
        if self.table:
            self.task = self.schedule.View(self.my_id, "daily", self.table)
        else:
            self.task = self.schedule.View(self.my_id, "daily")
        for key, _ in self.task.items():
            self.task_ID = key
            text = self.task[key]['Topic']
            self.question = f"""test my knowledge on the following topic {text}
                            by asking exactly 10 none objective questions"""
    
    """
        class method generate average score gotten from the user quiz section
        based on the response received from openai api request
    """
    @classmethod
    def check_answers(cls, data, ID, key):
        try:
            response_dict = data
            DB = None
            num_true = len(response_dict["True"])
            num_false = len(response_dict["False"])
            if num_true + num_false == 0:
                average = 0
            else:
                average = num_true / (num_true + num_false) * 100

            if ID and key is not None:
                DB = models.storage.access(ID, 'id', user_id)
            if DB is not None:
                DB = DB.schedules
                for index, task in enumerate(DB):
                    if task.id == key:
                        DB[index].Average = average
                        DB[index].Target = 1
                        models.storage.save()
            return average
        except Exception as e:
            return f"the following Error occured {e}"

    """
        class method uses the openAI API to invoke a chatbot to check and
        validate the quiz answers sent from the user quiz session
        and then return a dictionary of the true and false answers
    """
    @classmethod
    def _invoke_chatbot(cls, data):
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        try:
            openai.api_key = os.environ['OPENAI_API_KEY']
            response_dict = {"True": {}, "False": {}}
            Value = None
            for _, v in data.items():
                Value = v
            if Value is None:
                return response_dict

            for question, answer in Value.items():
                prompt = f"""Based on this question: {question}, determine
                            if the following statement is true or false:
                            {answer}? If the answer cannot be determined,
                            please respond with false."""
                response = openai.Completion.create(
                                model="text-davinci-003",
                                prompt=prompt,
                                temperature=0.3,
                                max_tokens=200,
                                top_p=1.0,
                                frequency_penalty=0.0,
                                presence_penalty=0.0)
# Quary API response to get questions that have a true  or false value key
                if response.choices and "True" in response.choices[0].text:
                    response_dict["True"][question] = answer
                elif response.choices and "False" in response.choices[0].text:
                    response_dict["False"][question] = answer
            with open('checked_answer.json', 'a') as file:
                json.dump(response_dict, file)
            return response_dict
        except Exception as e:
            raise Exception(f"Error invoking chatbot {e}")

    def Help(self, message):
        """
            class method uses the openAI API to invoke a chatbot to recommend
            resources based on the daily topic queried from the database
            or questions asked
        """
        try:
            usr = models.storage.access(self.my_id, 'id', user_id)
            opt = message
            cache_key = f"conv_ID_{self.my_id}"
            conversation_history = models.redis_storage.get_list(cache_key)

            conversation_history.append({"role": "user", "content": opt,
                                         "ID": self.my_id})
            messages = [
                        {"role": "system", "content": f"{opt}"}
                ]
            answer = self.Bot(messages)
            """
                returns a JSON value of the API response
            """
            if not usr.save_history:
                conversation_history.append({"role": "bot", "content": answer,
                                        "ID": self.my_id})
                models.redis_storage.set_dict(cache_key, conversation_history, ex=86400)
            return answer.strip()
        except Exception as e:
            raise Exception(f"Error invoking chatbot {e}")

    def Question(self, **kwargs):
        """
            class method uses the openAI API to invoke a chatbot to generate
            questions based on the daily topic queried from the database
            or questions asked
        """
        try:
            if kwargs:
                opt = kwargs.get('question')
            else:
                opt = self.question
            dic = {}
            new_dic = {}
            model = "text-davinci-003"
            data = self.Bot(opt, model)
            dic["tasks"] = data
            obj = dic["tasks"].split("\n")
            for key in range(len(obj)):
                new_dic[key] = obj[key]
            new_dic = {key: value for key, value in new_dic.items()
                       if value != ''}
            with open('tasks.yaml', 'a') as file:
                yaml.dump(new_dic, file)
            return new_dic
        except Exception as e:
            print(f"Error invoking chatbot {e}")

    def Bot(self, prompt, model=None):
        """
            Bot method allows to indicate which model to use for the
            openAI API request
        """
        openai.api_key = os.environ['OPENAI_API_KEY']
        if model is None:
            model = "gpt-3.5-turbo"
            response = openai.ChatCompletion.create(
                    model=model,
                    messages=prompt,
                    temperature=0.3,
                    max_tokens=150,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                    )
            answer = response['choices'][0]['message']['content'].strip()
            return answer
        else:
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=0.3,
                max_tokens=150,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
                )
            answer = response['choices'][0]['text'].strip()
            return answer
