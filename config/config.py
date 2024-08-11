import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    _conf = {}
    
    @staticmethod
    def load_stream_config():
        logging.info('load_stream_config')
        config_path = os.getenv("STREAM_CONFIG_PATH")
        if not config_path:
            raise ValueError("Environment variable STREAM_CONFIG_PATH not set")
        with open(config_path, "r") as file:
            Config._conf = json.load(file)
            
    @staticmethod
    def get_stream_config_value(key):
        logging.info('get_stream_config_value: %s', key)
        return Config._conf.get(key)

    @staticmethod
    def update_rules(rules) -> None:
        logging.info('update_rules: %s', rules)
        if 'rules' in Config._conf:
            Config._conf['rules'] = rules
        else:
            raise KeyError("Key 'rules' not found in configuration")

    @staticmethod
    def save_rules() -> None:
        logging.info('save_rules:')
        config_path = os.getenv("STREAM_CONFIG_PATH")
        if not config_path:
            raise ValueError("Environment variable STREAM_CONFIG_PATH not set")

        try:
            with open(config_path, "w") as file:
                json.dump(Config._conf, file, indent=4)
        except IOError as e:
            raise RuntimeError(f"Error writing to config file: {e}")
