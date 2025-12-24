import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from weather import WeatherState, WeatherSystem
from event_logger import EventLogger
from predator import PredatorAgent


class TestWeatherState(unittest.TestCase):
    
    def test_weather_state_creation(self):
        state = WeatherState("TestWeather", 1.5, 2, 1)
        
        self.assertEqual(state.name, "TestWeather")
        self.assertEqual(state.move_multiplier, 1.5)
        self.assertEqual(state.global_damage, 2)
        self.assertEqual(state.visibility_penalty, 1)


class TestWeatherSystem(unittest.TestCase):
    
    def test_weather_system_creation(self):
        system = WeatherSystem(seed=42)
        
        self.assertIsNotNone(system.current)
        self.assertEqual(system.turns_in_state, 0)
    
    def test_initial_weather_calm(self):
        system = WeatherSystem(seed=42)
        
        self.assertEqual(system.current.name, "Calm")
    
    def test_calm_weather_properties(self):
        system = WeatherSystem()
        system.current = system._calm()
        
        self.assertEqual(system.current.move_multiplier, 1.0)
        self.assertEqual(system.current.global_damage, 0)
        self.assertEqual(system.current.visibility_penalty, 0)
    
    def test_sandstorm_properties(self):
        system = WeatherSystem()
        system.current = system._sandstorm()
        
        self.assertEqual(system.current.name, "Sandstorm")
        self.assertEqual(system.current.move_multiplier, 1.3)
        self.assertEqual(system.current.visibility_penalty, 2)
    
    def test_acid_rain_properties(self):
        system = WeatherSystem()
        system.current = system._acid_rain()
        
        self.assertEqual(system.current.name, "AcidRain")
        self.assertEqual(system.current.move_multiplier, 1.1)
        self.assertEqual(system.current.global_damage, 3)
    
    def test_electrical_storm_properties(self):
        system = WeatherSystem()
        system.current = system._electrical_storm()
        
        self.assertEqual(system.current.name, "ElectricalStorm")
        self.assertEqual(system.current.move_multiplier, 1.2)
        self.assertEqual(system.current.global_damage, 1)
        self.assertEqual(system.current.visibility_penalty, 1)
    
    def test_maybe_transition_increments_turns(self):
        system = WeatherSystem(seed=12345)
        initial_turns = system.turns_in_state
        
        system.maybe_transition()
        
        self.assertGreaterEqual(system.turns_in_state, 0)
    
    def test_movement_cost_multiplier(self):
        system = WeatherSystem()
        system.current = system._sandstorm()
        
        multiplier = system.movement_cost_multiplier()
        self.assertEqual(multiplier, 1.3)
    
    def test_damage_this_turn_calm(self):
        system = WeatherSystem()
        system.current = system._calm()
        
        damage = system.damage_this_turn()
        self.assertEqual(damage, 0)
    
    def test_damage_this_turn_acid_rain(self):
        system = WeatherSystem()
        system.current = system._acid_rain()
        
        damage = system.damage_this_turn()
        self.assertEqual(damage, 3)
    
    def test_visibility_penalty_method(self):
        system = WeatherSystem()
        system.current = system._sandstorm()
        
        penalty = system.visibility_penalty()
        self.assertEqual(penalty, 2)
    
    def test_weather_transition_resets_turns(self):
        system = WeatherSystem(seed=1)
        
        for _ in range(100):
            if system.maybe_transition():
                self.assertEqual(system.turns_in_state, 0)
                break


