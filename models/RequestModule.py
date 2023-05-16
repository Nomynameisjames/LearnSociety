import requests
import os
import smtplib
import wikipedia
import re
from jinja2 import Environment, FileSystemLoader
from requests.structures import CaseInsensitiveDict
from cachetools import cached, TTLCache
from bs4 import BeautifulSoup
from functools import wraps

"""
    cache decorator to save web scrapped data from the wikipedia api
    for a given time
"""
def cached_route(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
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
    def __init__(self):
        self.cache = TTLCache(maxsize=200, ttl=300)

    #@cached_route(ttl=500) 
    def Wikipedia(self, search):
        """
            function makes a request to the wikipedia module and returns a
            wikipedia summary for a given search term
        """
        try:
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
            self.cache[search] = summary
            # print the summary
            return summary
        except Exception as e:
            return e

    def get_wiki_briefs(self, search):
        """
            function makes a request to the get_wiki_briefs api endpoint 
            returns a summary for a given search term
        """
        try:
            url = "https://wiki-briefs.p.rapidapi.com/search" 
            querystring = {"q":search,"topk":"3"}
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
                return response_dict
            else:
                return None
        except Exception as e:
            print(f"Error: {e}")
            return f"error {e}"

    def get_recommendations(self, task):
        """
            method makes a request to the Python documentation website
            and returns a list of topics related to the search term
        """
        url = "https://docs.python.org/3/tutorial/index.html"
        try:
            response = requests.get(url)
            #response.raise_for_status()
            search_word = task
            pattern = re.compile(search_word, re.IGNORECASE)
            soup = BeautifulSoup(response.content, 'html.parser')
            topics = []
            for item in soup.find_all('a', class_='reference internal'):
                if pattern.search(item.text):
                    topics.append({'topic': item.text, 'link': item['href']})
            if topics:
                return topics
            else:
                return None
        except BaseException as exc:
            print(f'There was a problem: {exc}')
            return f'There was a problem: {exc}'
        #except Exception as e:
        #    return f"error {e}"

    def get_resource(self, task):
        """
            method makes a request to the Python documentation website
            taking a task as an argument which is a list of topic links returned
            from the get_recommendations method and returns a list of webscrapped
            data from the Python documentation website
        """
        task = task[0]
        task = task.get('link')
        if task:
            url = f"https://docs.python.org/3/tutorial/{task}"
        #else:
        #    return f'No link found'
            try:
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
                        for tag in file.find_all(['h2', 'p', ('div', "class_='highlight'")]):
                            if tag.name == 'h2':
                                content.append(({'type': 'heading', 'text': tag.text}))
                            elif tag.name == 'p':
                                content.append({'type': 'paragraph', 'text': tag.text})
                            elif tag.name == 'div' and 'highlight' in tag.get('class', []):
                                code = tag.text
                                content.append({'type': 'code', 'text': code})
                        if title and content:
                            section_data.append({'title': title, 'content': content})
                        else:
                            continue
                    return section_data
                else:
                    raise ConnectionError(f'Error: {req.status_code}')
            except ConnectionError as exc:
                print(f'Connection Error: {exc}')
                return f'Connection Error: {exc}'
            except BaseException as exc:
                return f'There was a problem: {exc}'
        else:
            return f'No link found'
        
        #except Exception as exc:
        #    return f'There was a problem: {exc}'


class Notifications:
    """
        class defines all requests to enable sending
        emails and notifications to users
    """
    def __init__(self):
        self.sender_email = os.environ.get('MAIL_USERNAME')
        self.password = os.environ.get('MAIL_PASSWORD')
        self.server = os.environ.get('MAIL_SERVER')
        self.port = os.environ.get('MAIL_PORT')
        self._token = None

    def send_email(self, user, subject, message):
        """
            function sends an email to a given email address by using the
            smtplib module returns True if email is sent successfully
        """
        try:
            self._token = user.generate_confirmation_code()
            code = self._token[0]
            message = f"Hello {user.User_name},\n\n{message}\n\n{code}"
            if not self.sender_email or not self.password:
                return "No email or password found"
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.ehlo()
                server.login(self.sender_email, self.password)
                msg = f"Subject: {subject}\n\n{message}"
                server.sendmail(self.sender_email, user.Email, msg)

            return True
        except Exception as e:
            print("some error occured while sending mail {}".format(e))
            return f"error {e}"

    def close_connection(self):
        """
            function closes the server connection established by the smtplib
            module after each request
        """
        self.server.quit()

    def send_Grid(self, user=None, **kwargs):
        """
            function sends an email to a given email address by using the 
            sendgrid API returns True if email is sent successfully
        """
        try:
            """
                file path points to the directory where the email template is
                stored
            """
            filePath = os.environ.get('FILE_PATH') 
            env = Environment(loader=FileSystemLoader(filePath))
            template = env.get_template('emailFile.html')
            verify_url = kwargs.get('url')
            mail_body = kwargs.get('message')
            header = kwargs.get('header')
            #message = f"Hello {user.User_name},\n\n{message}\n\n{self._token[0]}"
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
                    "from": {"email": self.sender_email}, #change here
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

    def is_valid(self, email: str):
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
                return format_valid and mx_found and smtp_check and state == 'deliverable'
            else:
                raise ConnectionError(f'Error: {response.status_code}')
        except Exception as exc:
            print(f'There was a problem: {exc}')
            return False

