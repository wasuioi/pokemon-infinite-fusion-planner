# Fusion Team Planner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single Python CLI script that takes a team of Pokémon Infinite Fusion fusions, shows type coverage, and suggests fusions to fill gaps.

**Architecture:** All logic lives in one file (`fusion.py`). Data (POKEMON dict, TYPE_CHART) is hardcoded at the top. Four pure functions do the work. `main()` wires argparse to the functions and prints results.

**Tech Stack:** Python 3, standard library only (`argparse`, `sys`). Tests use `pytest`.

## Global Constraints

- Python 3.8+
- No external dependencies (no `pip install` needed)
- All 151 Gen 1 Pokémon, using Gen 3 types (e.g. Magnemite is Electric/Steel)
- Special-character names use ASCII keys: `NidoranF`, `NidoranM`, `Farfetchd`, `MrMime`
- Coverage = offensive STAB only (what types can the team hit super effectively)
- Top 3 suggestions, no duplicates (A/B and B/A count as the same fusion)

---

## File Map

| File | Role |
|---|---|
| `fusion.py` | All data + all logic + CLI entry point |
| `tests/test_fusion.py` | pytest tests for all functions |

---

### Task 1: Data layer + `get_fusion_types()`

**Files:**
- Create: `fusion.py`
- Create: `tests/test_fusion.py`

**Interfaces:**
- Produces: `POKEMON: dict[str, list[str]]`, `TYPE_CHART: dict[str, list[str]]`
- Produces: `get_fusion_types(head: str, body: str | None) -> list[str]`

---

- [ ] **Step 1: Write the failing tests**

Create `tests/test_fusion.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py -v
```

Expected: `ModuleNotFoundError: No module named 'fusion'`

- [ ] **Step 3: Create `fusion.py` with POKEMON + TYPE_CHART + `get_fusion_types()`**

