import base64
import json
import pokedex_pb2
from typing import Dict, Any
from google.protobuf.message import DecodeError

class PokemonProcessor:
    @staticmethod
    def process_pokemon(data: str) -> Dict[str, Any]:
        print('process_pokemon ', data)
        try:
            pokemon = json.loads(data)
            processed_pokemon = PokemonProcessor._convert_to_boolean(pokemon)
            return processed_pokemon
        except json.JSONDecodeError as e:
            return {"error": str(e)}


    @staticmethod
    def decode_protobuf_bytes_to_json(protobuf_data: bytes) -> str:
        print('decode_protobuf_bytes_to_json ', protobuf_data)
        pokemon = pokedex_pb2.Pokemon()
        pokemon.ParseFromString(protobuf_data)
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
        return json.dumps(pokemon_dict, indent=2)

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