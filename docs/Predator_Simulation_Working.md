# 🎬 PREDATOR: BADLANDS - Simulation Working Guide

## Overview

**PREDATOR: BADLANDS** is a multi-agent AI simulation inspired by the Predator movie franchise. It features autonomous agents navigating a hostile environment, engaging in combat, following an honour system, and competing for survival.

---

## 📦 1. INITIALIZATION

### Grid Setup
```
Grid Size: 30x30 cells (toroidal - wraps around edges)

Terrain Types:
├── EMPTY     - Normal movement
├── DESERT    - Slightly slower movement
├── ROCKY     - Movement penalty
├── CANYON    - Cover available
├── HOSTILE   - Damage on entry
├── TRAP      - Damage + movement stop
└── TELEPORT  - Random teleport to another cell
```

### Agent Placement
```
Starting Positions:
┌────────────────────────────────────────┐
│  FATHER (5,5)              BOSS (25,25)│
│       ▲                         ◉      │
│                                        │
│                                        │
│          DEK (10,10)                   │
│          ◆ ● THIA (11,10)              │
│                                        │
│              ▲ BROTHER (15,10)         │
│                                        │
│         ✦ WILDLIFE scattered           │
│                                        │
└────────────────────────────────────────┘
```

### Items Distribution
```
18 items randomly placed:
├── Medkit      - Restores 30 health
├── EnergyPack  - Restores 20 stamina
├── RepairKit   - Restores 15 health (synthetics)
└── WeaponItem  - +5 attack damage
```

---

## 🔄 2. MAIN SIMULATION LOOP

### Turn Structure
```
┌─────────────────────────────────────────────────────────────┐
│                        TURN N                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 1: Weather Transition                                │
│  ─────────────────────────────                              │
│  • 10% chance of weather change each turn                   │
│  • Weather cycles: Calm → Sandstorm → AcidRain → Storm      │
│                                                             │
│  PHASE 2: Agent Actions                                     │
│  ─────────────────────────                                  │
│  For each alive agent (in order):                           │
│    1. DEK        - Main protagonist                         │
│    2. THIA       - Synthetic ally                           │
│    3. FATHER     - Elder Predator                           │
│    4. BROTHER    - Rival Predator                           │
│    5. BOSS       - Ultimate Adversary                       │
│    6. WILDLIFE[] - Wild creatures                           │
│                                                             │
│  PHASE 3: Item Pickup                                       │
│  ─────────────────────                                      │
│  • Auto-collect items on agent's cell                       │
│  • Apply item effects immediately                           │
│                                                             │
│  PHASE 4: Weather Damage                                    │
│  ──────────────────────                                     │
│  • Apply damage to all agents based on current weather      │
│                                                             │
│  PHASE 5: Victory Check                                     │
│  ─────────────────────                                      │
│  • Check win/lose/timeout conditions                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                     TURN N+1                                │
└─────────────────────────────────────────────────────────────┘
```

### Turn Delay
```
Configurable: 50ms (fast) to 1000ms (slow)
Default: 200ms per turn
```

---

## 👽 3. AGENT BEHAVIORS

### DEK (Main Protagonist)
```python
class Dek:
    """
    The main playable character - a young Predator (Yautja)
    seeking to prove himself to his clan.
    """
    
    Attributes:
    ├── health: 100 (max)
    ├── stamina: 100 (max)
    ├── honour: 0 (starting)
    ├── clan_rank: "unblooded"
    ├── trophies: [] (collected from kills)
    └── is_exiled: False
    
    Behavior (step function):
    ┌─────────────────────────────────────────┐
    │ 1. Scan surroundings for threats        │
    │ 2. If enemy in attack range → ATTACK    │
    │ 3. If health < 30% → Seek medkit        │
    │ 4. If stamina < 20% → Rest              │
    │ 5. Else → Move toward BOSS              │
    │ 6. After kill → Collect trophy          │
    └─────────────────────────────────────────┘
    
    Special Abilities:
    ├── Cloaking (thermal camouflage)
    ├── Trophy collection (+honour)
    └── Clan code adherence
```