```python
POKEMON = {
    "Bulbasaur":   ["Grass", "Poison"],
    "Ivysaur":     ["Grass", "Poison"],
    "Venusaur":    ["Grass", "Poison"],
    "Charmander":  ["Fire"],
    "Charmeleon":  ["Fire"],
    "Charizard":   ["Fire", "Flying"],
    "Squirtle":    ["Water"],
    "Wartortle":   ["Water"],
    "Blastoise":   ["Water"],
    "Caterpie":    ["Bug"],
    "Metapod":     ["Bug"],
    "Butterfree":  ["Bug", "Flying"],
    "Weedle":      ["Bug", "Poison"],
    "Kakuna":      ["Bug", "Poison"],
    "Beedrill":    ["Bug", "Poison"],
    "Pidgey":      ["Normal", "Flying"],
    "Pidgeotto":   ["Normal", "Flying"],
    "Pidgeot":     ["Normal", "Flying"],
    "Rattata":     ["Normal"],
    "Raticate":    ["Normal"],
    "Spearow":     ["Normal", "Flying"],
    "Fearow":      ["Normal", "Flying"],
    "Ekans":       ["Poison"],
    "Arbok":       ["Poison"],
    "Pikachu":     ["Electric"],
    "Raichu":      ["Electric"],
    "Sandshrew":   ["Ground"],
    "Sandslash":   ["Ground"],
    "NidoranF":    ["Poison"],
    "Nidorina":    ["Poison"],
    "Nidoqueen":   ["Poison", "Ground"],
    "NidoranM":    ["Poison"],
    "Nidorino":    ["Poison"],
    "Nidoking":    ["Poison", "Ground"],
    "Clefairy":    ["Normal"],
    "Clefable":    ["Normal"],
    "Vulpix":      ["Fire"],
    "Ninetales":   ["Fire"],
    "Jigglypuff":  ["Normal"],
    "Wigglytuff":  ["Normal"],
    "Zubat":       ["Poison", "Flying"],
    "Golbat":      ["Poison", "Flying"],
    "Oddish":      ["Grass", "Poison"],
    "Gloom":       ["Grass", "Poison"],
    "Vileplume":   ["Grass", "Poison"],
    "Paras":       ["Bug", "Grass"],
    "Parasect":    ["Bug", "Grass"],
    "Venonat":     ["Bug", "Poison"],
    "Venomoth":    ["Bug", "Poison"],
    "Diglett":     ["Ground"],
    "Dugtrio":     ["Ground"],
    "Meowth":      ["Normal"],
    "Persian":     ["Normal"],
    "Psyduck":     ["Water"],
    "Golduck":     ["Water"],
    "Mankey":      ["Fighting"],
    "Primeape":    ["Fighting"],
    "Growlithe":   ["Fire"],
    "Arcanine":    ["Fire"],
    "Poliwag":     ["Water"],
    "Poliwhirl":   ["Water"],
    "Poliwrath":   ["Water", "Fighting"],
    "Abra":        ["Psychic"],
    "Kadabra":     ["Psychic"],
    "Alakazam":    ["Psychic"],
    "Machop":      ["Fighting"],
    "Machoke":     ["Fighting"],
    "Machamp":     ["Fighting"],
    "Bellsprout":  ["Grass", "Poison"],
    "Weepinbell":  ["Grass", "Poison"],
    "Victreebel":  ["Grass", "Poison"],
    "Tentacool":   ["Water", "Poison"],
    "Tentacruel":  ["Water", "Poison"],
    "Geodude":     ["Rock", "Ground"],
    "Graveler":    ["Rock", "Ground"],
    "Golem":       ["Rock", "Ground"],
    "Ponyta":      ["Fire"],
    "Rapidash":    ["Fire"],
    "Slowpoke":    ["Water", "Psychic"],
    "Slowbro":     ["Water", "Psychic"],
    "Magnemite":   ["Electric", "Steel"],
    "Magneton":    ["Electric", "Steel"],
    "Farfetchd":   ["Normal", "Flying"],
    "Doduo":       ["Normal", "Flying"],
    "Dodrio":      ["Normal", "Flying"],
    "Seel":        ["Water"],
    "Dewgong":     ["Water", "Ice"],
    "Grimer":      ["Poison"],
    "Muk":         ["Poison"],
    "Shellder":    ["Water"],
    "Cloyster":    ["Water", "Ice"],
    "Gastly":      ["Ghost", "Poison"],
    "Haunter":     ["Ghost", "Poison"],
    "Gengar":      ["Ghost", "Poison"],
    "Onix":        ["Rock", "Ground"],
    "Drowzee":     ["Psychic"],
    "Hypno":       ["Psychic"],
    "Krabby":      ["Water"],
    "Kingler":     ["Water"],
    "Voltorb":     ["Electric"],
    "Electrode":   ["Electric"],
    "Exeggcute":   ["Grass", "Psychic"],
    "Exeggutor":   ["Grass", "Psychic"],
    "Cubone":      ["Ground"],
    "Marowak":     ["Ground"],
    "Hitmonlee":   ["Fighting"],
    "Hitmonchan":  ["Fighting"],
    "Lickitung":   ["Normal"],
    "Koffing":     ["Poison"],
    "Weezing":     ["Poison"],
    "Rhyhorn":     ["Ground", "Rock"],
    "Rhydon":      ["Ground", "Rock"],
    "Chansey":     ["Normal"],
    "Tangela":     ["Grass"],
    "Kangaskhan":  ["Normal"],
    "Horsea":      ["Water"],
    "Seadra":      ["Water"],
    "Goldeen":     ["Water"],
    "Seaking":     ["Water"],
    "Staryu":      ["Water"],
    "Starmie":     ["Water", "Psychic"],
    "MrMime":      ["Psychic"],
    "Scyther":     ["Bug", "Flying"],
    "Jynx":        ["Ice", "Psychic"],
    "Electabuzz":  ["Electric"],
    "Magmar":      ["Fire"],
    "Pinsir":      ["Bug"],
    "Tauros":      ["Normal"],
    "Magikarp":    ["Water"],
    "Gyarados":    ["Water", "Flying"],
    "Lapras":      ["Water", "Ice"],
    "Ditto":       ["Normal"],
    "Eevee":       ["Normal"],
    "Vaporeon":    ["Water"],
    "Jolteon":     ["Electric"],
    "Flareon":     ["Fire"],
    "Porygon":     ["Normal"],
    "Omanyte":     ["Rock", "Water"],
    "Omastar":     ["Rock", "Water"],
    "Kabuto":      ["Rock", "Water"],
    "Kabutops":    ["Rock", "Water"],
    "Aerodactyl":  ["Rock", "Flying"],
    "Snorlax":     ["Normal"],
    "Articuno":    ["Ice", "Flying"],
    "Zapdos":      ["Electric", "Flying"],
    "Moltres":     ["Fire", "Flying"],
    "Dratini":     ["Dragon"],
    "Dragonair":   ["Dragon"],
    "Dragonite":   ["Dragon", "Flying"],
    "Mewtwo":      ["Psychic"],
    "Mew":         ["Psychic"],
}

TYPE_CHART = {
    "Normal":   [],
    "Fire":     ["Grass", "Ice", "Bug", "Steel"],
    "Water":    ["Fire", "Ground", "Rock"],
    "Electric": ["Water", "Flying"],
    "Grass":    ["Water", "Ground", "Rock"],
    "Ice":      ["Grass", "Ground", "Flying", "Dragon"],
    "Fighting": ["Normal", "Ice", "Rock", "Dark", "Steel"],
    "Poison":   ["Grass", "Fairy"],
    "Ground":   ["Fire", "Electric", "Poison", "Rock", "Steel"],
    "Flying":   ["Grass", "Fighting", "Bug"],
    "Psychic":  ["Fighting", "Poison"],
    "Bug":      ["Grass", "Psychic", "Dark"],
    "Rock":     ["Fire", "Ice", "Flying", "Bug"],
    "Ghost":    ["Ghost", "Psychic"],
    "Dragon":   ["Dragon"],
    "Dark":     ["Ghost", "Psychic"],
    "Steel":    ["Ice", "Rock", "Fairy"],
    "Fairy":    ["Fighting", "Dragon", "Dark"],
}


def get_fusion_types(head, body=None):
    if body is None:
        return POKEMON[head][:]
    head_types = POKEMON[head]
    body_types = POKEMON[body]
    type1 = head_types[0]
    type2 = None
    for t in body_types:
        if t != type1:
            type2 = t
            break
    return [type1, type2] if type2 else [type1]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/pacas/pokemon && git add fusion.py tests/test_fusion.py && git commit -m "feat: add Pokemon data, type chart, and get_fusion_types"
```

