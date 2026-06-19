import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fusion import get_fusion_types, POKEMON, TYPE_CHART, calc_coverage

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

def test_single_type_covers_correct_types():
    result = calc_coverage([["Fire"]])
    assert result == {"Grass", "Ice", "Bug", "Steel"}

def test_two_types_union_coverage():
    result = calc_coverage([["Fire"], ["Water"]])
    assert "Grass" in result   # from Fire
    assert "Ground" in result  # from Water
    assert "Rock" in result    # from Water

def test_dual_type_pokemon_covers_both():
    result = calc_coverage([["Electric", "Flying"]])
    assert "Water" in result    # Electric hits Water
    assert "Fighting" in result # Flying hits Fighting

def test_empty_team_covers_nothing():
    assert calc_coverage([]) == set()

def test_normal_type_covers_nothing():
    assert calc_coverage([["Normal"]]) == set()

from fusion import suggest_fusions

def test_suggest_returns_at_most_top_n():
    results = suggest_fusions(["Fire", "Water", "Grass"], top_n=3)
    assert len(results) <= 3

def test_suggest_each_result_is_tuple_of_four():
    results = suggest_fusions(["Electric"])
    assert len(results) >= 1
    head, body, types, gain = results[0]
    assert isinstance(head, str)
    assert isinstance(body, str)
    assert isinstance(types, list)
    assert isinstance(gain, list)

def test_suggest_covers_missing_type():
    results = suggest_fusions(["Electric"])
    all_gains = [g for _, _, _, g in results]
    assert any("Electric" in g for g in all_gains)

def test_suggest_no_duplicate_pairs():
    results = suggest_fusions(["Fire", "Water", "Electric"], top_n=10)
    pairs = [tuple(sorted([h, b])) for h, b, _, _ in results]
    assert len(pairs) == len(set(pairs))

import subprocess

def test_cli_runs_and_prints_coverage():
    result = subprocess.run(
        ["python3", "fusion.py", "Charizard/Blastoise"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    assert result.returncode == 0
    assert "Team Coverage" in result.stdout
    assert "Missing" in result.stdout

def test_cli_unfused_pokemon():
    result = subprocess.run(
        ["python3", "fusion.py", "Pikachu"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    assert result.returncode == 0
    assert "Electric" in result.stdout

def test_cli_shows_suggestions_when_missing():
    result = subprocess.run(
        ["python3", "fusion.py", "Snorlax"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    assert result.returncode == 0
    assert "suggestions" in result.stdout.lower()