### THIA (Synthetic Ally)
```python
class Thia:
    """
    A synthetic/android companion who assists Dek.
    Loyal, logical, and supportive.
    """
    
    Attributes:
    ├── health: 80 (max)
    ├── stamina: 100 (max)
    ├── synthetic: True
    └── loyalty: 100
    
    Behavior (step function):
    ┌─────────────────────────────────────────┐
    │ 1. Calculate distance to DEK            │
    │ 2. If DEK health < 50% → Move to heal   │
    │ 3. If distance > 3 → Move closer to DEK │
    │ 4. If enemy threatens DEK → Intercept   │
    │ 5. Scout and report enemy positions     │
    └─────────────────────────────────────────┘
    
    Special Abilities:
    ├── Healing support for DEK
    ├── Enhanced sensors
    └── Repair with RepairKit
```

### PREDATOR FATHER (Elder Kaail)
```python
class PredatorFather:
    """
    Dek's father - an Elder Predator who judges
    Dek's actions and honour.
    """
    
    Attributes:
    ├── health: 150 (max)
    ├── opinion_of_dek: 0 (neutral)
    ├── disappointed_in_dek: False
    └── trial_manager: ClanTrialManager
    
    Behavior (step function):
    ┌─────────────────────────────────────────┐
    │ 1. Observe DEK's actions                │
    │ 2. Judge honour of combat               │
    │ 3. Update opinion (+/- based on action) │
    │ 4. Issue trials if needed               │
    │ 5. Move independently (patrol)          │
    └─────────────────────────────────────────┘
    
    Judgment System:
    ├── opinion > 30  → Approve DEK
    ├── opinion < -30 → Exile DEK
    └── opinion 0     → Neutral observation
    
    Trial Types:
    ├── Combat Trial: Kill X enemies
    ├── Survival Trial: Survive X turns
    └── Hunt Trial: Defeat specific target
```

### PREDATOR BROTHER (Cetanu)
```python
class PredatorBrother:
    """
    Dek's brother - a rival who competes with Dek
    for clan recognition.
    """
    
    Attributes:
    ├── health: 120 (max)
    ├── rivalry_with_dek: 0
    ├── jealous_of_dek: False
    └── protective_of_dek: True (initially)
    
    Behavior (step function):
    ┌─────────────────────────────────────────┐
    │ 1. Monitor DEK's successes              │
    │ 2. If DEK succeeds → rivalry++          │
    │ 3. If rivalry > 20 → Challenge duel     │
    │ 4. Compete for same targets             │
    │ 5. Patrol own territory                 │
    └─────────────────────────────────────────┘
    
    Rivalry Escalation:
    ├── rivalry < 10  → Friendly competition
    ├── rivalry 10-20 → Tense rivalry
    └── rivalry > 20  → Open challenge
```

### WILDLIFE (Beasts)
```python
class WildlifeAgent:
    """
    Hostile creatures that inhabit the badlands.
    Aggressive predators that attack on sight.
    """
    
    Attributes:
    ├── health: 50-80 (varies)
    ├── damage: 10-15
    ├── territory_center: (x, y)
    └── territory_radius: 5
    
    Behavior (step function):
    ┌─────────────────────────────────────────┐
    │ 1. Patrol within territory              │
    │ 2. If intruder detected → Chase         │
    │ 3. If in range → Attack                 │
    │ 4. If health < 20% → Flee               │
    │ 5. Random wander if idle                │
    └─────────────────────────────────────────┘
    
    Types:
    ├── Canyon Beast: High health
    ├── Sand Raptor: Fast movement
    └── Desert Stalker: High damage
```

