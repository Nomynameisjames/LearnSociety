#!/bin/bash

# Prompt for storage type
read -p "Enter storage type [$STORAGE_TYPE]: " storage_type
if [[ -z "$storage_type" ]]; then
    storage_type="$STORAGE_TYPE"
fi

if [[ -z "${MYSQL_USR}" ]]; then
    read -p "Enter MySQL username (default: root): " MYSQL_USR
    MYSQL_USR=${MYSQL_USR:-root}
fi

# Check if MYSQL_HOST is set, and prompt if not
if [[ -z "${MYSQL_HOST}" ]]; then
    read -p "Enter MySQL host: " MYSQL_HOST
fi


# Check if MYSQL_PASS is set, and prompt if not
if [[ -z "${MYSQL_PASS}" ]]; then
    read -p "Enter MySQL password: " MYSQL_PASS
fi


# Check if MYSQL_DB is set, and prompt if not
if [[ -z "${MYSQL_DB}" ]]; then
    read -p "Enter MySQL database: " MYSQL_DB
fi

# Check if MYSQL_DB is set, and prompt if not
if [[ -z "${PORT}" ]]; then
    read -p "Enter MySQL database: (default: 3306): " PORT
fi

# Check if OPENAI_API_KEY is set, and prompt if not
if [[ -z "${OPENAI_API_KEY}" ]]; then
    read -p "Enter OpenAI API key: " OPENAI_API_KEY
fi

# Check if TWILIO_AUTH_TOKEN is set, and prompt if not
if [[ -z "${TWILIO_AUTH_TOKEN}" ]]; then
    read -p "Enter Twilio auth token: " TWILIO_AUTH_TOKEN
fi

# Set storage type variables
export STORAGE_TYPE="$storage_type"
export STORAGE_TYPE2="redisDB"

# Prompt for additional environment variables
read -p "Enter additional environment variables (variable=value) [Press Enter to skip]: " env_vars
while [[ -n "$env_vars" ]]; do
    export "$env_vars"
    read -p "Enter additional environment variables (variable=value) [Press Enter to finish]: " env_vars
done

# Set Python path
export PYTHONPATH="$PYTHONPATH:$(pwd)"

read -p "for optimal performance it is recommended to set you openai api key and twilio auth key, do you want to? (y/n): " confirm

if [[ $confirm == "y" ]]; then
    # Prompt the user to enter the additional variables
    read -p "Enter OPENAI_API_KEY: " OPENAI_API_KEY
    read -p "Enter TWILIO_AUTH_TOKEN: " TWILIO_AUTH_TOKEN
fi

# Run the command
python3 web_flask/app.py

