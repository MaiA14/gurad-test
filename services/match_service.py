from typing import Dict, Any, List
from config.config import Config
import re
import operator
import httpx
import json

class MatchService: 
    @staticmethod   
    def match_check(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        print('match_check', data)
        
        pokemon = data.get('pokemon_data', {})
        rules = Config.load_rules_config()["rules"]
        matching_rules = []
        
        for rule in rules:
            if MatchService._process_conditions(rule.get('match', []), pokemon):
                matching_rules.append(rule)
        return matching_rules
    
    @staticmethod    
    def process_matches(data: dict) -> None:
        print('process_matches ', data)

        matched_rules = MatchService.match_check(data)
        if matched_rules:
            MatchService.notify_subscribers(data, matched_rules)

    @staticmethod             
    def notify_subscribers(pokemon_message: dict, matched_rules: list) -> None:
        print('notify_subscribers', pokemon_message, matched_rules)
        
        pokemon_info = pokemon_message.get('pokemon_data', {})
        headers_from_message = pokemon_message.get('headers', {})
        pokemon_proto = json.dumps(pokemon_info)

        print('notify_subscribers final data', pokemon_proto, headers)
        
        try:
            with httpx.AsyncClient() as client:
                for rule in matched_rules:
                    subscriber_url = rule.get('url')
                    reason = rule.get('reason')
                    payload = pokemon_proto
                    headers = {
                        "Content-Type": "application/json",
                        "X-Grd-Reason": reason
                    }
                    headers.update(headers_from_message)
                         
                    print('Attempting to forward request to ', subscriber_url, headers, payload)
                    response = client.post(subscriber_url, json=payload, headers=headers)
                      
                    if response.status_code == 200:
                        print('Notification sent successfully to ', subscriber_url)
                    else:
                        print('Failed to send notification to ', subscriber_url, response.status_code, response.text)
                        
        except httpx.RequestError as e:
                    print('Error sending notification to ', subscriber_url, str(e))

    @staticmethod
    def _process_conditions(conditions: List[str], pokemon: Dict[str, Any]) -> bool:
        print('_process_conditions ', conditions, pokemon)
        all_conditions_met = True
        
        for condition in conditions:
            condition = condition.strip()
            print(f"Checking condition: {condition}")
            
            if not MatchService._evaluate_condition(condition, pokemon):
                all_conditions_met = False
                break
        
        return all_conditions_met
    
    @staticmethod
    def _check_equal(pokemon_value: Any, condition_value: Any) -> bool:
        print('_check_equal ', pokemon_value, condition_value)
        return pokemon_value == condition_value
    
    @staticmethod
    def _check_not_equal(pokemon_value: Any, condition_value: Any) -> bool:
        print('_check_not_equal ', pokemon_value, condition_value)
        return pokemon_value != condition_value
    
    @staticmethod
    def _check_greater_than(pokemon_value: Any, condition_value: Any) -> bool:
        print('_check_greater_than ', pokemon_value, condition_value)
        return pokemon_value > condition_value
    
    @staticmethod
    def _check_less_than(pokemon_value: Any, condition_value: Any) -> bool:
        print('_check_less_than ', pokemon_value, condition_value)
        return pokemon_value < condition_value
    
    @staticmethod
    def _evaluate_condition(condition: str, pokemon: Dict[str, Any]) -> bool:
        print('_evaluate_condition ', condition, pokemon)
        operators = {
            '==': MatchService._check_equal,
            '!=': MatchService._check_not_equal,
            '>': MatchService._check_greater_than,
            '<': MatchService._check_less_than
        }
        
        for operator, check_function in operators.items():
            if operator in condition:
                key, value = MatchService._parse_condition(condition, operator)
                if not check_function(pokemon.get(key), value):
                    print(f"Condition failed: {key} {operator} {value} (pokemon.get({key}) = {pokemon.get(key)})")
                    return False
        
        return True
    
    @staticmethod
    def _parse_condition(condition: str, operator: str) -> (str, Any):
        print('_parse_condition ', condition, operator)
        key, value = condition.split(operator)
        key = key.strip()
        value = value.strip().strip("'")
        
        if value.isnumeric():
            value = int(value)
        
        return key, value