### BOSS ADVERSARY (Ultimate Adversary)
```python
class BossAdversary:
    """
    The final challenge - a powerful entity
    that guards a specific territory.
    """
    
    Attributes:
    ├── health: 200 (max)
    ├── damage: 25
    ├── territory_center: (25, 25)
    ├── territory_radius: 8
    └── phase: 1 (changes at 50% health)
    
    Behavior (step function):
    ┌─────────────────────────────────────────┐
    │ PHASE 1 (health > 50%):                 │
    │ ├── Guard territory                     │
    │ ├── Attack intruders                    │
    │ └── Normal movement speed               │
    │                                         │
    │ PHASE 2 (health <= 50%):                │
    │ ├── ENRAGED mode activated              │
    │ ├── Damage doubled (50)                 │
    │ ├── Faster movement                     │
    │ └── Actively hunt nearest enemy         │
    └─────────────────────────────────────────┘
    
    Special Abilities:
    ├── Phase transition at 50% HP
    ├── Area denial
    └── High damage output
```

---

## ⚔️ 4. COMBAT SYSTEM

### Attack Mechanics
```
Combat Flow:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ATTACKER                        DEFENDER                   │
│     │                               │                       │
│     │  1. Check range (adjacent)    │                       │
│     │─────────────────────────────>│                        │
│     │                               │                       │
│     │  2. Calculate damage          │                       │
│     │  base_damage + weapon_bonus   │                       │
│     │  + random(0, 5)               │                       │
│     │                               │                       │
│     │  3. Apply damage              │                       │
│     │─────────────────────────────>│                        │
│     │                               │                       │
│     │  4. Check if defeated         │                       │
│     │                               │                       │
│     │  If health <= 0:              │                       │
│     │  ├── is_alive = False         │                       │
│     │  └── Drop trophy (if worthy)  │                       │
│     │                               │                       │
└─────────────────────────────────────────────────────────────┘
```

### Damage Values
```
Agent Base Damage:
├── DEK:      15
├── THIA:     10
├── FATHER:   20
├── BROTHER:  18
├── WILDLIFE: 10-15
└── BOSS:     25 (50 in Phase 2)
```

### Trophy System
```
After defeating an enemy:
┌─────────────────────────────────────┐
│ DEK can collect trophy              │
│                                     │
│ Trophy Value:                       │
│ ├── Wildlife: +5 honour             │
│ ├── Strong enemy: +10 honour        │
│ └── Boss: +50 honour                │
│                                     │
│ Stored in: dek.trophies[]           │
└─────────────────────────────────────┘
```

---

## 🏆 5. HONOUR SYSTEM

### Honourable Actions
```
Action                          Honour Change
─────────────────────────────────────────────
Kill in fair combat             +5
Defeat stronger enemy           +10
Protect Thia                    +3
Complete Father's trial         +15
Collect worthy trophy           +5 to +50
Spare wounded enemy             +2
```

### Dishonourable Actions
```
Action                          Honour Change
─────────────────────────────────────────────
Kill weak/unarmed enemy         -10
Flee from combat                -5
Betray ally                     -20
Attack from hiding (ambush)     -3
Fail trial                      -10
```

### Honour Thresholds
```
Honour Level     Status              Effect
──────────────────────────────────────────────────
> 50             Honoured Hunter     Father approves
> 30             Respected           Clan acceptance
0 to 30          Unblooded          Neutral standing
-30 to 0         Questionable       Father disappointed
< -30            Dishonoured        Exile from clan
```

### Clan Ranks
```
Rank Progression:
┌─────────────────────────────────────┐
│ 1. Unblooded (starting)             │
│         ↓ (first kill)              │
│ 2. Young Blood                      │
│         ↓ (honour > 30)             │
│ 3. Blooded                          │
│         ↓ (honour > 60)             │
│ 4. Warrior                          │
│         ↓ (honour > 100)            │
│ 5. Elite                            │
└─────────────────────────────────────┘
```

---

## 🌦️ 6. WEATHER SYSTEM

### Weather States
```
┌─────────────────────────────────────────────────────────────┐
│  ☀ CALM                                                     │
│  ├── Damage: 0                                              │
│  ├── Effect: Normal conditions                              │
│  └── Duration: Variable                                     │
├─────────────────────────────────────────────────────────────┤
│  🌪 SANDSTORM                                                │
│  ├── Damage: 2 per turn                                     │
│  ├── Effect: Reduced visibility                             │
│  └── Duration: 5-15 turns                                   │
├─────────────────────────────────────────────────────────────┤
│  ☢ ACID RAIN                                                │
│  ├── Damage: 5 per turn                                     │
│  ├── Effect: Corrosive, damages all                         │
│  └── Duration: 3-8 turns                                    │
├─────────────────────────────────────────────────────────────┤
│  ⚡ ELECTRICAL STORM                                         │
│  ├── Damage: 3 per turn                                     │
│  ├── Effect: Random lightning strikes                       │
│  └── Duration: 5-10 turns                                   │
└─────────────────────────────────────────────────────────────┘
```

