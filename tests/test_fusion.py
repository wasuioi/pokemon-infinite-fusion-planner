import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fusion import get_fusion_types, POKEMON, TYPE_CHART

def test_pokemon_dict_has_151_entries():
    assert len(POKEMON) == 151

def test_all_types_are_valid():
    valid = set(TYPE_CHART.keys())
    for name, types in POKEMON.items():
        for t in types:
            assert t in valid, f"{name} has unknown type {t}"

def test_solo_pokemon_returns_own_types():
    assert get_fusion_types("Charizard") == ["Fire", "Flying"]
    assert get_fusion_types("Pikachu") == ["Electric"]

def test_fusion_head_gives_type1():
    # Charizard (Fire/Flying) + Blastoise (Water) → Fire + Water
    assert get_fusion_types("Charizard", "Blastoise") == ["Fire", "Water"]

def test_fusion_uses_body_type1_if_different():
    # Bulbasaur (Grass/Poison) + Charmander (Fire) → Grass + Fire
    assert get_fusion_types("Bulbasaur", "Charmander") == ["Grass", "Fire"]

def test_fusion_skips_duplicate_type():
    # Pikachu (Electric) + Raichu (Electric) → only Electric
    assert get_fusion_types("Pikachu", "Raichu") == ["Electric"]

def test_fusion_falls_back_to_body_type2_when_type1_matches():
    # Gastly (Ghost/Poison) + Gastly (Ghost/Poison)
    # Head type1=Ghost. Body type1=Ghost (same), Body type2=Poison → Ghost + Poison
    assert get_fusion_types("Gastly", "Gastly") == ["Ghost", "Poison"]

def test_fusion_single_type_body_same_as_head_gives_one_type():
    # Charmander (Fire) + Vulpix (Fire) → only Fire (body has no type2)
    assert get_fusion_types("Charmander", "Vulpix") == ["Fire"]
