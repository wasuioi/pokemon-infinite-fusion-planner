# Pokémon Infinite Fusion — Team Planner CLI

## Overview

A single-file Python CLI tool that takes a team of fusions as input, calculates type coverage, and suggests fusions to fill gaps.

## Usage

```
python fusion.py Charizard/Blastoise Jolteon/Slowbro Machamp/Gengar
```

- Each argument is a fusion in `Head/Body` format
- If no `/` is given, the Pokemon is treated as un-fused (uses its own types)
- Supports 1–6 team members

### Example Output

```
Team Coverage:
  ✓ Fire    ✓ Water   ✓ Electric ✓ Ghost
  ✓ Fighting ✗ Grass  ✗ Psychic  ✗ Ground ...

Missing: Grass, Psychic, Ground, Rock, Ice

Top suggestions to fill gaps:
  Exeggutor/Alakazam  → Grass + Psychic
  Golem/Sandslash     → Rock + Ground
```

## Fusion Type Formula

Matches the in-game mechanic:

1. Type 1 of fusion = Type 1 of Head
2. Type 2 of fusion = Type 1 of Body (if different from Type 1)
3. If same = Type 2 of Body (if it exists)

## Data

- `POKEMON` dict: types for all 151 Gen 1 Pokemon, hardcoded in the script
- `TYPE_CHART` dict: standard 18-type effectiveness table

## Coverage Calculation

A team "covers" a type if at least one fusion can hit it super effectively (2× or 4×). Coverage is calculated from offensive moves, not defensive resistances.

## Suggestions

Loop over all possible Head/Body combinations from the 151-Pokemon pool. Score each by how many missing types it covers. Return top 3 results.

## File Structure

```
pokemon/
├── fusion.py   # all logic: data, calculation, output
```

No external dependencies — uses only Python standard library (`sys`, `argparse`).

## Out of Scope (for now)

- Defensive coverage / weaknesses
- Moves or stats
- Pokemon beyond Gen 1
- GUI or web interface