### Weather Transition
```
Transition Probability: 10% per turn

Transition Matrix:
From → To          Probability
────────────────────────────────
Calm → Sandstorm      40%
Calm → AcidRain       30%
Calm → Storm          30%
Any → Calm            50%
```

---

## 📦 7. ITEM SYSTEM

### Item Types
```
┌─────────────────────────────────────────────────────────────┐
│  🩹 MEDKIT                                                   │
│  ├── Effect: +30 Health                                     │
│  ├── Target: All agents                                     │
│  └── Rarity: Common                                         │
├─────────────────────────────────────────────────────────────┤
│  ⚡ ENERGY PACK                                              │
│  ├── Effect: +20 Stamina                                    │
│  ├── Target: All agents                                     │
│  └── Rarity: Common                                         │
├─────────────────────────────────────────────────────────────┤
│  🔧 REPAIR KIT                                               │
│  ├── Effect: +15 Health                                     │
│  ├── Target: Synthetics only (Thia)                         │
│  └── Rarity: Uncommon                                       │
├─────────────────────────────────────────────────────────────┤
│  ⚔️ WEAPON ITEM                                              │
│  ├── Effect: +5 Attack damage (permanent)                   │
│  ├── Target: Combat agents                                  │
│  └── Rarity: Rare                                           │
└─────────────────────────────────────────────────────────────┘
```

### Item Pickup
```
Automatic on cell entry:
┌─────────────────────────────────────┐
│ Agent moves to cell with item       │
│         ↓                           │
│ Check if item applicable            │
│         ↓                           │
│ If yes → Apply effect               │
│        → Remove from cell           │
│        → Log event                  │
│         ↓                           │
│ If no → Item stays on cell          │
└─────────────────────────────────────┘
```

---

## 🏁 8. VICTORY CONDITIONS

### Win Condition
```
┌─────────────────────────────────────────────────────────────┐
│                    ◆ VICTORY ◆                              │
│                                                             │
│  Conditions:                                                │
│  ├── BOSS is defeated (health <= 0)                         │
│  └── DEK is still alive                                     │
│                                                             │
│  Rewards:                                                   │
│  ├── +50 Honour for boss kill                               │
│  ├── Clan recognition                                       │
│  └── Father's approval                                      │
└─────────────────────────────────────────────────────────────┘
```

### Lose Condition
```
┌─────────────────────────────────────────────────────────────┐
│                    ✖ DEFEAT ✖                               │
│                                                             │
│  Conditions:                                                │
│  └── DEK health <= 0                                        │
│                                                             │
│  Consequences:                                              │
│  ├── Simulation ends                                        │
│  ├── No clan advancement                                    │
│  └── Father's disappointment                                │
└─────────────────────────────────────────────────────────────┘
```