class TestEventLogger(unittest.TestCase):
    
    def test_logger_creation(self):
        logger = EventLogger()
        
        self.assertEqual(logger.events, [])
        self.assertEqual(logger.step_counter, 0)
    
    def test_increment_step(self):
        logger = EventLogger()
        
        logger.increment_step()
        logger.increment_step()
        
        self.assertEqual(logger.step_counter, 2)
    
    def test_log_event(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        predator.x = 5
        predator.y = 10
        
        logger.log_event('test_event', predator, {'key': 'value'})
        
        self.assertEqual(len(logger.events), 1)
        event = logger.events[0]
        self.assertEqual(event['type'], 'test_event')
        self.assertEqual(event['agent'], 'Hunter')
        self.assertEqual(event['position'], (5, 10))
        self.assertEqual(event['details']['key'], 'value')
    
    def test_log_event_statistics(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        logger.log_event('combat', predator)
        logger.log_event('combat', predator)
        logger.log_event('movement', predator)
        
        self.assertEqual(logger.statistics['combat'], 2)
        self.assertEqual(logger.statistics['movement'], 1)
    
    def test_log_event_agent_stats(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        logger.log_event('combat', predator)
        logger.log_event('combat', predator)
        
        self.assertEqual(logger.agent_stats['Hunter']['combat'], 2)
    
    def test_log_event_no_agent(self):
        logger = EventLogger()
        
        logger.log_event('system_event', None, {'message': 'System startup'})
        
        event = logger.events[0]
        self.assertEqual(event['agent'], 'system')
        self.assertIsNone(event['position'])
    
    def test_log_health_change(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        predator.health = 80
        
        logger.log_health_change(predator, -20, "combat")
        
        event = logger.events[0]
        self.assertEqual(event['type'], 'health_change')
        self.assertEqual(event['details']['change'], -20)
        self.assertEqual(event['details']['cause'], "combat")
    
    def test_log_stamina_change(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        predator.stamina = 90
        
        logger.log_stamina_change(predator, -10)
        
        event = logger.events[0]
        self.assertEqual(event['type'], 'stamina_change')
        self.assertEqual(event['details']['change'], -10)
    
    def test_log_honour_change(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        predator.honour = 30
        
        logger.log_honour_change(predator, 10, "worthy kill")
        
        event = logger.events[0]
        self.assertEqual(event['type'], 'honour_change')
        self.assertEqual(event['details']['change'], 10)
        self.assertEqual(event['details']['reason'], "worthy kill")
    
    def test_log_death(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        killer = PredatorAgent("Killer")
        
        logger.log_death(predator, killer)
        
        event = logger.events[0]
        self.assertEqual(event['type'], 'death')
        self.assertEqual(event['details']['cause'], 'combat')
        self.assertEqual(event['details']['killer'], 'Killer')
    
    def test_log_death_no_killer(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        logger.log_death(predator)
        
        event = logger.events[0]
        self.assertEqual(event['details']['cause'], 'unknown')
        self.assertNotIn('killer', event['details'])
    
    def test_get_events_by_type(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        logger.log_event('combat', predator)
        logger.log_event('movement', predator)
        logger.log_event('combat', predator)
        logger.log_event('rest', predator)
        
        combat_events = logger.get_events_by_type('combat')
        
        self.assertEqual(len(combat_events), 2)


class TestEventLoggerCombat(unittest.TestCase):
    
    def test_log_combat(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        class MockCombatResult:
            def __init__(self):
                self.attacker = predator
                self.defender = PredatorAgent("Target")
                self.damage_dealt = 25
                self.kill = False
            
            def to_dict(self):
                return {
                    'attacker': self.attacker.name,
                    'defender': self.defender.name,
                    'damage': self.damage_dealt,
                    'kill': self.kill
                }
        
        combat_result = MockCombatResult()
        logger.log_combat(predator, combat_result)
        
        combat_events = logger.get_events_by_type('combat')
        self.assertEqual(len(combat_events), 1)
    
    def test_log_combat_with_kill(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        class MockCombatResult:
            def __init__(self):
                self.attacker = predator
                self.defender = PredatorAgent("Victim")
                self.damage_dealt = 100
                self.kill = True
            
            def to_dict(self):
                return {
                    'attacker': self.attacker.name,
                    'defender': self.defender.name,
                    'damage': self.damage_dealt,
                    'kill': self.kill
                }
        
        combat_result = MockCombatResult()
        logger.log_combat(predator, combat_result)
        
        kill_events = logger.get_events_by_type('kill')
        self.assertEqual(len(kill_events), 1)


class TestEventLoggerTrophy(unittest.TestCase):
    
    def test_log_trophy(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        class MockTrophy:
            def to_dict(self):
                return {
                    'name': 'Beast Skull',
                    'type': 'skull',
                    'value': 10
                }
        
        trophy = MockTrophy()
        logger.log_trophy(predator, trophy)
        
        trophy_events = logger.get_events_by_type('trophy_collected')
        self.assertEqual(len(trophy_events), 1)
        self.assertEqual(trophy_events[0]['details']['name'], 'Beast Skull')


class TestEventLoggerClanReaction(unittest.TestCase):
    
    def test_log_clan_reaction(self):
        logger = EventLogger()
        judge = PredatorAgent("Elder")
        target = PredatorAgent("Hunter")
        
        from clan_code import ClanReaction, ClanRelationship
        reaction = ClanReaction(
            ClanRelationship.FATHER,
            10,
            "Father approves"
        )
        
        logger.log_clan_reaction(judge, target, reaction)
        
        reaction_events = logger.get_events_by_type('clan_reaction')
        self.assertEqual(len(reaction_events), 1)


class TestEventLoggerAction(unittest.TestCase):
    
    def test_log_action(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        predator.stamina = 90
        
        from actions import ActionResult, ActionType
        action_result = ActionResult(ActionType.MOVE, True, 10, "Moved successfully")
        
        logger.log_action(predator, action_result)
        
        action_events = logger.get_events_by_type('action')
        self.assertEqual(len(action_events), 1)
    
    def test_log_action_with_stamina(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        predator.stamina = 90
        
        from actions import ActionResult, ActionType
        action_result = ActionResult(ActionType.ATTACK, True, 15)
        
        logger.log_action(predator, action_result)
        
        stamina_events = logger.get_events_by_type('stamina_change')
        self.assertEqual(len(stamina_events), 1)


class TestWeatherSystemWithSeed(unittest.TestCase):
    
    def test_deterministic_with_seed(self):
        system1 = WeatherSystem(seed=42)
        system2 = WeatherSystem(seed=42)
        
        transitions1 = []
        transitions2 = []
        
        for _ in range(20):
            transitions1.append(system1.maybe_transition())
            transitions2.append(system2.maybe_transition())
        
        self.assertEqual(transitions1, transitions2)
    
    def test_different_seeds_different_results(self):
        system1 = WeatherSystem(seed=42)
        system2 = WeatherSystem(seed=123)
        
        results1 = []
        results2 = []
        
        for _ in range(50):
            system1.maybe_transition()
            system2.maybe_transition()
            results1.append(system1.current.name)
            results2.append(system2.current.name)
        
        self.assertNotEqual(results1, results2)


class TestEventLoggerIntegration(unittest.TestCase):
    
    def test_multiple_agents_tracking(self):
        logger = EventLogger()
        
        predator1 = PredatorAgent("Hunter1")
        predator2 = PredatorAgent("Hunter2")
        
        logger.log_event('combat', predator1)
        logger.log_event('combat', predator1)
        logger.log_event('movement', predator2)
        logger.log_event('rest', predator2)
        logger.log_event('combat', predator2)
        
        self.assertEqual(logger.agent_stats['Hunter1']['combat'], 2)
        self.assertEqual(logger.agent_stats['Hunter2']['combat'], 1)
        self.assertEqual(logger.agent_stats['Hunter2']['movement'], 1)
    
    def test_event_timestamp(self):
        logger = EventLogger()
        predator = PredatorAgent("Hunter")
        
        logger.increment_step()
        logger.increment_step()
        logger.log_event('test', predator)
        
        event = logger.events[0]
        self.assertEqual(event['timestamp'], 2)


if __name__ == '__main__':
    unittest.main()
