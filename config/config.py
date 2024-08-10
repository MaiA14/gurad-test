import os
import json

class Config:
    _conf = {}
    
    @staticmethod
    def load_stream_config():
        config_path = os.getenv("STREAM_CONFIG_PATH")
        if not config_path:
            raise ValueError("Environment variable STREAM_CONFIG_PATH not set")
        with open(config_path, "r") as file:
            Config._conf = json.load(file)
            
    @staticmethod
    def get_stream_config_value(key):
        return Config._conf.get(key)

    @staticmethod
    def update_rules(rules) -> None:
        if 'rules' in Config._conf:
            Config._conf['rules'] = rules
        else:
            raise KeyError("Key 'rules' not found in configuration")

    @staticmethod
    def save_rules() -> None:
        config_path = os.getenv("STREAM_CONFIG_PATH")
        if not config_path:
            raise ValueError("Environment variable STREAM_CONFIG_PATH not set")

        try:
            with open(config_path, "w") as file:
                json.dump(Config._conf, file, indent=4)
        except IOError as e:
            raise RuntimeError(f"Error writing to config file: {e}")