### Timeout Condition
```
┌─────────────────────────────────────────────────────────────┐
│                    ◉ TIMEOUT ◉                              │
│                                                             │
│  Conditions:                                                │
│  └── Turn count >= 100 (configurable)                       │
│                                                             │
│  Result:                                                    │
│  ├── Draw / Inconclusive                                    │
│  └── Neither victory nor defeat                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🖥️ 9. VISUAL INTERFACE

### UI Layout
```
┌─────────────────────────────────────────────────────────────────────┐
│                    ◀ PREDATOR: BADLANDS ▶                           │
│                  THERMAL TACTICAL INTERFACE v8.0                    │
├────────────────────────────────────┬────────────────────────────────┤
│                                    │  ┌─ MISSION STATUS ─────────┐  │
│                                    │  │ TURN: 045    ☀ Calm      │  │
│           30x30 GRID               │  │ ──────────────────────── │  │
│                                    │  │ HONOUR: [████████░░] 35  │  │
│    ◆ DEK    ● THIA                 │  └──────────────────────────┘  │
│    ▲ FATHER  ▲ BROTHER             │                                │
│    ✦ BEAST   ◉ BOSS                │  ┌─ THERMAL SIGNATURES ─────┐  │
│    ■ ITEM                          │  │ ● DEK    [████████] 85   │  │
│                                    │  │ ● THIA   [██████░░] 60   │  │
│                                    │  │ ● FATHER [████████] 150  │  │
│                                    │  │ ● BROTHER[███████░] 110  │  │
│                                    │  │ ● BOSS   [████░░░░] 80   │  │
│                                    │  │ Active Signatures: 7     │  │
│                                    │  └──────────────────────────┘  │
│                                    │                                │
│                                    │  ┌─ COMBAT LOG ─────────────┐  │
│                                    │  │ [043] DEK attacks Beast  │  │
│                                    │  │ [044] Weather: Sandstorm │  │
│                                    │  │ [045] THIA heals DEK     │  │
├────────────────────────────────────┴────────────────────────────────┤
│   ┌─ AGENT SIGNATURES ──────────────────────────────────────────┐   │
│   │  DEK  THIA  ELDER  RIVAL  BEAST  BOSS  ITEM                 │   │
│   └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│  [▶ START]  [⏸ PAUSE]  [⏭ STEP]  [↺ RESET]     SPEED: [====●===]   │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Icons (Thermal Vision Style)
```
┌─────────────────────────────────────────────────────────────┐
│  DEK (Predator Mask)                                        │
│  ┌─────┐                                                    │
│  │ ◯ ◯ │  Red glowing eyes                                  │
│  │  ▼  │  Triangular forehead                               │
│  │ ||| │  Dreadlocks                                        │
│  └─────┘                                                    │
├─────────────────────────────────────────────────────────────┤
│  THIA (Android Face)                                        │
│  ┌─────┐                                                    │
│  │ ■ ■ │  Square sensor eyes                                │
│  │  ●  │  Antenna on top                                    │
│  │ ─── │  Mouth line                                        │
│  └─────┘                                                    │
├─────────────────────────────────────────────────────────────┤
│  FATHER (Elder Predator)                                    │
│  ┌─────┐                                                    │
│  │ ◎ ◎ │  Yellow wise eyes                                  │
│  │  ◆  │  Crown jewel                                       │
│  │|||||| Longer dreadlocks                                  │
│  └─────┘                                                    │
├─────────────────────────────────────────────────────────────┤
│  BROTHER (Young Predator)                                   │
│  ┌─────┐                                                    │
│  │ ○ ○ │  Orange eager eyes                                 │
│  │  ▽  │  Smaller forehead                                  │
│  │ ||| │  Shorter dreadlocks                                │
│  └─────┘                                                    │
├─────────────────────────────────────────────────────────────┤
│  BEAST (Wildlife)                                           │
│  ┌─────┐                                                    │
│  │/\ /\│  Pointed ears                                      │
│  │ ⊙ ⊙ │  Yellow predator eyes                              │
│  │ VVVV│  Fangs/teeth                                       │
│  └─────┘                                                    │
├─────────────────────────────────────────────────────────────┤
│  BOSS (Skull Adversary)                                     │
│  ┌─────┐                                                    │
│  │⟨   ⟩│  Devil horns                                       │
│  │ ◉ ◉ │  Black hollow eyes                                 │
│  │  ▽  │  Nose hole                                         │
│  │|||||│  Teeth                                             │
│  └─────┘                                                    │
└─────────────────────────────────────────────────────────────┘
```

### Controls
```
┌─────────────────────────────────────────────────────────────┐
│  Button        Keyboard     Action                          │
├─────────────────────────────────────────────────────────────┤
│  ▶ START       SPACE        Begin simulation                │
│  ⏸ PAUSE       SPACE        Pause/Resume                    │
│  ⏭ STEP        RIGHT ARROW  Single turn advance             │
│  ↺ RESET       R            Restart simulation              │
│  -             ESC          Exit application                │
├─────────────────────────────────────────────────────────────┤
│  SPEED SLIDER  -            50ms (fast) to 1000ms (slow)    │
└─────────────────────────────────────────────────────────────┘
```

