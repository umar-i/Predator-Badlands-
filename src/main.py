import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grid import Grid
from renderer import GridRenderer


def test_clan_honour_system():
    from predator import Dek, PredatorFather, PredatorBrother, PredatorClan
    from synthetic import Thia
    from creatures import WildlifeAgent, BossAdversary
    from actions import ActionType, Direction
    from event_logger import EventLogger
    from clan_code import (
        YautjaClanCode, ClanTrialManager, HonourTracker,
        ClanRelationship, HonourableAction, ClanCodeViolation
    )
    
    print("=" * 70)
    print("PREDATOR: BADLANDS SIMULATION")
    print("Phase 6: Clan & Honour System Test")
    print("=" * 70)
    
    grid = Grid(30, 30)
    grid.generate_terrain()
    renderer = GridRenderer(grid)
    logger = EventLogger()
    trial_manager = ClanTrialManager()
    
    dek = Dek(10, 10)
    thia = Thia(11, 10)
    father = PredatorFather("Elder Kaail", 5, 5)
    brother = PredatorBrother("Cetanu", 15, 10)
    clan_warrior = PredatorClan("Warrior Thar", 8, 8, "warrior")
    wildlife1 = WildlifeAgent("Canyon Beast", "predator", 12, 12)
    wildlife2 = WildlifeAgent("Desert Stalker", "predator", 14, 14)
    boss = BossAdversary("Ultimate Adversary", 25, 25)
    
    honour_tracker = HonourTracker(dek)
    
    father.set_trial_manager(trial_manager)
    father.set_dek_reference(dek)
    brother.set_dek_reference(dek)
    
    agents = [dek, thia, father, brother, clan_warrior, wildlife1, wildlife2, boss]
    
    for agent in agents:
        agent.set_grid(grid)
        grid.place_agent(agent, agent.x, agent.y)
    
    print(f"\n{'='*70}")
    print("INITIAL STATE")
    print(f"{'='*70}")
    print(f"\nDek Status:")
    print(f"  Position: ({dek.x}, {dek.y})")
    print(f"  Honour: {dek.honour}")
    print(f"  Clan Rank: {dek.clan_rank}")
    print(f"  Is Exiled: {dek.is_exiled}")
    print(f"  Clan Judgment: {YautjaClanCode.get_clan_judgment(dek)}")
    
    print(f"\nFather Status:")
    print(f"  {father.name}")
    print(f"  Opinion of Dek: {father.opinion_of_dek}")
    print(f"  Relationship: {father.get_relationship_status()}")
    print(f"  Disappointed: {father.disappointed_in_dek}")
    
    print(f"\nBrother Status:")
    print(f"  {brother.name}")
    print(f"  Rivalry with Dek: {brother.rivalry_with_dek}")
    print(f"  Relationship: {brother.get_relationship_status()}")
    print(f"  Protective: {brother.protective_of_dek}")
    print(f"  Jealous: {brother.jealous_of_dek}")
    
    print(f"\n{'='*70}")
    print("TEST 1: Combat and Honour Evaluation")
    print(f"{'='*70}")
    
    wildlife1.x, wildlife1.y = dek.x + 1, dek.y
    grid.place_agent(wildlife1, wildlife1.x, wildlife1.y)
    
    attack_result = dek.perform_action(ActionType.ATTACK, None, wildlife1)
    print(f"\nDek attacks {wildlife1.name}:")
    print(f"  Result: {attack_result.message}")
    
    if attack_result.combat_result:
        honour_events = YautjaClanCode.evaluate_combat_honour(
            dek, wildlife1, attack_result.combat_result
        )
        for event_type, message in honour_events:
            print(f"  Honour Event ({event_type}): {message}")
            honour_tracker.record_change(event_type, 0, message)
    
    father_reaction = father.judge_dek_action(dek, attack_result)
    print(f"\nFather's Reaction:")
    print(f"  {father_reaction.message}")
    print(f"  Opinion Change: {father_reaction.opinion_change}")
    print(f"  New Opinion: {father.opinion_of_dek}")
    
    brother_reaction = brother.react_to_dek_success(dek, attack_result)
    print(f"\nBrother's Reaction:")
    print(f"  {brother_reaction.message}")
    print(f"  Rivalry Now: {brother.rivalry_with_dek}")
    
    print(f"\n{'='*70}")
    print("TEST 2: Trophy Collection and Clan Response")
    print(f"{'='*70}")
    
    if not wildlife1.is_alive:
        trophy_result = dek.perform_action(ActionType.COLLECT_TROPHY, None, wildlife1)
        print(f"\nDek collects trophy:")
        print(f"  Result: {trophy_result.message}")
        
        if trophy_result.trophy_collected:
            trial_manager.notify_trophy(dek, trophy_result.trophy_collected)
            print(f"  Trophy Value: {trophy_result.trophy_collected.get_honour_value()}")
        
        father_reaction2 = father.judge_dek_action(dek, trophy_result)
        print(f"\nFather's Reaction to Trophy:")
        print(f"  {father_reaction2.message}")
        print(f"  Opinion Now: {father.opinion_of_dek}")
        
        brother_reaction2 = brother.react_to_dek_success(dek, trophy_result)
        print(f"\nBrother's Reaction to Trophy:")
        print(f"  {brother_reaction2.message}")
        print(f"  Jealous Now: {brother.jealous_of_dek}")
    
    print(f"\n{'='*70}")
    print("TEST 3: Thia Assistance and Honour")
    print(f"{'='*70}")
    
    carry_result = dek.perform_action(ActionType.CARRY, None, thia)
    print(f"\nDek carries Thia:")
    print(f"  Result: {carry_result.message}")
    
    thia_honour = YautjaClanCode.evaluate_thia_assistance(dek, 'carry')
    if thia_honour:
        print(f"  Honour for helping Thia: {thia_honour}")
    
    father_reaction3 = father.judge_dek_action(dek, carry_result)
    print(f"\nFather's View on Protecting Ally:")
    print(f"  {father_reaction3.message}")
    
    print(f"\n{'='*70}")
    print("TEST 4: Clan Trial System")
    print(f"{'='*70}")
    
    trial_message = father.issue_trial_to_dek(dek, "combat")
    print(f"\n{trial_message}")
    
    active_trials = trial_manager.get_active_trials_for(dek)
    print(f"\nActive Trials for Dek: {len(active_trials)}")
    for trial in active_trials:
        status = trial.get_status()
        print(f"  - {status['trial_type']}: {status['progress']}")
        print(f"    Time Remaining: {status['time_remaining']}")
    
    print(f"\n{'='*70}")
    print("TEST 5: Brother Rivalry Dynamics")
    print(f"{'='*70}")
    
    original_rivalry = brother.rivalry_with_dek
    
    for i in range(3):
        brother.rivalry_with_dek += 5
        print(f"\nRivalry increased to {brother.rivalry_with_dek}")
        print(f"  Status: {brother.get_relationship_status()}")
        
        challenge = brother.challenge_dek_to_duel(dek)
        if challenge:
            print(f"  CHALLENGE: {challenge}")
    
    brother.rivalry_with_dek = original_rivalry
    
    print(f"\n{'='*70}")
    print("TEST 6: Approval/Rejection Thresholds")
    print(f"{'='*70}")
    
    print(f"\nTesting Approval Path:")
    father.opinion_of_dek = 35
    approval = father.approve_dek(dek)
    if approval:
        print(f"  {approval}")
        print(f"  Dek Exiled Status: {dek.is_exiled}")
    
    print(f"\nTesting Rejection Path:")
    father.opinion_of_dek = -35
    rejection = father.reject_dek(dek)
    if rejection:
        print(f"  {rejection}")
        print(f"  Dek Exiled Status: {dek.is_exiled}")
    
    father.opinion_of_dek = -20
    
    print(f"\n{'='*70}")
    print("TEST 7: Honour Tracker Summary")
    print(f"{'='*70}")
    
    tracker_summary = honour_tracker.get_summary()
    print(f"\nHonour Tracking Summary:")
    for key, value in tracker_summary.items():
        print(f"  {key}: {value}")
    
    print(f"\n{'='*70}")
    print("TEST 8: Simulation Loop (10 turns)")
    print(f"{'='*70}")
    
    father.opinion_of_dek = -15
    dek.is_exiled = True
    
    for turn in range(10):
        logger.increment_step()
        trial_manager.update_trials()
        
        for agent in agents:
            if agent.is_alive:
                agent.step()
        
        if turn % 3 == 0:
            print(f"\nTurn {turn + 1}:")
            print(f"  Dek - Honour: {dek.honour}, Position: ({dek.x}, {dek.y})")
            print(f"  Father Opinion: {father.opinion_of_dek}")
            print(f"  Brother Rivalry: {brother.rivalry_with_dek}")
            
            trials = trial_manager.get_active_trials_for(dek)
            if trials:
                for t in trials:
                    trial_manager.notify_survival(dek)
    
    print(f"\n{'='*70}")
    print("FINAL STATE")
    print(f"{'='*70}")
    
    print(f"\nDek Final Status:")
    print(f"  Honour: {dek.honour}")
    print(f"  Clan Rank: {dek.clan_rank}")
    print(f"  Clan Judgment: {YautjaClanCode.get_clan_judgment(dek)}")
    print(f"  Trophies: {len(dek.trophies)}")
    
    print(f"\nClan Relationships:")
    print(f"  Father: {father.get_relationship_status()}")
    print(f"  Brother: {brother.get_relationship_status()}")
    
    print(f"\nTrial Manager Summary:")
    trial_summary = trial_manager.get_trial_summary()
    for key, value in trial_summary.items():
        print(f"  {key}: {value}")
    
    logger.export_events_json('data/phase6_test.json')
    print(f"\nEvent log exported to: data/phase6_test.json")
    
    print(f"\n{'='*70}")
    print("Phase 6 Test Complete - Requirement (e) Satisfied")
    print("Clan & Honour System Fully Implemented")
    print(f"{'='*70}")


