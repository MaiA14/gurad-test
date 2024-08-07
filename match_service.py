from typing import Dict, Any, List
from config import Config
import re
import operator

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

                
    @staticmethod
    def notify_subscribers(pokemon_message: dict, matched_rules: list):
        print('notify_subscribers ', pokemon_message, matched_rules)
        pokemon_data = pokemon_message.get("pokemon_data", {})
        headers_from_message = pokemon_message.get("headers", {})
        
        for rule in matched_rules:
            subscriber_url = rule['url']
            reason = rule['reason']
            payload = {
                "pokemon_data": pokemon_data
            }
            headers = {
                "Content-Type": "application/json",
                "X-Grd-Reason": reason
            }
            headers.update(headers_from_message)
            
            try:
                print('try forward req ', headers, payload)
                response = requests.post(subscriber_url, json=payload, headers=headers)
                if response.status_code == 200:
                    print(f"Notification sent successfully to {subscriber_url}")
                else:
                    print(f"Failed to send notification to {subscriber_url}. Status code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Error sending notification to {subscriber_url}: {e}")