---

### Task 2: `calc_coverage()`

**Files:**
- Modify: `fusion.py`
- Modify: `tests/test_fusion.py`

**Interfaces:**
- Consumes: `TYPE_CHART: dict[str, list[str]]`
- Produces: `calc_coverage(team_types: list[list[str]]) -> set[str]`

---

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_fusion.py`:

```python
from fusion import calc_coverage

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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py::test_single_type_covers_correct_types -v
```

Expected: `ImportError: cannot import name 'calc_coverage'`

- [ ] **Step 3: Add `calc_coverage()` to `fusion.py`**

Add after `get_fusion_types()`:

```python
def calc_coverage(team_types):
    covered = set()
    for types in team_types:
        for t in types:
            covered.update(TYPE_CHART.get(t, []))
    return covered
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py -v
```

Expected: All 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/pacas/pokemon && git add fusion.py tests/test_fusion.py && git commit -m "feat: add calc_coverage"
```

---

### Task 3: `suggest_fusions()`

**Files:**
- Modify: `fusion.py`
- Modify: `tests/test_fusion.py`

**Interfaces:**
- Consumes: `get_fusion_types(head, body)`, `TYPE_CHART`
- Produces: `suggest_fusions(missing: list[str], top_n: int = 3) -> list[tuple[str, str, list[str], list[str]]]`
  - Each tuple: `(head_name, body_name, fusion_types, missing_types_covered)`

