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
    async def notify_subscribers(pokemon_message: Dict[str, Any], matched_rules: List[Dict[str, Any]]) -> None:
        print('notify_subscribers', pokemon_message, matched_rules)
        
        pokemon_info = pokemon_message.get('pokemon_data', {})
        proto_pokemon = MatchService._convert_pokemon_info_to_json(pokemon_info)
        headers_from_message = pokemon_message.get('headers', {})
        
        print('notify_subscribers pokemon_info ', proto_pokemon)
        print('notify_subscribers headers_from_message ', headers_from_message)
        
        async with httpx.AsyncClient() as client:
            try:
                for rule in matched_rules:
                    subscriber_url = rule.get('url')
                    reason = rule.get('reason')
                    
                    headers = MatchService._prepare_headers(reason, headers_from_message)
                    print('Attempting to forward request to ', subscriber_url, headers, proto_pokemon)
                    
                    try:
                        response = await client.post(subscriber_url, json=proto_pokemon, headers=headers)
                        MatchService._handle_notify_response(subscriber_url, response)
                    except httpx.RequestError as e:
                        print('Error sending notification: ', str(e))
                        
            except httpx.RequestError as e:
                print('Error sending notification: ', str(e))
 
    
    @staticmethod
    def _handle_notify_response(subscriber_url: str, response: httpx.Response) -> None:
        print('_handle_notify_response ', subscriber_url)
        if response.status_code == 200:
            print('Notification sent successfully to ', subscriber_url)
        else:
            print('Failed to send notification to ', subscriber_url, response.status_code, response.text)

    @staticmethod
    def _convert_pokemon_info_to_json(pokemon_info: Dict[str, Any]) -> str:
        print('_convert_pokemon_info_to_json ', pokemon_info)
        return json.dumps(pokemon_info)

    @staticmethod
    def _prepare_headers(reason: str, additional_headers: Dict[str, str]) -> Dict[str, str]:
        print('_prepare_headers ', reason, additional_headers)
        headers = {
            "Content-Type": "application/json",
            "X-Grd-Reason": reason
        }
        headers.update(additional_headers)
        return headers

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