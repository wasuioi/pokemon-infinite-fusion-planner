# Defensive Coverage `--defense` Flag Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `--defense` flag to the CLI that shows which attacking types hit the team's fusions super effectively, split into partial (hits at least one) and universal (hits everyone).

**Architecture:** Invert the existing `TYPE_CHART` into a module-level `WEAK_TO` dict, add a pure `calc_weaknesses()` function, then wire a `--defense` flag in `main()` that calls it and prints the results.

**Tech Stack:** Python 3.8+, standard library only.

## Global Constraints

- Python 3.8+, no external dependencies
- Only `fusion.py` and `tests/test_fusion.py` are modified — no new files
- `--defense` is an optional flag; without it the tool behaves exactly as before
- `WEAK_TO` is derived from `TYPE_CHART` at module level (not hardcoded)
- `calc_weaknesses` returns `(partial: set[str], universal: set[str])`

---

## File Map

| File | Change |
|---|---|
| `fusion.py` | Add `WEAK_TO` dict, `calc_weaknesses()`, `--defense` flag in `main()` |
| `tests/test_fusion.py` | Add unit tests for `calc_weaknesses()` and one CLI integration test |

---

### Task 1: `WEAK_TO` dict + `calc_weaknesses()`

**Files:**
- Modify: `fusion.py` (after `ALL_TYPES` on line 224, before `main()`)
- Modify: `tests/test_fusion.py` (append new tests)

**Interfaces:**
- Consumes: `TYPE_CHART: dict[str, list[str]]` (already in fusion.py)
- Produces:
  - `WEAK_TO: dict[str, list[str]]` — module-level dict, defending type → list of attacking types that hit it 2x
  - `calc_weaknesses(team_types: list[list[str]]) -> tuple[set[str], set[str]]` — returns `(partial, universal)`

---

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_fusion.py`:

```python
from fusion import calc_weaknesses, WEAK_TO

def test_weak_to_fire_includes_water():
    assert "Water" in WEAK_TO["Fire"]

def test_weak_to_covers_all_types_in_pokemon():
    from fusion import POKEMON
    all_pokemon_types = {t for types in POKEMON.values() for t in types}
    for t in all_pokemon_types:
        assert t in WEAK_TO, f"{t} missing from WEAK_TO"

def test_single_member_partial_equals_universal():
    # One-member team: partial and universal are the same set
    partial, universal = calc_weaknesses([["Fire"]])
    assert partial == universal
    assert "Water" in partial
    assert "Rock" in partial
    assert "Ground" in partial

def test_two_members_partial_is_union():
    # Fire weak to Water/Rock/Ground; Water weak to Electric/Grass
    partial, universal = calc_weaknesses([["Fire"], ["Water"]])
    assert "Water" in partial    # hits Fire
    assert "Electric" in partial  # hits Water
    assert "Grass" in partial     # hits Water

def test_two_members_universal_is_intersection():
    # Fire weak to Water/Rock/Ground; Electric weak to Ground
    partial, universal = calc_weaknesses([["Fire"], ["Electric"]])
    assert "Ground" in universal   # hits both Fire and Electric
    assert "Water" not in universal  # hits Fire but not Electric

def test_empty_team_returns_empty_sets():
    partial, universal = calc_weaknesses([])
    assert partial == set()
    assert universal == set()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py::test_weak_to_fire_includes_water -v
```

Expected: `ImportError: cannot import name 'calc_weaknesses'`

- [ ] **Step 3: Add `WEAK_TO` and `calc_weaknesses()` to `fusion.py`**

Insert after line 224 (`ALL_TYPES = ...`), before `def main()`:

```python
WEAK_TO = {}
for _attacker, _defenders in TYPE_CHART.items():
    for _defender in _defenders:
        WEAK_TO.setdefault(_defender, []).append(_attacker)


def calc_weaknesses(team_types):
    if not team_types:
        return set(), set()
    sets = []
    for types in team_types:
        member_weak = set()
        for t in types:
            member_weak.update(WEAK_TO.get(t, []))
        sets.append(member_weak)
    partial = set.union(*sets)
    universal = set.intersection(*sets)
    return partial, universal
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py -v
```

Expected: All 26 tests PASS (20 existing + 6 new).

- [ ] **Step 5: Commit**

```bash
cd /Users/pacas/pokemon && git add fusion.py tests/test_fusion.py && git commit -m "feat: add WEAK_TO dict and calc_weaknesses"
```

---

### Task 2: `--defense` flag in `main()`

**Files:**
- Modify: `fusion.py` — `main()` function
- Modify: `tests/test_fusion.py` — append one CLI integration test

**Interfaces:**
- Consumes: `calc_weaknesses(team_types: list[list[str]]) -> tuple[set[str], set[str]]` from Task 1
- Produces: `--defense` optional flag; when set, prints "Defensive Weaknesses:" block after normal output

---

- [ ] **Step 1: Write the failing test**

Append to `tests/test_fusion.py`:

```python
def test_cli_defense_flag_shows_weaknesses():
    result = subprocess.run(
        ["python", "fusion.py", "--defense", "Charizard/Blastoise"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    assert result.returncode == 0
    assert "Defensive Weaknesses" in result.stdout
    assert "Partial" in result.stdout
    assert "Universal" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py::test_cli_defense_flag_shows_weaknesses -v
```

Expected: FAIL — `error: unrecognized arguments: --defense`

- [ ] **Step 3: Add `--defense` flag to `main()` in `fusion.py`**

Replace the `main()` function (lines 227–267) with:

```python
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Pokémon Infinite Fusion — team type coverage checker"
    )
    parser.add_argument(
        "team", nargs="+",
        help="Fusions as Head/Body (e.g. Charizard/Blastoise) or solo name"
    )
    parser.add_argument(
        "--defense", action="store_true",
        help="Also show defensive weaknesses"
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

    if args.defense:
        partial, universal = calc_weaknesses(team_types)
        print("\nDefensive Weaknesses:")
        print(f"  Partial (hits at least 1):  {', '.join(sorted(partial)) or 'None'}")
        print(f"  Universal (hits everyone):  {', '.join(sorted(universal)) or 'None'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
cd /Users/pacas/pokemon && python -m pytest tests/test_fusion.py -v
```

Expected: All 27 tests PASS.

- [ ] **Step 5: Smoke test manually**

```bash
cd /Users/pacas/pokemon && python fusion.py --defense Charizard/Blastoise Jolteon/Slowbro Machamp/Gengar
```

Expected output includes:
```
Defensive Weaknesses:
  Partial (hits at least 1):  ...
  Universal (hits everyone):  ...
```

- [ ] **Step 6: Commit**

```bash
cd /Users/pacas/pokemon && git add fusion.py tests/test_fusion.py && git commit -m "feat: add --defense flag to show team weaknesses"
```
