#!/usr/bin/env python3
from .app import app
from dotenv import load_dotenv
import os

load_dotenv()
Host = os.getenv('HBNB_API_HOST', '127.0.0.1')
Port = os.getenv('HBNB_API_PORT', '5001')


if __name__ == "__main__":
    app.run(host=Host, port=Port)
