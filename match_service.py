from typing import Dict, Any, List
from config import Config
import re
import operator
import httpx

class MatchService:
    @staticmethod    
    def match_check(pokemon):
        print('match_check', pokemon)
        rules = Config.load_rules_config()["rules"]
        print('rules from match_check ', rules)
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
        
        print('matching_rules ', matching_rules)
        return matching_rules

    @staticmethod    
    def process_matches(data: dict):
        print('process_matches ', data)
        pokemon_data = data.get("pokemon_data", {})
        matched_rules = MatchService.match_check(pokemon_data)
        print('Matched rules:', matched_rules)
        if matched_rules:
            print('got matched_rules ', matched_rules)
            MatchService.notify_subscribers(pokemon_data, matched_rules)
        else:
            print("No rules matched. No notification sent.")

                
    def notify_subscribers(pokemon_message: dict, matched_rules: list):
        print('notify_subscribers', pokemon_message, matched_rules)
        
        pokemon_data = pokemon_message.get("pokemon_data", {})
        headers_from_message = pokemon_message.get("headers", {})

        print('notify_subscribers pokemon_data ', pokemon_data)
        print('notify_subscribers headers_from_message ', headers_from_message)
        
        try:
            with httpx.AsyncClient() as client:
                for rule in matched_rules:
                    subscriber_url = rule.get('url')
                    reason = rule.get('reason')
                    
                    payload = pokemon_data
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