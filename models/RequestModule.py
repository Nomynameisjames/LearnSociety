import requests
import os
import smtplib
import wikipedia
import re
from jinja2 import Environment, FileSystemLoader
from requests.structures import CaseInsensitiveDict
from cachetools import TTLCache
from bs4 import BeautifulSoup
from functools import wraps
from typing import Dict, List, Union, Any, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from .baseModel import user_id
from flask_mail import Message
from flask import current_app

"""
    cache decorator to save web scrapped data from the wikipedia api
    for a given time
"""
load_dotenv()
file_loader = FileSystemLoader(os.getenv('FILE_PATH') or "web_flask/templates")
ENV = Environment(loader=file_loader)


def cached_route(ttl=300) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Use the request path as the cache key
            key = args[1]
            if key in self.cache:
                # Return the cached response if available
                response = self.cache[key]
            else:
                # Call the route function and cache the response
                response = func(self, *args, **kwargs)
                self.cache[key] = response
            return response
        return wrapper
    return decorator


class SearchBar:
    """
        class defines all requests to enable searching
        and web scraping
    """

    wikipedia.set_lang('en')

    def __init__(self) -> None:
        self.__cache = TTLCache(maxsize=500, ttl=4500)

    @property
    def get_cache(self):
        if self.__cache:
            return self.__cache

    def Wikipedia(self, search: str) -> Union[str, bool]:
        """
            function makes a request to the wikipedia module and returns a
            wikipedia summary for a given search term
        """
        try:
            if search in self.__cache:
                return self.__cache[search]
            # check if the search term is spelled correctly
            suggestion = wikipedia.suggest(search)
            if suggestion:
                search = suggestion
            # get the search results
            results = wikipedia.search(search, results=5)
            # get the page summary of the first search result
            page = wikipedia.page(results[0])
            summary = page.summary
            # add the search term and summary to the cache
            self.__cache[search] = summary
            # print the summary
            return summary
        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_wiki_briefs(self, search: str) -> Union[str, Dict[str, Any], None]:
        """
            function makes a request to the get_wiki_briefs api endpoint
            returns a summary for a given search term
        """
        try:
            if search in self.__cache:
                return self.__cache[search]
            url = "https://wiki-briefs.p.rapidapi.com/search"
            querystring = {"q": search, "topk": "3"}
            code = os.getenv('RapidAPI')
            Host = os.getenv('X-RapidAPI-Host') or\
                "wiki-briefs.p.rapidapi.com"
            code = str(code)
            headers = {
                    "X-RapidAPI-Key": code,
                    "X-RapidAPI-Host": Host
                    }
            response = requests.request("GET", url, headers=headers,
                                        params=querystring)
            if response.status_code == 200:
                response_dict = response.json()
                self.__cache[search] = response_dict
                return response_dict
            else:
                return None
        except Exception as e:
            print(f"Error: {e}")
            return

    def get_recommendations(self, task: str)\
            -> Union[str, List[Dict[str, str]], None]:
        """
            method makes a request to the Python documentation website
            and returns a list of topics related to the search term
        """
        url = "https://docs.python.org/3/tutorial/index.html"
        try:
            if task in self.__cache:
                return self.__cache[task]
            response = requests.get(url)
            pattern = re.compile(task, re.IGNORECASE)
            soup = BeautifulSoup(response.content, 'html.parser')
            topics = []
            for item in soup.find_all('a', class_='reference internal'):
                if pattern.search(item.text):
                    topics.append({'topic': item.text, 'link': item['href']})
            if topics:
                self.__cache[task] = topics[0].get('link')
                return topics
            else:
                return None
        except BaseException as exc:
            print(f'There was a problem: {exc}')
            return f'There was a problem: {exc}'

    def get_resource(self, task: List[Dict[str, str]], topic=None)\
            -> Union[str, List[str], None, bool]:
        """
            method makes a request to the Python documentation website
            taking a task as an argument which is a list of topic links
            returned from the get_recommendations method and returns a list
            of webscrapped data from the Python documentation website
        """
        searchword = None
        if topic in self.__cache:
            searchword = self.__cache[topic]
        else:
            searchword = task[0].get('link')
        if searchword:
            url = f"https://docs.python.org/3/tutorial/{searchword}"
            try:
                if url in self.__cache:
                    return self.__cache[url]
                req = requests.get(url)
                req.raise_for_status()
                req.status_code
                if req.status_code == 200:
                    soup = BeautifulSoup(req.content, 'html.parser')
                    section_data = []
                    for file in soup.find_all('section'):
                        content = []
                        title = ''
                        for idx, item in enumerate(file.find_all(['h1', 'p'])):
                            if idx > 0:
                                break
                            if item.name == 'h1':
                                title = item.text
                        for tag in file.find_all(
                                ['h2', 'p', ('div', "class_='highlight'")]
                                ):
                            if tag.name == 'h2':
                                content.append(({'type': 'heading',
                                                 'text': tag.text}))
                            elif tag.name == 'p':
                                content.append({'type': 'paragraph',
                                                'text': tag.text})
                            elif tag.name == 'div' and 'highlight' in\
                                    tag.get('class', []):
                                code = tag.text
                                content.append({'type': 'code', 'text': code})
                        if title and content:
                            section_data.append({'title': title,
                                                 'content': content})
                        else:
                            continue
                    self.__cache[url] = section_data
                    return section_data
                else:
                    raise ConnectionError(f'Error: {req.status_code}')
            except ConnectionError as exc:
                print(f'Connection Error: {exc}')
                return False
            except BaseException as exc:
                print(f'There was a problem: {exc}')
                return False
        else:
            return


class Notifications:
    """
        class defines all requests to enable sending
        emails and notifications to users
    """
    def send_mail(self, subject: str, to_email: str, temp_name: str, temp_context: dict) -> bool:
        """
            Sends an email to a specified recipient using a rendered template.

            Args:
                subject (str): The subject of the email.
                to_email (str): The email address of the recipient.
                temp_name (str): The name of the template to use for the email body.
                temp_context (dict): A dictionary of variables to render in the template.

            Returns:
                bool: True if the email is sent successfully, False otherwise.

            Raises:
                Exception: If an error occurs while sending the email or failed to access 
                the mail settings, an exception is logged and False is returned.

            Notes:
                This function uses the Flask-Mail extension to send emails. It retrieves the email template from the Jinja2 environment,
                renders it with the provided context, and sends the resulting HTML message to the specified recipient.
        """
        
        template = ENV.get_template(temp_name)
        message = template.render(temp_context)
        
        msg = Message(subject, recipients=[to_email], html=message)
        
        try:
            mail = current_app.extensions["mail"]
            mail.send(msg)

        except KeyError as err:
            current_app.logger.error("Flask Mail not installed, initialize and re-run")
            return False
        
        except smtplib.SMTPRecipientsRefused as err:
            current_app.logger.warning(err)
            return False
            
        except Exception as err:
            current_app.logger.error(err, exc_info=True)
            return False
        
        return True
