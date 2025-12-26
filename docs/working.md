# PREDATOR: BADLANDS - Complete Project Documentation (Hinglish)

## Kya Hai Ye Project?

**Predator: Badlands** ek multi-agent AI simulation hai jo Python mein banayi gayi hai. Isme Q-learning, multi-agent coordination, procedural generation, aur adaptive adversarial AI jaise advanced AI concepts use kiye gaye hain. Ye simulation Kalisk planet pe set hai jahan ek exiled Predator warrior **Dek** ko prove karna hai apne aap ko ek ultimate adversary ko defeat karke, uski help karti hai ek damaged synthetic android **Thia**.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture aur Design](#architecture-aur-design)
3. [Agent System](#agent-system)
4. [Game Mechanics](#game-mechanics)
5. [AI aur Learning Systems](#ai-aur-learning-systems)
6. [Visualization System](#visualization-system)
7. [Experiment Framework](#experiment-framework)
8. [Technical Implementation](#technical-implementation)
9. [Testing Strategy](#testing-strategy)
10. [Project Kaise Run Karein](#project-kaise-run-karein)

---

## Project Overview

### Story/Narrative

Ye simulation **Dek** ki kahani follow karti hai, jo ek young Yautja (Predator) warrior hai jisko uski clan se exile kar diya gaya. Harsh planet Kalisk pe, Dek ko milti hai **Thia**, ek damaged Weyland-Yutani synthetic android. Dono ko milke dangerous terrain navigate karna hai, hostile wildlife face karni hai, aur ultimately ek **Ultimate Adversary** (Boss) ko defeat karna hai taake Dek apni worth prove kar sake aur clan acceptance regain kar sake.

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Simulation** | 7+ different agent types unique behaviors ke saath |
| **Toroidal Grid World** | 40×30 wrap-around environment varied terrain ke saath |
| **Honour System** | Full Yautja Clan Code violations aur rewards ke saath |
| **Adaptive AI** | Q-learning agents ke liye, adaptive behavior Boss ke liye |
| **Procedural Generation** | Dynamic hazard aur terrain generation |
| **Real-time Visualization** | Tkinter-based thermal vision GUI |
| **Experiment Framework** | Automated testing metrics collection ke saath |

### Libraries Used

```python
# Standard Library (Koi external dependencies nahi core ke liye)
- tkinter       # GUI visualization ke liye
- json          # Data persistence ke liye
- csv           # Data export ke liye
- random        # Randomization ke liye
- abc           # Abstract base classes ke liye
- dataclasses   # Data structures ke liye
- enum          # Enumerations ke liye
- statistics    # Metrics analysis ke liye
- typing        # Type hints ke liye
- pathlib       # File path handling ke liye
- math          # Mathematical calculations ke liye
- time          # Timing functions ke liye

# Optional
- matplotlib    # Experiment visualization plots ke liye
```

---

## Architecture aur Design

### Project Structure (Folder Layout)

```
moviesimulation/
├── src/                    # Main source code
│   ├── main.py            # Entry point aur simulation engine
│   ├── grid.py            # 2D toroidal grid implementation
│   ├── cell.py            # Individual cell management
│   ├── terrain.py         # Terrain types aur properties
│   ├── agent.py           # Abstract base agent class
│   ├── predator.py        # Predator agents (Dek, Father, Brother)
│   ├── synthetic.py       # Synthetic agents (Thia)
│   ├── creatures.py       # Wildlife aur Boss agents
│   ├── items.py           # Resource items
│   ├── actions.py         # Action types aur results
│   ├── clan_code.py       # Yautja honour system
│   ├── coordination.py    # Multi-agent coordination
│   ├── learning.py        # Q-learning implementation
│   ├── procedural.py      # Procedural generation
│   ├── weather.py         # Weather system
│   ├── visualizer.py      # Tkinter GUI
│   ├── config.py          # Game configuration
│   ├── event_logger.py    # Event logging
│   ├── metrics.py         # Metrics collection
│   ├── data_collector.py  # Data persistence
│   ├── experiment_runner.py    # Automated experiments
│   └── experiment_visualizer.py # Matplotlib plots
├── tests/                  # Unit tests
│   ├── test_p2.py         # Grid tests (60+ tests)
│   ├── test_p3.py         # Agent tests (50+ tests)
│   ├── test_p4.py         # Combat tests
│   ├── test_p5.py         # Synthetic tests
│   ├── test_p6.py         # Clan code tests
│   ├── test_p7.py         # Hazard tests
│   ├── test_p8.py         # Visualizer tests
│   ├── test_p9.py         # Learning tests
│   └── test_p10.py        # Experiment tests (38 tests)
├── data/                   # Output data
│   ├── experiments/       # Experiment results
│   │   ├── csv/          # CSV exports
│   │   ├── json/         # JSON backups
│   │   └── plots/        # Generated graphs
│   └── *_q_table.json    # Saved Q-tables
├── docs/                   # Documentation
│   └── working.md        # Ye file
└── run_full_experiment.py # Full experiment script
```

### Class Hierarchy (Kaun Kisse Inherit Karta Hai)

```
Agent (ABC) - Abstract Base Class
├── PredatorAgent
│   ├── Dek              [Hero - 180 HP, 150 Stamina]
│   ├── PredatorFather   [Elder - 180 HP, 140 Stamina]
│   ├── PredatorBrother  [Rival - 150 HP, 130 Stamina]
│   └── PredatorClan     [Warrior - Variable stats]
├── SyntheticAgent
│   ├── Thia             [Ally - 60 HP, 150 Stamina]
│   └── SyntheticEnemy   [Enemy synthetic - Variable]
├── WildlifeAgent        [Wildlife - 50 HP, 80 Stamina]
└── BossAdversary        [Boss - 150 HP, 300 Stamina]
```

---

## Agent System

### Agent Base Class

Saare agents ek abstract `Agent` class se inherit karte hain:

```python
class Agent(ABC):
    - name: str              # Agent ka naam
    - x, y: int             # Position grid pe
    - health, max_health: int  # Health points
    - stamina, max_stamina: int # Energy/Stamina
    - is_alive: bool        # Zinda hai ya nahi
    
    Methods:
    - take_damage(amount)    # Damage lena
    - heal(amount)           # Health recover karna
    - consume_stamina(amount) # Stamina use karna
    - restore_stamina(amount) # Stamina wapas lena
    - move_to(x, y)          # Move karna
    - decide_action()        # Kya action lena hai (Abstract)
    - update()               # Har turn pe update (Abstract)
```

### Dek (Main Hero Character)

| Stat | Value | Description |
|------|-------|-------------|
| Health | 180 | Zyada health hero survivability ke liye |
| Stamina | 150 | Sustained action ke liye |
| Attack Damage | 35-55 | Strong melee combat |
| Stealth Bonus | 2.0x | Double damage stealth se |
| Special | Carry Thia | Injured ally ko carry kar sakta hai |

**Dek Ke Actions:**
- MOVE (8 directions mein move kar sakta hai)
- ATTACK (melee combat)
- REST (health aur stamina recover)
- COLLECT_TROPHY (defeated enemies se trophy)
- STEALTH (invisible ho jata hai, bonus damage milta hai)
- CARRY/DROP (Thia ko uthao/chod do)
- SCAN (area reconnaissance)
- REQUEST_INFO / SHARE_INFO (coordination ke liye)
- FORM_ALLIANCE (ally bonding)

### Thia (Synthetic Android Ally)

| Stat | Value | Description |
|------|-------|-------------|
| Health | 60 | Fragile lekin essential |
| Stamina | 150 | Long-lasting battery |
| Damage Level | 40% | Pehle se damaged condition |
| Mobility | Limited | Carry hona padta hai |
| Trust in Dek | 0-100 | Time ke saath build hoti hai |

**Thia Ki Abilities:**
- **Intel Database**: Enemy weaknesses, safe routes, hazard locations jaanti hai
- **Scan Area**: 4-cell radius mein threats detect karna
- **Provide Intel**: Dek ke saath strategic info share karna
- **Warning System**: Allies ko danger ke baare mein alert karna

### Boss Adversary (Ultimate Enemy)

| Stat | Phase 1 | Phase 2 |
|------|---------|---------|
| Health | 150 | Phase 1 se continue |
| Attack Range | 2 cells | 2 cells |
| Basic Damage | 18-30 | 28-45 |
| Earthquake | 15-25 | 25-40 |
| Energy Blast | 35-55 | 45-70 |
| Rage Multiplier | 1.0x | 1.3x |
| Scan Radius | 5 cells | 8 cells |

**Boss Ki Special Abilities:**
1. **Earthquake**: Area damage 4-6 cell radius mein
2. **Energy Blast**: Ranged targeted attack
3. **Regeneration**: 50 HP tak heal kar sakta hai
4. **Phase Transition**: 50% HP pe zyada aggressive ho jata hai

### Clan Agents (Family Members)

| Agent | Role | Dek Ke Baare Mein Opinion | Special Power |
|-------|------|---------------------------|---------------|
| Father | Elder Kaail | Shuru mein -20 | Trials issue karta hai, approve/reject kar sakta hai |
| Brother | Cetanu | Rivalry vary hoti hai | Duels ke liye challenge, jealousy mechanics |
| Warrior | Generic | Neutral | Patrol aur combat |

---

## Game Mechanics

### Toroidal Grid (Wrap-Around Duniya)

Game world 40×30 grid hai **wrap-around edges** ke saath:
- Right edge se jaoge toh left side pe aa jaoge
- Bottom se jaoge toh top pe aa jaoge
- Strategic flanking maneuvers enable hote hain

### Terrain Types (Zameen Ke Types)

| Terrain | Symbol | Move Cost | Damage | Khatarnak? |
|---------|--------|-----------|--------|------------|
| Empty | `.` | 1 | 0 | Nahi |
| Desert | `~` | 2 | 0 | Nahi |
| Rocky | `^` | 3 | 0 | Nahi |
| Canyon | `#` | 2 | 0 | Nahi |
| Hostile | `!` | 4 | 5 | Haan |
| Trap | `X` | 5 | 15 | Haan |
| Teleport | `O` | 1 | 0 | Nahi |

### Weather System (Mausam)

Dynamic weather saare agents ko affect karta hai:

| Weather | Move Cost | Global Damage | Visibility |
|---------|-----------|---------------|------------|
| Calm | 1.0x | 0 | Full |
| Sandstorm | 1.3x | 0 | Reduced |
| Acid Rain | 1.1x | 3/turn | Normal |
| Electrical Storm | 1.2x | 1/turn | Reduced |

### Honour System (Yautja Clan Code - Izzat Ka System)

**Honourable Actions (+Honour milti hai):**
| Action | Honour | Reputation |
|--------|--------|------------|
| Worthy Kill | +10 | +5 |
| Protect Ally | +8 | +3 |
| Face Superior Foe | +15 | +8 |
| Complete Trial | +20 | +10 |
| Defeat Boss | +50 | +30 |
| Save Thia | +12 | +5 |

**Code Violations (-Honour jaati hai):**
| Violation | Penalty | Severity |
|-----------|---------|----------|
| Hunt Unworthy | -15 | High |
| Unfair Advantage | -10 | Medium |
| Territory Violation | -20 | High |
| Trophy Theft | -25 | Severe |
| Harm Innocent | -30 | Severe |
| Cowardice | -12 | Medium |
| Abandon Ally | -22 | High |

### Resource Items (Cheezein Jo Mil Sakti Hain)

| Item | Effect | Kitni Common |
|------|--------|--------------|
| Medkit | +15-35 HP | 35% |
| Energy Pack | +20-40 Stamina | 35% |
| Repair Kit | -15-30 Damage (Thia ke liye) | 20% |
| Weapon | Arsenal mein add hota hai | 10% |

---

## AI aur Learning Systems

### Q-Learning Implementation

Simulation mein **Tabular Q-Learning** implement kiya gaya hai Dek aur Thia ke liye:

```python
Q(s,a) ← Q(s,a) + α[R + γ·max(Q(s',a')) - Q(s,a)]

Parameters:
- α (learning_rate) = 0.1      # Kitna fast seekhna hai
- γ (discount_factor) = 0.95   # Future rewards ki importance
- ε (exploration_rate) = 0.3 → 0.05 (decay hota hai)  # Random exploration
```

**State Space (Discretized - States Ko Categories Mein Divide Kiya):**
```python
State = (health_level, enemy_distance, enemy_count, 
         ally_nearby, stamina_level, boss_phase)

health_level: 0-3 (0=critical, 3=healthy)
enemy_distance: 0-3 (0=paas, 3=door)
enemy_count: 0-3 (0=koi nahi, 3=bahut)
ally_nearby: 0/1 (haan ya nahi)
stamina_level: 0-2 (0=kam, 2=zyada)
boss_phase: 1-2
```

**Action Space (Jo Actions Le Sakte Hain):**
```python
ActionSpace = {
    ATTACK, RETREAT, HEAL, MOVE_TOWARDS, 
    MOVE_AWAY, COORDINATE, DEFEND, FLANK, REST, SPECIAL
}
```

**Reward Function (Rewards aur Penalties):**
| Event | Reward |
|-------|--------|
| Kill Wildlife | +10.0 |
| Kill Boss | +100.0 |
| Damage Dealt | +0.5/point |
| Damage Taken | -0.3/point |
| Death | -100.0 |
| Ally Death | -50.0 |
| Coordination Bonus | +8.0 |
| Survive Turn | +0.1 |
| Smart Retreat | +5.0 |

### Multi-Agent Coordination (Dek aur Thia Ka Teamwork)

Coordination system Dek aur Thia ko saath mein kaam karne deta hai:

**Roles (Kirdaar):**
- LEADER (Dek - attack focus)
- SUPPORT (Thia - intel/healing)
- SCOUT (reconnaissance)
- TANK (enemy fire draw karo)
- HEALER (ally support)
- ATTACKER (damage dealing)

**Shared Goals (Common Objectives):**
```python
GoalType = {
    SURVIVE,          # Bachna
    HUNT_TARGET,      # Target hunt karna
    PROTECT_ALLY,     # Ally protect karna
    COLLECT_ITEM,     # Item collect karna
    REACH_POSITION,   # Position pe pahunchna
    ESCAPE_DANGER,    # Danger se bhagna
    DEFEAT_BOSS,      # Boss ko maarna
    HEAL_ALLY,        # Ally ko heal karna
    COVER_ALLY,       # Ally ko cover dena
    FLANK_ENEMY       # Enemy ko flank karna
}
```

**Coordination Protocol (Kaise Kaam Karta Hai):**
1. **Threat Assessment**: Saare enemies evaluate karo
2. **Goal Planning**: Priorities assign karo
3. **Role Assignment**: Tasks distribute karo
4. **Action Sync**: Coordinated attacks execute karo
5. **Communication**: Intel aur warnings share karo

### Adaptive Boss AI (Boss Ka Dimag)

Boss **reactive behavior trees** use karta hai:

1. **Threat Detection**: 5-8 cell radius scan karta hai
2. **Target Selection**: Wounded ya isolated enemies ko priority
3. **Ability Selection**: Optimal attack choose karta hai based on:
   - Enemy positions (groups ke liye earthquake)
   - Health status (kam health pe regenerate)
   - Rage level (enraged hone pe special attacks)
4. **Phase Transition**: 50% HP pe zyada aggressive ho jata hai

### Procedural Generation (Randomly Generated Content)

**Perlin Noise** use hota hai natural-looking hazard placement ke liye:

**Hazard Types (Khatre Ke Types):**
- Acid Pool (spreading damage)
- Spike Trap (high single damage)
- Fire Vent (delayed activation)
- Quicksand (slow kar deta hai)
- Radiation (lingering damage)
- Electric Field (periodic pulses)
- Poison Gas (spreading cloud)
- Collapse Zone (warning phir damage)

**Pattern Types (Hazards Kaise Generate Hote Hain):**
- Random, Clustered, Linear, Circular
- Spiral, Wave, Symmetric, Perimeter

---

## Visualization System

### Tkinter GUI Features

Visualizer ek comprehensive thermal-vision interface provide karta hai:

**Main Components (Parts):**
1. **Grid Canvas** (40×30 cells terrain colors ke saath)
2. **Minimap** (tactical overview)
3. **Mission Status** (turn, weather, honour)
4. **Combat Statistics** (damage, kills, items)
5. **Thermal Signatures** (saare agents ki health bars)
6. **Event Log** (scrolling combat/system messages)
7. **Control Panel** (start, pause, step, reset)

**Color Scheme (Thermal Vision Colors):**
```python
THERMAL_COLORS = {
    'background': '#050505',    # Near black
    'dek': '#00ff00',          # Bright green - Hero
    'thia': '#00ffff',         # Cyan - Ally
    'father': '#ffaa00',       # Orange - Elder
    'brother': '#ff6600',      # Dark orange - Rival
    'wildlife': '#ff3333',     # Red - Enemies
    'boss': '#ff00ff',         # Magenta - Ultimate Boss
    'item': '#ffff00',         # Yellow - Items
}
```

**Interactive Features:**
- Mouse hover pe agent details dikhte hain
- Keyboard shortcuts (1-4 speed ke liye, SPACE pause ke liye)
- Achievement popups
- Combat flash effects
- Speed presets (0.5x se 4x tak)

### Controls (Kaise Chalayein)

| Key/Button | Action |
|------------|--------|
| SPACE | Start/Pause simulation |
| STEP | Ek turn aage badho |
| RESET | Simulation restart karo |
| 1-4 | Speed presets |
| Theme | Color themes switch karo |

---

## Experiment Framework

### Automated Testing

Experiment system multiple simulations run karta hai statistical analysis ke liye:

**Configuration Options:**
```python
ExperimentConfig(
    name="normal",
    difficulty=DifficultyLevel.NORMAL,
    grid_size=(40, 30),
    max_turns=200,
    boss_health_multiplier=1.0,
    wildlife_count=4,
    resource_count=15,
    num_runs=20,
    enable_coordination=True,
    enable_learning=True
)
```

**Pre-defined Configurations:**
| Config | Boss HP | Wildlife | Resources |
|--------|---------|----------|-----------|
| Easy | 0.7x | 2 | 20 |
| Normal | 1.0x | 4 | 15 |
| Hard | 1.5x | 6 | 10 |
| Extreme | 2.0x | 8 | 5 |
| No Coordination | 1.0x | 4 | 15 |
| No Learning | 1.0x | 4 | 15 |
| Baseline | 1.0x | 4 | 15 |

### Metrics Collection (Kya Data Collect Hota Hai)

**Per-Agent Metrics:**
- survival_time (kitni der zinda raha)
- honour_history (honour ka track)
- kills, deaths (kitne maare, kitni baar mara)
- resources_collected (kitni cheezein mili)
- distance_traveled (kitna chala)
- combats_won (kitne fights jeete)
- coordinated_actions (kitne coordinated moves)

**Per-Simulation Metrics:**
- total_steps (kitne turns lage)
- winner (victory/defeat/timeout)
- boss_defeated (boss mara ya nahi)
- team_survival_rate (team kitni bachi)
- total_combats (total fights)
- resource_efficiency (resources kitni efficiently use hui)

### Output Formats (Results Kaise Save Hote Hain)

**CSV Files:**
- `simulation_results_*.csv` - Per-simulation summary
- `agent_metrics_*.csv` - Per-agent detailed data
- `honour_progression_*.csv` - Honour over time
- `summary_stats_*.csv` - Aggregate statistics

**JSON Backup:**
- Complete experiment data later analysis ke liye

**Matplotlib Plots:**
- Win rate comparison bar charts
- Survival time distributions
- Honour progression curves
- Combat effectiveness comparisons

---

## Technical Implementation

### Key Design Patterns (Jo Patterns Use Kiye Gaye)

1. **Abstract Factory**: Agent creation ke liye
2. **Strategy Pattern**: Different AI behaviors ke liye
3. **Observer Pattern**: Event logging aur notifications ke liye
4. **State Pattern**: Agent states (alive, dead, carried) ke liye
5. **Template Method**: Base agent customizable actions ke saath

### Performance Optimizations

- Grid O(1) cell access use karta hai 2D array se
- Distance calculations Chebyshev distance use karti hain
- Q-table dictionary use karta hai sparse state space ke liye
- Batch rendering GUI updates ke liye

### Error Handling

- Agar matplotlib available nahi hai toh graceful degradation
- Safe file operations exception handling ke saath
- Input validation saari user-configurable values ke liye

---

## Testing Strategy

### Test Coverage (Kitne Tests Hain)

| Module | Tests | Coverage |
|--------|-------|----------|
| Grid (Phase 2) | 60+ | Complete |
| Agents (Phase 3) | 50+ | Complete |
| Combat (Phase 4) | 40+ | Complete |
| Synthetics (Phase 5) | 30+ | Complete |
| Clan Code (Phase 6) | 40+ | Complete |
| Hazards (Phase 7) | 30+ | Complete |
| Visualizer (Phase 8) | 30+ | Complete |
| Learning (Phase 9) | 50+ | Complete |
| Experiments (Phase 10) | 38 | Complete |
| **TOTAL** | **470** | **Sab Pass** |

### Tests Kaise Run Karein

```bash
# Saare tests run karo
py -m unittest discover tests -v

# Specific phase ke tests
py -m unittest tests.test_p2 -v

# Quick verification
py -m unittest discover tests 2>&1 | Select-String "(OK|FAILED)"
```

---

## Project Kaise Run Karein

### Prerequisites (Kya Chahiye)

- Python 3.12+
- Koi external dependencies nahi core ke liye (standard library only)
- Optional: `pip install matplotlib` experiment plots ke liye

### Quick Start (Jaldi Shuru Karo)

```bash
# Visual simulation (GUI ke saath)
cd src
py main.py

# CLI mode (command line)
py main.py --cli

# Full experiment suite run karo (80 simulations)
py run_full_experiment.py
```

### Game Controls (Game Kaise Khelein)

1. Game launch karo `py main.py` se
2. **SPACE** dabao ya **START** click karo shuru karne ke liye
3. Agents automatically interact karte hain - dekho
4. **STEP** use karo turn-by-turn analysis ke liye
5. Speed adjust karo **1-4** keys ya slider se
6. **RESET** dabao nayi simulation shuru karne ke liye

### Victory Conditions (Jeetne Ke Tareekey)

| Outcome | Condition |
|---------|-----------|
| **VICTORY** | Boss ki health 0 ho jaye, Dek zinda rahe |
| **DEFEAT** | Dek ki health 0 ho jaye |
| **TIMEOUT** | Max turns (200) complete ho jayein |

---

## Agent Stats Summary (Saare Agents Ki Stats)

| Agent | HP | Stamina | Attack | Role |
|-------|------|---------|--------|------|
| Dek | 180 | 150 | 35-55 | Hero |
| Thia | 60 | 150 | Support | Ally |
| Father | 180 | 140 | 20-30 | Neutral |
| Brother | 150 | 130 | 18-28 | Rival |
| Wildlife | 50 | 80 | 5-15 | Enemy |
| Boss | 150 | 300 | 18-70 | Ultimate |

---

## Conclusion (Khatam Ki Baat)

**Predator: Badlands** multi-agent AI concepts ka comprehensive implementation hai ek engaging simulation environment mein. Project ye demonstrate karta hai:

1. **AI Fundamentals**: Q-learning, state machines, behavior trees
2. **Multi-Agent Systems**: Coordination, communication, role-based strategies
3. **Game Development**: Grid-based movement, combat systems, resource management
4. **Software Engineering**: Clean architecture, comprehensive testing, documentation
5. **Data Science**: Metrics collection, statistical analysis, visualization

Simulation successfully entertainment value ko educational AI concepts ke saath balance karti hai, jisse ye dono ek functional game aur intelligent agent behavior study karne ka platform ban jaata hai.

---

*Document Version: 1.0*  
*Last Updated: December 26, 2025*  
*Project: CPS5002 Artificial Intelligence Assessment*
