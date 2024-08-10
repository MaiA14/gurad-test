from typing import Dict, Any, List
import re
import operator
import httpx
import json
import logging
from config.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MatchService:
    @staticmethod   
    def match_check(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        logging.info('match_check: %s', data)
        
        pokemon = data.get('pokemon_data', {})
        rules = Config.load_stream_config()["rules"]
        matching_rules = []
        
        for rule in rules:
            if MatchService._process_conditions(rule.get('match', []), pokemon):
                matching_rules.append(rule)
        return matching_rules
    
    @staticmethod    
    async def process_matches(data: dict) -> None:
        logging.info('process_matches: %s', data)

        matched_rules = MatchService.match_check(data) 
        print('matched_rules ', matched_rules)
        if matched_rules:
            await MatchService.notify_subscribers(data, matched_rules)

    @staticmethod             
    async def notify_subscribers(pokemon_message: dict, matched_rules: list) -> None:  
        logging.info('notify_subscribers: %s, %s', pokemon_message, matched_rules)
        
        pokemon_info = pokemon_message.get('pokemon_data', {})
        headers_from_message = pokemon_message.get('headers', {})
        converted_pokemon_dict_to_proto = json.dumps(pokemon_info)

        logging.info('notify_subscribers pokemon_info: %s', converted_pokemon_dict_to_proto)
        logging.info('notify_subscribers headers_from_message: %s', headers_from_message)
        
        try:
            with httpx.AsyncClient() as client:
                for rule in matched_rules:
                    subscriber_url = rule.get('url')
                    reason = rule.get('reason')
                    payload = converted_pokemon_dict_to_proto
                    headers = {
                        "Content-Type": "application/json",
                        "X-Grd-Reason": reason
                    }
                    headers.update(headers_from_message)
                         
                    logging.info('Attempting to forward request to %s with headers %s and payload %s', subscriber_url, headers, payload)
                    response = await client.post(subscriber_url, json=payload, headers=headers)
                        
                    if response.status_code == 200:
                        logging.info('Notification sent successfully to %s', subscriber_url)
                    else:
                        logging.error('Failed to send notification to %s: %d %s', subscriber_url, response.status_code, response.text)
                        
        except httpx.RequestError as e:
            logging.error('Error sending notification: %s', str(e))

    @staticmethod
    def _process_conditions(conditions: List[str], pokemon: Dict[str, Any]) -> bool:
        logging.info('_process_conditions: %s, %s', conditions, pokemon)
        all_conditions_met = True
        
        for condition in conditions:
            condition = condition.strip()
            logging.info('Checking condition: %s', condition)
            
            if not MatchService._evaluate_condition(condition, pokemon):
                all_conditions_met = False
                break
        
        return all_conditions_met
    
    @staticmethod
    def _check_equal(pokemon_value: Any, condition_value: Any) -> bool:
        logging.info('_check_equal: %s, %s', pokemon_value, condition_value)
        return pokemon_value == condition_value
    
    @staticmethod
    def _check_not_equal(pokemon_value: Any, condition_value: Any) -> bool:
        logging.info('_check_not_equal: %s, %s', pokemon_value, condition_value)
        return pokemon_value != condition_value
    
    @staticmethod
    def _check_greater_than(pokemon_value: Any, condition_value: Any) -> bool:
        logging.info('_check_greater_than: %s, %s', pokemon_value, condition_value)
        return pokemon_value > condition_value
    
    @staticmethod
    def _check_less_than(pokemon_value: Any, condition_value: Any) -> bool:
        logging.info('_check_less_than: %s, %s', pokemon_value, condition_value)
        return pokemon_value < condition_value
    
    @staticmethod
    def _evaluate_condition(condition: str, pokemon: Dict[str, Any]) -> bool:
        logging.info('_evaluate_condition: %s, %s', condition, pokemon)
        
        operators = {
            '==': MatchService._check_equal,
            '!=': MatchService._check_not_equal,
            '>': MatchService._check_greater_than,
            '<': MatchService._check_less_than
        }
        
        for op, check_function in operators.items():
            if op in condition:
                key, value = MatchService._parse_condition(condition, op)
                if not check_function(pokemon.get(key), value):
                    logging.info('Condition failed: %s %s %s (pokemon.get(%s) = %s)', key, op, value, key, pokemon.get(key))
                    return False
        return True
    
    @staticmethod
    def _parse_condition(condition: str, operator: str) -> (str, Any):
        logging.info('_parse_condition: %s, %s', condition, operator)
        key, value = condition.split(operator)
        key = key.strip()
        value = value.strip().strip("'").lower() 
        
        if value.isnumeric():
            value = int(value)
        elif value in ['true', 'false']:  
            value = value == 'true'
        elif value in ['none', 'null']:  
            value = None
        return key, value