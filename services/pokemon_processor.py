import base64
import json
import pokedex_pb2
from typing import Dict, Any
from google.protobuf.message import DecodeError
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PokemonProcessor:
    @staticmethod
    def process_pokemon(data: str) -> Dict[str, Any]:
        logging.info('process_pokemon: %s', data)
        try:
            pokemon = json.loads(data)
            processed_pokemon = PokemonProcessor._convert_to_boolean(pokemon)
            return processed_pokemon
        except json.JSONDecodeError as e:
            logging.error('JSON decode error: %s', str(e))
            return {"error": str(e)}

    @staticmethod
    def decode_protobuf_bytes_to_json(protobuf_data: bytes) -> str:
        logging.info('decode_protobuf_bytes_to_json: %s', protobuf_data)
        pokemon = pokedex_pb2.Pokemon()
        try:
            pokemon.ParseFromString(protobuf_data)
        except DecodeError as e:
            logging.error('Protobuf decode error: %s', str(e))
            return json.dumps({"error": str(e)})
        
        pokemon_dict = {
            "number": pokemon.number,
            "name": pokemon.name,
            "type_one": pokemon.type_one,
            "type_two": pokemon.type_two,
            "total": pokemon.total,
            "hit_points": pokemon.hit_points,
            "attack": pokemon.attack,
            "defense": pokemon.defense,
            "special_attack": pokemon.special_attack,
            "special_defense": pokemon.special_defense,
            "speed": pokemon.speed,
            "generation": pokemon.generation,
            "legendary": pokemon.legendary
        }
        json_result = json.dumps(pokemon_dict, indent=2)
        logging.info('Decoded protobuf data to JSON: %s', json_result)
        return json_result

    @staticmethod
    def _parse_string_to_boolean(value: Any) -> Any:
        if isinstance(value, str):
            value = value.lower()
            if value == 'true':
                return True
            elif value == 'false':
                return False
        return value

    @staticmethod
    def _convert_to_boolean(d: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = PokemonProcessor._convert_to_boolean(value)
            elif isinstance(value, str) and value.lower() in ('true', 'false'):
                d[key] = PokemonProcessor._parse_string_to_boolean(value)
        return d
