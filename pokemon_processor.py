import base64
import json
import pokedex_pb2
from typing import Dict, Any
from google.protobuf.message import DecodeError

class PokemonProcessor:
    @staticmethod
    def process_pokemon(data: str) -> Dict[str, Any]:
        try:
            pokemon = json.loads(data)
            if isinstance(pokemon.get('legendary'), str):
                if pokemon['legendary'].lower() == 'false':
                    pokemon['legendary'] = False
                elif pokemon['legendary'].lower() == 'true':
                    pokemon['legendary'] = True
            return pokemon
        except json.JSONDecodeError as e:
            return {"error": str(e)}

    @staticmethod
    def decode_protobuf_bytes_to_json(protobuf_data: bytes) -> str:
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
        


