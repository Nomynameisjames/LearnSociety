# LearnSociety Learning
It's all about Simplifying Learning and Amplifying Success. We explore an Easy-to-Use Learning Management System that Enhances Engagement and Accelerates Learning Outcomes.

## Introduction
LearnSociety is a web application that aims to facilitate task management and learning progression. It allows users to break down tasks into daily subroutines, track their productivity, and visualize their progress on a graph chart.

The application also provides resources and guidance for acquiring programming skills. Additionally, it features real-time chat functionality for users interactions and a blog post feature(*still in development stage*) for sharing perspective and receiving feedback.

## Team Members
- Aitebiremen Okojie
- Adava Onimisi
- Ernest Aiji
- Sammy Iyebhora

## Installation
This project is built with python as such it's needed for running this project.
- installing python on apt based system
```
sudo apt-get update
sudo apt-get install -y python3
sudo apt-get install -y python3-pip
```
- installing project packages
```
sudo apt-get install -y mysql-server
sudo apt-get install -y mysql-client
sudo apt-get insall -y python3-dev default-libmysqlclient-dev build essential
sudo apt-get install -y redis
```
*make sure you take note of your mysql login credentials during mysql insallation*
- install the python modules
```
pip3 install -r requirements.txt
```
-  create the following environmental variables either on shell or on `~/.bashrc` file (`~/.bashrc` is more preferrable)
```bash
export MYSQL_USER="mysql_user_name"
export MYSQL_HOST="<server_machine_ip | localhost>"
export MYSQL_PASS="your_mysql_password"
export MYSQL_DB="name_of_db_in_mysql"
export STORAGE_TYPE="< mysqlDB | filestorageDB >"
export PORT="mysql_port"
export SECRET_KEY="flask_app_Secret_key"
export GOOGLE_CLIENT_ID="google_client_key"
export GOOGLE_SECRET_KEY="google_client_key"
export GOOGLE_CALLBACK_URL="google_client_callback_url"
```
- head over to google developers to create application key and download the `client_secrets.json` file
- copy or move `clients_secrets.json` file to `web_flask/main/client_Secrets.json`

### run
```
$ ./start_flask_server.sh
#just press enter
Enter storage type [mysqlDB]:
# enter your corresponding api key if available else press enter
Enter OpenAI API key:
Enter Twilio auth token:
Enter additional environment variables (variable=value) [Press Enter to skip]:
for optimal performance it is recommended to set you openai api key and twilio auth key, do you want to? (y/n):n
# specify app to run flask application or api to run api service
Do you want to start the Flask app or the API route? (app/api)
```
## Technologies
### Front-end:
- HTML (Hypertext Markup Language): Markup language for structuring web pages.
- CSS (Cascading Style Sheets): Stylesheet language for styling web pages.
- JavaScript: Programming language for adding interactivity and dynamic behavior to web pages.
- Frontend libraries/Framework: Bootstrap, JQuery
### Backend
- Programming language: Python.
- Databases: MySQL (for storing structured data e.g user table, courses table, library table), redisDB  for caching and storing unstructured data like chats.
- RESTful APIs: Design and development of APIs for communication between the front-end and back-end components.
- Flask socketIO: For real time communication between users.
### Server and Hosting:
- Web servers: Nginx
- Cloud platforms: AWS (Amazon Web Services).
### Security
- Authentication and authorization: Flask login, Flask Session, JWT (JSON Web Tokens), etc.
- Encryption and secure communication: HTTPS, SSL/TLS certificates.
### 3rd Party services
- OpenAI API for chatbot functionality
- SendGrid API for sending user emails
- Twilio API for notification functionality
- Getwiki API for web page search bar functionality
