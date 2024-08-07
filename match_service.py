from typing import Dict, Any, List
from config import Config
import re
import operator
import httpx
import json

class MatchService:
    @staticmethod    
    def match_check(data):
        print('match_check', data)

        pokemon = data.get('pokemon_data', {})
        rules = Config.load_rules_config()["rules"]
        matching_rules = []
        
        for rule in rules:
            match = rule['match']
            all_conditions_met = True
            
            for condition in match:
                condition = condition.strip()
                print(f"Checking condition: {condition}") 
                
                if '==' in condition:
                    key, value = condition.split('==')
                    key = key.strip()
                    value = value.strip()
                    if value.isnumeric():
                        value = int(value)
                    print(f"Comparing {key}: pokemon.get({key}) = {pokemon.get(key)}, value = {value}")
                    if pokemon.get(key) != value:
                        print(f"Condition failed: {key} == {value} (pokemon.get({key}) = {pokemon.get(key)})")
                        all_conditions_met = False
                        break
                
                elif '!=' in condition:
                    key, value = condition.split('!=')
                    key = key.strip()
                    value = value.strip().strip("'") 
                    if value.isnumeric():
                        value = int(value)
                    print(f"Comparing {key}: pokemon.get({key}) = {pokemon.get(key)}, value = {value}")
                    if pokemon.get(key) == value:
                        print(f"Condition failed: {key} != {value} (pokemon.get({key}) = {pokemon.get(key)})")
                        all_conditions_met = False
                        break
                
                elif '>' in condition:
                    key, value = condition.split('>')
                    key = key.strip()
                    value = value.strip()
                    if value.isnumeric():
                        value = int(value)
                    print(f"Comparing {key}: pokemon.get({key}) = {pokemon.get(key)}, value = {value}")
                    if pokemon.get(key) <= value:
                        print(f"Condition failed: {key} > {value} (pokemon.get({key}) = {pokemon.get(key)})")
                        all_conditions_met = False
                        break
                
                elif '<' in condition:
                    key, value = condition.split('<')
                    key = key.strip()
                    value = value.strip()
                    if value.isnumeric():
                        value = int(value)
                    print(f"Comparing {key}: pokemon.get({key}) = {pokemon.get(key)}, value = {value}")
                    if pokemon.get(key) >= value:
                        print(f"Condition failed: {key} < {value} (pokemon.get({key}) = {pokemon.get(key)})")
                        all_conditions_met = False
                        break
            
            if all_conditions_met:
                matching_rules.append(rule)
        return matching_rules

    @staticmethod    
    def process_matches(data: dict):
        print('process_matches ', data)

        matched_rules = MatchService.match_check(data)
        if matched_rules:
            MatchService.notify_subscribers(data, matched_rules)
                
    def notify_subscribers(pokemon_message: dict, matched_rules: list):
        print('notify_subscribers', pokemon_message, matched_rules)
        
        pokemon_info = pokemon_message.get('pokemon_data', {})
        headers_from_message = pokemon_message.get('headers', {})
        converted_pokemnon_dict_to_proto = json.dumps(pokemon_info)

        print('notify_subscribers pokemon_info ', converted_pokemnon_dict_to_proto)
        print('notify_subscribers headers_from_message ', headers_from_message)
        
        try:
            with httpx.AsyncClient() as client:
                for rule in matched_rules:
                    subscriber_url = rule.get('url')
                    reason = rule.get('reason')
                    
                    payload = converted_pokemnon_dict_to_proto
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