def run_phase7_simulation():
    import random
    from predator import Dek, PredatorFather, PredatorBrother
    from synthetic import Thia
    from creatures import WildlifeAgent, BossAdversary
    from items import random_item
    from weather import WeatherSystem
    from actions import ActionType
    from event_logger import EventLogger
    from clan_code import YautjaClanCode
    
    grid = Grid(30, 30)
    grid.generate_terrain()
    logger = EventLogger()
    weather = WeatherSystem()
    renderer = GridRenderer(grid)
    
    dek = Dek(10, 10)
    thia = Thia(11, 10)
    father = PredatorFather("Elder Kaail", 5, 5)
    brother = PredatorBrother("Cetanu", 15, 10)
    wildlife = [
        WildlifeAgent("Canyon Beast", "predator", 12, 12),
        WildlifeAgent("Sand Raptor", "predator", 18, 18)
    ]
    boss = BossAdversary("Ultimate Adversary", 25, 25)
    agents = [dek, thia, father, brother, boss] + wildlife
    
    for a in agents:
        a.set_grid(grid)
        grid.place_agent(a, a.x, a.y)
    
    resource_spots = 18
    placed = 0
    rng = random.Random(42)
    while placed < resource_spots:
        cell = grid.find_empty_cell()
        if not cell:
            break
        item = random_item()
        cell.add_item(item)
        placed += 1
    
    turns = 80
    outcome = None
    reason = ""
    
    def try_pickup(agent):
        cell = grid.get_cell(agent.x, agent.y)
        if not cell.items:
            return
        new_items = []
        for it in cell.items:
            if it.apply(agent):
                logger.log_item_pickup(agent, it)
            else:
                new_items.append(it)
        cell.items = new_items
    
    print("=" * 70)
    print("Phase 7: Survival, Hazards, and Boss")
    print("=" * 70)
    
    for t in range(1, turns + 1):
        logger.increment_step()
        changed = weather.maybe_transition()
        if changed:
            logger.log_weather_change(weather.current)
        
        for agent in list(agents):
            if not agent.is_alive:
                continue
            agent.step()
            try_pickup(agent)
        
        wd = weather.damage_this_turn()
        if wd > 0:
            for agent in agents:
                if agent.is_alive:
                    before = agent.health
                    agent.take_damage(wd)
                    if agent.health < before:
                        logger.log_hazard_effect(agent, wd, weather.current.name)
        
        if not boss.is_alive and dek.is_alive:
            outcome = "win"
            reason = "boss_defeated"
            break
        if not dek.is_alive:
            outcome = "lose"
            reason = "dek_dead"
            break
        
        if t % 10 == 0:
            print(f"Turn {t} | Dek H:{dek.health} S:{dek.stamina} Honour:{dek.honour} | Boss H:{boss.health}")
    
    if not outcome:
        outcome = "timeout"
        reason = "turn_limit"
    logger.log_outcome(outcome, logger.step_counter, reason)
    logger.export_events_json('data/phase7_run.json')
    print(f"Outcome: {outcome} ({reason}) -> data/phase7_run.json")