### Visual Effects
```
┌─────────────────────────────────────────────────────────────┐
│  Glow Effects:                                              │
│  ├── DEK: Green pulsing glow                                │
│  ├── THIA: Cyan pulsing glow                                │
│  ├── BOSS: Purple pulsing glow                              │
│  └── WILDLIFE: Red pulsing glow                             │
│                                                             │
│  Health Bars:                                               │
│  ├── Green: > 60% health                                    │
│  ├── Yellow: 30-60% health                                  │
│  └── Red: < 30% health                                      │
│                                                             │
│  Combat Effects:                                            │
│  ├── Attack line between attacker and target                │
│  └── Impact circle on target                                │
│                                                             │
│  Hover Tooltip:                                             │
│  ├── Agent name                                             │
│  ├── Health / Max Health                                    │
│  ├── Stamina                                                │
│  ├── Position (x, y)                                        │
│  └── Honour (for DEK)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 10. EVENT LOGGING

### Log Categories
```
Tag          Color       Events
────────────────────────────────────────────
system       Gray        Initialization, turn start
combat       Red         Attacks, damage, deaths
honour       Green       Honour changes, trials
item         Yellow      Item pickups
weather      Orange      Weather transitions
victory      Green       Win condition
defeat       Red         Lose condition
```

### JSON Export
```json
{
  "simulation_id": "uuid",
  "timestamp": "2025-12-23T10:30:00",
  "total_turns": 67,
  "outcome": "win",
  "reason": "boss_defeated",
  "events": [
    {
      "turn": 1,
      "type": "combat",
      "message": "DEK attacks Canyon Beast for 15 damage"
    },
    {
      "turn": 45,
      "type": "weather",
      "message": "Weather changed to Sandstorm"
    }
  ]
}
```

---

## 🗂️ 11. FILE STRUCTURE

```
movieproject/
├── src/
│   ├── main.py           # Entry point, simulation engine
│   ├── grid.py           # Grid and cell management
│   ├── cell.py           # Cell class
│   ├── terrain.py        # Terrain types
│   ├── agent.py          # Base agent class
│   ├── predator.py       # Dek, Father, Brother, Clan
│   ├── synthetic.py      # Thia and other synthetics
│   ├── creatures.py      # Wildlife, Boss
│   ├── actions.py        # Action types and results
│   ├── items.py          # Item classes
│   ├── weather.py        # Weather system
│   ├── clan_code.py      # Honour and trial system
│   ├── event_logger.py   # Event logging
│   ├── renderer.py       # Text-based renderer
│   ├── config.py         # Game configuration
│   └── visualizer.py     # Tkinter UI
├── data/
│   └── *.json            # Exported logs
├── docs/
│   └── Predator_Simulation_Working.md
└── tests/
    └── __init__.py
```

---

## 🎮 12. RUNNING THE SIMULATION

### Command Line
```bash
# Run with visual interface
python src/main.py --visual

# Run without UI (console only)
python src/main.py
```

### Quick Start
```
1. Open terminal in project folder
2. Run: python src/main.py --visual
3. Window opens with thermal vision UI
4. Press START or SPACE to begin
5. Watch agents hunt and fight
6. Adjust speed with slider
7. Press R to reset anytime
```

---

## 📝 Summary

**PREDATOR: BADLANDS** is a comprehensive multi-agent simulation featuring:

- ✅ 7 unique agent types with distinct behaviors
- ✅ Turn-based tactical combat system
- ✅ Honour and clan code mechanics
- ✅ Dynamic weather hazards
- ✅ Item collection and management
- ✅ Visual thermal interface with real icons
- ✅ Event logging and JSON export
- ✅ Configurable difficulty settings

The simulation captures the essence of the Predator universe - the hunt, the honour, and the ultimate test of survival.

---

*"The hunt has begun..."* 🎬👽
