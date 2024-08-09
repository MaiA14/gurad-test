import os
import json

class Config:
    @staticmethod
    def load_stream_config():
        config_path = os.getenv("STREAM_CONFIG_PATH")
        if not config_path:
            raise ValueError("Environment variable STREAM_CONFIG_PATH not set")
        with open(config_path, "r") as file:
            return json.load(file)


    @staticmethod
    def get_stream_config_value(key):
        config = Config.load_stream_config()
        return config.get(key)