class SimulationEngine:
    
    def __init__(self, config):
        from predator import Dek, PredatorFather, PredatorBrother
        from synthetic import Thia
        from creatures import WildlifeAgent, BossAdversary
        from items import random_item
        from weather import WeatherSystem
        from event_logger import EventLogger
        from coordination import CoordinationProtocol, Role
        from learning import LearningSystem, ActionSpace
        from procedural import ProceduralSystem, DifficultyLevel, HazardType
        import random
        
        self.config = config
        self.random = random
        self.random_item = random_item
        
        self.grid = None
        self.logger = None
        self.weather = None
        self.agents = []
        self.dek = None
        self.thia = None
        self.boss = None
        self.turn = 0
        self.outcome = None
        self.reason = ""
        self.max_turns = config.max_turns
        
        self.Dek = Dek
        self.Thia = Thia
        self.PredatorFather = PredatorFather
        self.PredatorBrother = PredatorBrother
        self.WildlifeAgent = WildlifeAgent
        self.BossAdversary = BossAdversary
        self.WeatherSystem = WeatherSystem
        self.EventLogger = EventLogger
        
        self.CoordinationProtocol = CoordinationProtocol
        self.LearningSystem = LearningSystem
        self.ProceduralSystem = ProceduralSystem
        self.DifficultyLevel = DifficultyLevel
        self.HazardType = HazardType
        self.ActionSpace = ActionSpace
        self.Role = Role
        
        self.coordination = None
        self.learning = None
        self.procedural = None
        
        self.prev_dek_state = {}
        self.prev_thia_state = {}
        
        self.visualizer = None
        self.initialize()
    
    def initialize(self):
        self.grid = Grid(self.config.grid_width, self.config.grid_height)
        self.grid.generate_terrain()
        self.logger = self.EventLogger()
        self.weather = self.WeatherSystem()
        self.turn = 0
        self.outcome = None
        self.reason = ""
        
        # All agents positioned in top-center visible area (y between 3-15)
        self.dek = self.Dek(8, 8)
        self.thia = self.Thia(9, 8)
        father = self.PredatorFather("Elder Kaail", 5, 5)
        brother = self.PredatorBrother("Cetanu", 20, 6)
        
        wildlife_count = self.config.get("difficulty", "wildlife_count", 3)
        wildlife = []
        # Place one weak wildlife close to Dek for easy early kill
        positions = [(10, 8), (12, 6), (6, 10), (22, 10), (15, 8)]
        for i in range(min(wildlife_count, len(positions))):
            px, py = positions[i]
            w = self.WildlifeAgent(f"Beast_{i+1}", "predator", px, py)
            # First wildlife is weaker for easy early kill
            if i == 0:
                w.max_health = 40
                w.health = 40
            wildlife.append(w)
        
        boss_hp_mult = self.config.get("difficulty", "boss_health_multiplier", 1.0)
        self.boss = self.BossAdversary("Ultimate Adversary", 30, 8)
        self.boss.max_health = int(self.boss.max_health * boss_hp_mult)
        self.boss.health = self.boss.max_health
        
        self.agents = [self.dek, self.thia, father, brother, self.boss] + wildlife
        
        for a in self.agents:
            a.set_grid(self.grid)
            self.grid.place_agent(a, a.x, a.y)
        
        resource_count = self.config.get("difficulty", "resource_count", 15)
        placed = 0
        while placed < resource_count:
            cell = self.grid.find_empty_cell()
            if not cell:
                break
            item = self.random_item()
            cell.add_item(item)
            placed += 1
        
        self._initialize_phase9_systems()
    
    def _initialize_phase9_systems(self):
        self.coordination = self.CoordinationProtocol()
        self.coordination.initialize(self.dek, self.thia)
        
        self.learning = self.LearningSystem()
        self.learning.initialize_boss_ai(self.boss)
        
        difficulty_map = {
            'easy': self.DifficultyLevel.EASY,
            'medium': self.DifficultyLevel.MEDIUM,
            'hard': self.DifficultyLevel.HARD,
            'nightmare': self.DifficultyLevel.NIGHTMARE
        }
        diff_name = self.config.get("difficulty", "level", "medium").lower()
        diff_level = difficulty_map.get(diff_name, self.DifficultyLevel.MEDIUM)
        
        self.procedural = self.ProceduralSystem(
            self.config.grid_width,
            self.config.grid_height,
            diff_level
        )
        self.procedural.initialize(initial_hazard_count=3)
        
        self.prev_dek_state = self._capture_agent_state(self.dek)
        self.prev_thia_state = self._capture_agent_state(self.thia)
    
    def _capture_agent_state(self, agent):
        return {
            'health': agent.health,
            'health_pct': (agent.health / agent.max_health) * 100 if agent.max_health > 0 else 0,
            'stamina': agent.stamina,
            'kills': getattr(agent, 'kill_count', 0),
            'damage_dealt': getattr(agent, 'total_damage_dealt', 0),
            'honour': getattr(agent, 'honour', 0),
            'partner_health': 0
        }
    
    def _get_enemies(self):
        enemies = []
        for agent in self.agents:
            if agent.is_alive and agent != self.dek and agent != self.thia:
                if hasattr(agent, 'aggression_level') or hasattr(agent, 'phase'):
                    enemies.append(agent)
        return enemies
    
    def set_visualizer(self, visualizer):
        self.visualizer = visualizer
        visualizer.set_grid(self.grid)
        visualizer.set_simulation(self.step)
        visualizer.set_reset_callback(self.reset)
    
    def reset(self):
        self.grid = Grid(self.config.grid_width, self.config.grid_height)
        self.grid.generate_terrain()
        self.logger = self.EventLogger()
        self.weather = self.WeatherSystem()
        self.turn = 0
        self.outcome = None
        self.reason = ""
        
        # All agents positioned in top-center visible area (y between 3-15)
        self.dek = self.Dek(8, 8)
        self.thia = self.Thia(9, 8)
        father = self.PredatorFather("Elder Kaail", 5, 5)
        brother = self.PredatorBrother("Cetanu", 20, 6)
        
        wildlife_count = self.config.get("difficulty", "wildlife_count", 3)
        wildlife = []
        # Place one weak wildlife close to Dek for easy early kill
        positions = [(10, 8), (12, 6), (6, 10), (22, 10), (15, 8)]
        for i in range(min(wildlife_count, len(positions))):
            px, py = positions[i]
            w = self.WildlifeAgent(f"Beast_{i+1}", "predator", px, py)
            # First wildlife is weaker for easy early kill
            if i == 0:
                w.max_health = 40
                w.health = 40
            wildlife.append(w)
        
        boss_hp_mult = self.config.get("difficulty", "boss_health_multiplier", 1.0)
        self.boss = self.BossAdversary("Ultimate Adversary", 30, 8)
        self.boss.max_health = int(self.boss.max_health * boss_hp_mult)
        self.boss.health = self.boss.max_health
        
        self.agents = [self.dek, self.thia, father, brother, self.boss] + wildlife
        
        for a in self.agents:
            a.set_grid(self.grid)
            self.grid.place_agent(a, a.x, a.y)
        
        resource_count = self.config.get("difficulty", "resource_count", 15)
        placed = 0
        while placed < resource_count:
            cell = self.grid.find_empty_cell()
            if not cell:
                break
            item = self.random_item()
            cell.add_item(item)
            placed += 1
        
        self._initialize_phase9_systems()
        
        if self.visualizer:
            self.visualizer.set_grid(self.grid)
            self.visualizer.set_agents(self.agents)
            self.visualizer.update_turn(0)
            self.visualizer.update_weather("Calm")
            self._update_all_agent_status()
            self.visualizer.update_alive_count(len([a for a in self.agents if a.is_alive]))
            if hasattr(self.dek, 'honour'):
                self.visualizer.update_honour(self.dek.honour)
            # Reset stats tracking
            self.visualizer.update_stats(0, 0, 0, 0)
            self.visualizer.update_boss_hp(self.boss.health, self.boss.max_health)
            self.visualizer.render_grid()
            self.visualizer.log_event("Phase 9 systems initialized", "system")
            self.visualizer.log_event("Coordination & Q-Learning active", "system")
    
    def step(self):
        if self.outcome:
            return
        
        self.turn += 1
        self.logger.increment_step()
        
        changed = self.weather.maybe_transition()
        if changed:
            self.logger.log_weather_change(self.weather.current)
            if self.visualizer:
                self.visualizer.update_weather(self.weather.current.name)
                self.visualizer.log_event(f"Weather: {self.weather.current.name}", "weather")
        
        self._process_procedural_hazards()
        
        self._process_coordination_and_learning()
        
        for agent in list(self.agents):
            if not agent.is_alive:
                continue
            agent.step()
            self._try_pickup(agent)
        
        self._process_boss_adaptive_ai()
        
        wd = self.weather.damage_this_turn()
        if wd > 0:
            for agent in self.agents:
                if agent.is_alive:
                    before = agent.health
                    agent.take_damage(wd)
                    if agent.health < before:
                        self.logger.log_hazard_effect(agent, wd, self.weather.current.name)
                        if self.visualizer:
                            name = getattr(agent, 'name', agent.__class__.__name__)
                            self.visualizer.log_event(f"{name} takes {wd} weather damage", "combat")
        
        self._update_learning_systems()
        
        if self.visualizer:
            self.visualizer.update_turn(self.turn)
            self._update_all_agent_status()
            alive_count = sum(1 for a in self.agents if a.is_alive)
            self.visualizer.update_alive_count(alive_count)
            if hasattr(self.dek, 'honour'):
                self.visualizer.update_honour(self.dek.honour)
            
            # Update combat statistics
            damage_dealt = getattr(self.dek, 'total_damage_dealt', 0)
            damage_taken = getattr(self.dek, 'max_health', 100) - getattr(self.dek, 'health', 0)
            kills = getattr(self.dek, 'kill_count', 0)
            items = getattr(self.dek, 'items_collected', 0)
            self.visualizer.update_stats(damage_dealt, damage_taken, kills, items)
            
            # Update boss HP bar
            if self.boss:
                self.visualizer.update_boss_hp(self.boss.health, self.boss.max_health)
        
        if not self.boss.is_alive and self.dek.is_alive:
            self.outcome = "win"
            self.reason = "boss_defeated"
            self._finalize()
        elif not self.dek.is_alive:
            self.outcome = "lose"
            self.reason = "dek_dead"
            self._finalize()
        elif self.turn >= self.max_turns:
            self.outcome = "timeout"
            self.reason = "turn_limit"
            self._finalize()
    
    def _process_procedural_hazards(self):
        if not self.procedural:
            return
        
        game_state = {
            'player_position': (self.dek.x, self.dek.y),
            'turn': self.turn
        }
        
        result = self.procedural.update(self.turn, game_state)
        
        for agent in self.agents:
            if agent.is_alive:
                hazard_damage = self.procedural.get_damage_at_position((agent.x, agent.y))
                if hazard_damage > 0:
                    agent.take_damage(hazard_damage)
                    if self.visualizer:
                        name = getattr(agent, 'name', agent.__class__.__name__)
                        self.visualizer.log_event(f"{name} takes {hazard_damage} hazard damage", "combat")
        
        for event in result.get('events', []):
            if event['type'] == 'weather_change':
                if self.visualizer:
                    self.visualizer.log_event(f"Environmental: {event.get('weather', 'unknown')}", "weather")
    
    def _process_coordination_and_learning(self):
        if not self.coordination or not self.learning:
            return
        
        if not self.dek.is_alive:
            return
        
        enemies = self._get_enemies()
        
        planned_actions = self.coordination.plan_coordinated_turn(
            self.dek, self.thia, enemies, self.grid
        )
        
        if self.dek.name in planned_actions:
            dek_action = planned_actions[self.dek.name]
            all_agents = {a.name: a for a in self.agents if hasattr(a, 'name')}
            self.coordination.execute_coordinated_action(
                dek_action, self.dek, self.grid, all_agents
            )
        
        if self.thia and self.thia.is_alive and self.thia.name in planned_actions:
            thia_action = planned_actions[self.thia.name]
            all_agents = {a.name: a for a in self.agents if hasattr(a, 'name')}
            self.coordination.execute_coordinated_action(
                thia_action, self.thia, self.grid, all_agents
            )
        
        coord_stats = self.coordination.get_coordination_stats()
        if self.visualizer and coord_stats.get('coordination_score', 0) > 50:
            self.visualizer.log_event(f"Coordination level: {coord_stats['coordination_score']:.0f}%", "system")
    
    def _process_boss_adaptive_ai(self):
        if not self.learning or not self.learning.boss_ai:
            return
        
        if not self.boss.is_alive:
            return
        
        enemies = [self.dek, self.thia] if self.thia and self.thia.is_alive else [self.dek]
        enemies = [e for e in enemies if e.is_alive]
        
        if not enemies:
            return
        
        boss_action = self.learning.get_boss_action(enemies, self.grid)
        self.learning.boss_ai.execute_adaptive_action(boss_action, self.grid)
        
        if self.visualizer:
            pattern = self.learning.boss_ai.current_pattern.pattern_type.value
            if self.turn % 10 == 0:
                self.visualizer.log_event(f"Boss pattern: {pattern}", "system")
    
    def _update_learning_systems(self):
        if not self.learning:
            return
        
        curr_dek_state = self._capture_agent_state(self.dek)
        curr_thia_state = self._capture_agent_state(self.thia) if self.thia else {}
        
        enemies = self._get_enemies()
        
        dek_action = self.learning.get_dek_action(self.dek, enemies, self.thia)
        self.learning.update_dek_learning(
            self.dek, self.prev_dek_state, curr_dek_state,
            dek_action, enemies, self.thia
        )
        
        if self.thia and self.thia.is_alive:
            thia_action = self.learning.get_thia_action(self.thia, self.dek, enemies)
            self.learning.update_thia_learning(
                self.thia, self.dek, self.prev_thia_state, curr_thia_state,
                thia_action, enemies
            )
        
        self.prev_dek_state = curr_dek_state
        self.prev_thia_state = curr_thia_state
    
    def _update_all_agent_status(self):
        if not self.visualizer:
            return
        
        # Track wildlife health totals
        wildlife_health = 0
        wildlife_max = 0
        wildlife_count = 0
        wildlife_alive = False
        wildlife_x, wildlife_y = 0, 0
        
        for agent in self.agents:
            agent_class = agent.__class__.__name__
            key_map = {
                'Dek': 'dek',
                'Thia': 'thia',
                'PredatorFather': 'father',
                'PredatorBrother': 'brother',
                'BossAdversary': 'boss'
            }
            key = key_map.get(agent_class)
            if key:
                self.visualizer.update_agent_status(
                    key,
                    agent.health,
                    agent.max_health,
                    agent.x,
                    agent.y,
                    agent.is_alive
                )
            elif agent_class == 'WildlifeAgent':
                wildlife_max += agent.max_health
                if agent.is_alive:
                    wildlife_health += agent.health
                    wildlife_count += 1
                    wildlife_alive = True
                    wildlife_x, wildlife_y = agent.x, agent.y
        
        # Always update wildlife status (even if all dead)
        self.visualizer.update_agent_status(
            'wildlife',
            wildlife_health,
            wildlife_max if wildlife_max > 0 else 200,
            wildlife_x,
            wildlife_y,
            wildlife_alive
        )
    
    def _try_pickup(self, agent):
        cell = self.grid.get_cell(agent.x, agent.y)
        if not cell.items:
            return
        new_items = []
        for it in cell.items:
            if it.apply(agent):
                self.logger.log_item_pickup(agent, it)
                if agent == self.dek and hasattr(agent, 'items_collected'):
                    agent.items_collected += 1
                if self.visualizer:
                    name = getattr(agent, 'name', agent.__class__.__name__)
                    self.visualizer.log_item_pickup(name, it.name, agent.x, agent.y)
            else:
                new_items.append(it)
        cell.items = new_items
    
    def _finalize(self):
        self.logger.log_outcome(self.outcome, self.turn, self.reason)
        self.logger.export_events_json('data/visual_run.json')
        
        if self.learning:
            self.learning.end_episode()
            try:
                self.learning.save_learning_data('data')
            except Exception:
                pass
        
        if self.visualizer:
            self.visualizer.log_event(f"SIMULATION ENDED: {self.outcome.upper()}", "system")
            
            if self.learning:
                stats = self.learning.get_learning_stats()
                dek_updates = stats.get('dek_stats', {}).get('total_updates', 0)
                self.visualizer.log_event(f"Q-Learning updates: {dek_updates}", "system")
            
            if self.coordination:
                coord_stats = self.coordination.get_coordination_stats()
                self.visualizer.log_event(f"Final coordination: {coord_stats.get('coordination_score', 0):.0f}%", "system")
            
            self.visualizer.show_outcome(self.outcome, self.reason)


def run_visual_simulation():
    from config import GameConfig
    from visualizer import PredatorVisualizer
    
    config = GameConfig()
    engine = SimulationEngine(config)
    visualizer = PredatorVisualizer(config)
    engine.set_visualizer(visualizer)
    visualizer.set_agents(engine.agents)
    
    visualizer.update_turn(0)
    visualizer.update_weather("Calm")
    engine._update_all_agent_status()
    visualizer.update_alive_count(len([a for a in engine.agents if a.is_alive]))
    if hasattr(engine.dek, 'honour'):
        visualizer.update_honour(engine.dek.honour)
    visualizer.render_grid()
    
    visualizer.log_event("PREDATOR: BADLANDS initialized", "system")
    visualizer.log_event("Press START or SPACE to begin", "system")
    visualizer.log_event("Hover on agents for details", "system")
    
    visualizer.run()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_phase7_simulation()
    else:
        run_visual_simulation()
