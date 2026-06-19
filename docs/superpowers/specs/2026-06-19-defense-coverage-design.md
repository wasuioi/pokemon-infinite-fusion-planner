# Defensive Coverage — `--defense` Flag

## Overview

Add a `--defense` flag to the existing CLI that shows what attacking types the team is weak to.

## Usage

```
python fusion.py --defense Charizard/Blastoise Jolteon/Slowbro Machamp/Gengar
```

### Example Output

```
Defensive Weaknesses:
  Partial (hits at least 1):  Electric, Ground, Ice, Psychic, Rock, Water
  Universal (hits everyone):  Rock
```

- **Partial** — union of all members' weaknesses: types that hit at least one team member super effectively
- **Universal** — intersection of all members' weaknesses: types that hit every team member (most dangerous)

Without `--defense`, the tool behaves exactly as before.

## Logic

### WEAK_TO dict

Invert `TYPE_CHART` at module level to get "what attacking types hit each defending type 2x":

```python
WEAK_TO = {}
for attacker, defenders in TYPE_CHART.items():
    for defender in defenders:
        WEAK_TO.setdefault(defender, []).append(attacker)
```

### `calc_weaknesses(team_types)`

```python
def calc_weaknesses(team_types):
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

Returns `(partial: set[str], universal: set[str])`.

## File Structure

Only `fusion.py` is modified:
- Add `WEAK_TO` dict (module-level, derived from `TYPE_CHART`)
- Add `calc_weaknesses()` function
- Add `--defense` flag to `main()` argparse
- Add display block in `main()` for defense output

## Out of Scope

- Exact multipliers (4x, 0.5x, 0x immunities)
- Resistance/immunity cancellation between dual types
- Suggestions for fixing weaknesses
