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
from .baseModel import user_id

"""
    cache decorator to save web scrapped data from the wikipedia api
    for a given time
"""
file_loader = FileSystemLoader(os.environ.get('FILE_PATH'))
env = Environment(loader=file_loader)
template = env.get_template('emailFile.html')


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
            code = os.environ.get('RapidAPI')
            Host = os.environ.get('X-RapidAPI-Host') or\
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
    def __init__(self) -> None:
        self.sender_email = os.environ.get('MAIL_USERNAME')
        self.password = os.environ.get('MAIL_PASSWORD')
        self.server = os.environ.get('MAIL_SERVER')
        self.port = os.environ.get('MAIL_PORT')
        self._token = None
        self.server_connection = None

    def send_email(self, user: user_id, subject: str, message: str) -> Any:
        """
            function sends an email to a given email address by using the
            smtplib module returns True if email is sent successfully
        """
        try:
            self._token = user.generate_confirmation_code()
            code = self._token[0]
            message = f"{message}\n\n{code}"
            if not self.sender_email or not self.password:
                return False
            if self.server and self.port:
                file = [message, subject, user.User_name]
                html_content = template.render(file=file, url=None)
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = user.Email
                msg['Subject'] = subject
                msg.attach(MIMEText(html_content, 'html'))
                with smtplib.SMTP(self.server, int(self.port))\
                        as self.server_connection:
                    self.server_connection.starttls()
                    self.server_connection.ehlo()
                    self.server_connection.login(self.sender_email,
                                                 self.password)
                    self.server_connection.sendmail(self.sender_email,
                                                    user.Email,
                                                    msg.as_string())
                return True
        except Exception as e:
            print("some error occured while sending mail {}".format(e))
            return False

    def close_connection(self):
        """
            function closes the server connection established by the smtplib
            module after each request
        """
        if self.server_connection:
            self.server_connection.quit()

    def send_Grid(self, user=None, **kwargs) -> Union[bool, Any]:
        """
            function sends an email to a given email address by using the
            sendgrid API returns True if email is sent successfully
        """
        try:
            """
                file path points to the directory where the email template is
                stored
            """
            verify_url = kwargs.get('url')
            mail_body = kwargs.get('message')
            header = kwargs.get('header')
            if user:
                username = user.User_name
                email = user.Email
            else:
                username = kwargs.get('username')
                email = kwargs.get('email')
            subject = kwargs.get('subject')
            file = [mail_body, header, username]
            html_content = template.render(file=file, url=verify_url)
            URL = "https://rapidprod-sendgrid-v1.p.rapidapi.com/mail/send"
            tok = os.environ.get('RapidAPI')
            Host = "rapidprod-sendgrid-v1.p.rapidapi.com"
            tok = str(tok)
            payload = {
                    "personalizations": [
                        {
                            "to": [{"email": email}],
                            "subject": subject
                            }
                        ],
                    "from": {"email": self.sender_email},
                    "content": [
                        {
                            "type": "text/html",
                            "value": html_content
                            }
                        ]
                    }
            headers = {
                    "content-type": "application/json",
                    "X-RapidAPI-Key": tok,
                    "X-RapidAPI-Host": Host
                    }
            response = requests.post(URL, json=payload, headers=headers)

            if response.status_code == 202:
                return True
        except Exception as e:
            print("some error occured while sending email {}".format(e))
            raise ValueError(f"Error sending email: {e}")

    def is_valid(self, email: str) -> Any:
        """
            function checks if an email address is valid by using the
            emailvalidation.io API returns True if email is valid
        """
        url = f"https://api.emailvalidation.io/v1/info?email={email}"

        headers = CaseInsensitiveDict()
        headers['apikey'] = os.environ.get('MAIL_VALIDATE')
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_resp = response.json()
                format_valid = json_resp['format_valid']
                mx_found = json_resp['mx_found']
                smtp_check = json_resp['smtp_check']
                state = json_resp['state']
                return format_valid and mx_found and smtp_check and\
                    state == 'deliverable'
            else:
                raise ConnectionError(f'Error: {response.status_code}')
        except Exception as exc:
            print(f'There was a problem: {exc}')
            return False
