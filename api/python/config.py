# sanic_config.py

import os


class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))


def load_config():
    return Config