---

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_fusion.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py::test_suggest_returns_at_most_top_n -v
```

Expected: `ImportError: cannot import name 'suggest_fusions'`

- [ ] **Step 3: Add `suggest_fusions()` to `fusion.py`**

Add after `calc_coverage()`:

```python
def suggest_fusions(missing, top_n=3):
    missing_set = set(missing)
    scores = []
    names = list(POKEMON.keys())
    for head in names:
        for body in names:
            types = get_fusion_types(head, body)
            covered = set()
            for t in types:
                covered.update(TYPE_CHART.get(t, []))
            gain = sorted(covered & missing_set)
            if gain:
                scores.append((len(gain), head, body, types, gain))
    scores.sort(key=lambda x: -x[0])
    seen = set()
    results = []
    for _, head, body, types, gain in scores:
        key = tuple(sorted([head, body]))
        if key not in seen:
            seen.add(key)
            results.append((head, body, types, gain))
        if len(results) >= top_n:
            break
    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py -v
```

Expected: All 17 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/pacas/pokemon && git add fusion.py tests/test_fusion.py && git commit -m "feat: add suggest_fusions"
```

---

### Task 4: `main()` CLI entry point

**Files:**
- Modify: `fusion.py`

**Interfaces:**
- Consumes: `get_fusion_types()`, `calc_coverage()`, `suggest_fusions()`, `POKEMON`, `TYPE_CHART`
- Produces: CLI command `python fusion.py Head/Body ...`

---

- [ ] **Step 1: Write the failing test**

Append to `tests/test_fusion.py`:

```python
import subprocess

def test_cli_runs_and_prints_coverage():
    result = subprocess.run(
        ["python", "fusion.py", "Charizard/Blastoise"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    assert result.returncode == 0
    assert "Team Coverage" in result.stdout
    assert "Missing" in result.stdout

def test_cli_unfused_pokemon():
    result = subprocess.run(
        ["python", "fusion.py", "Pikachu"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    assert result.returncode == 0
    assert "Electric" in result.stdout

def test_cli_shows_suggestions_when_missing():
    result = subprocess.run(
        ["python", "fusion.py", "Snorlax"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    assert result.returncode == 0
    assert "suggestions" in result.stdout.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py::test_cli_runs_and_prints_coverage -v
```

Expected: FAIL — `fusion.py` has no `main()` and no `if __name__ == "__main__"` block.

- [ ] **Step 3: Add `main()` and entry point to `fusion.py`**

Add at the bottom of `fusion.py`:

```python
ALL_TYPES = sorted({t for types in POKEMON.values() for t in types})


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Pokémon Infinite Fusion — team type coverage checker"
    )
    parser.add_argument(
        "team", nargs="+",
        help="Fusions as Head/Body (e.g. Charizard/Blastoise) or solo name"
    )
    args = parser.parse_args()

    team_types = []
    for entry in args.team:
        if "/" in entry:
            head, body = entry.split("/", 1)
            types = get_fusion_types(head, body)
        else:
            types = get_fusion_types(entry)
        team_types.append(types)

    covered = calc_coverage(team_types)
    missing = [t for t in ALL_TYPES if t not in covered]

    print("Team Coverage:")
    for t in ALL_TYPES:
        mark = "✓" if t in covered else "✗"
        print(f"  {mark} {t}")

    if missing:
        print(f"\nMissing: {', '.join(missing)}")
        print("\nTop suggestions to fill gaps:")
        for head, body, types, gain in suggest_fusions(missing):
            types_str = " + ".join(types)
            gain_str = ", ".join(gain)
            print(f"  {head}/{body}  →  {types_str}  (covers: {gain_str})")
    else:
        print("\nFull coverage! No gaps.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py -v
```

Expected: All 20 tests PASS.

- [ ] **Step 5: Smoke test manually**

```bash
cd /Users/pacas/pokemon && python fusion.py Charizard/Blastoise Jolteon/Slowbro Machamp/Gengar
```

Expected output similar to:
```
Team Coverage:
  ✓ Bug
  ✓ Electric
  ✓ Fighting
  ✓ Fire
  ✓ Flying
  ✓ Ghost
  ✓ Grass
  ...

Missing: Dragon, Ground, Ice, Rock

Top suggestions to fill gaps:
  Geodude/Lapras  →  Rock + Water  (covers: Dragon, Ground, Ice, Rock)
  ...
```

- [ ] **Step 6: Commit**

```bash
cd /Users/pacas/pokemon && git add fusion.py tests/test_fusion.py && git commit -m "feat: add CLI main() — fusion team planner complete"
```
