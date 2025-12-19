import json
from datetime import datetime
from collections import defaultdict


class EventLogger:
    
    def __init__(self):
        self.events = []
        self.step_counter = 0
        self.statistics = defaultdict(int)
        self.agent_stats = defaultdict(lambda: defaultdict(int))
        
    def log_event(self, event_type, agent, details=None):
        event = {
            'timestamp': self.step_counter,
            'type': event_type,
            'agent': agent.name if agent else 'system',
            'position': (agent.x, agent.y) if agent else None,
            'details': details or {}
        }
        
        self.events.append(event)
        self.statistics[event_type] += 1
        
        if agent:
            self.agent_stats[agent.name][event_type] += 1
    
    def log_action(self, agent, action_result):
        details = action_result.to_dict()
        self.log_event('action', agent, details)
        
        if action_result.combat_result:
            self.log_combat(agent, action_result.combat_result)
        
        if action_result.trophy_collected:
            self.log_trophy(agent, action_result.trophy_collected)
        
        if action_result.stamina_cost > 0:
            self.log_stamina_change(agent, -action_result.stamina_cost)
    
    def log_combat(self, agent, combat_result):
        details = combat_result.to_dict()
        self.log_event('combat', agent, details)
        
        if combat_result.kill:
            self.log_event('kill', agent, {
                'victim': combat_result.defender.name,
                'damage': combat_result.damage_dealt
            })
    
    def log_trophy(self, agent, trophy):
        details = trophy.to_dict()
        self.log_event('trophy_collected', agent, details)
    
    def log_stamina_change(self, agent, change):
        self.log_event('stamina_change', agent, {
            'change': change,
            'current_stamina': agent.stamina,
            'percentage': agent.stamina_percentage
        })
    
    def log_health_change(self, agent, change, cause="unknown"):
        self.log_event('health_change', agent, {
            'change': change,
            'cause': cause,
            'current_health': agent.health,
            'percentage': agent.health_percentage
        })
    
    def log_honour_change(self, agent, change, reason=""):
        if hasattr(agent, 'honour'):
            self.log_event('honour_change', agent, {
                'change': change,
                'reason': reason,
                'current_honour': agent.honour,
                'clan_rank': agent.clan_rank
            })
    
    def log_clan_reaction(self, judge_agent, target_agent, reaction):
        self.log_event('clan_reaction', judge_agent, {
            'target': target_agent.name,
            'relationship': reaction.relationship.value,
            'opinion_change': reaction.opinion_change,
            'message': reaction.message
        })
    
    def log_death(self, agent, killer=None):
        details = {'cause': 'combat' if killer else 'unknown'}
        if killer:
            details['killer'] = killer.name
        
        self.log_event('death', agent, details)
    
    def increment_step(self):
        self.step_counter += 1
    
    def get_events_by_type(self, event_type):
        return [e for e in self.events if e['type'] == event_type]
    
    def get_agent_events(self, agent_name):
        return [e for e in self.events if e['agent'] == agent_name]
    
    def get_combat_statistics(self):
        combats = self.get_events_by_type('combat')
        kills = self.get_events_by_type('kill')
        
        stats = {
            'total_combats': len(combats),
            'total_kills': len(kills),
            'average_damage': 0,
            'kills_by_agent': defaultdict(int),
            'damage_by_agent': defaultdict(list)
        }
        
        total_damage = 0
        for combat in combats:
            damage = combat['details'].get('damage', 0)
            total_damage += damage
            agent = combat['agent']
            stats['damage_by_agent'][agent].append(damage)
        
        if combats:
            stats['average_damage'] = total_damage / len(combats)
        
        for kill in kills:
            killer = kill['agent']
            stats['kills_by_agent'][killer] += 1
        
        return stats
    
    def get_stamina_statistics(self):
        stamina_events = self.get_events_by_type('stamina_change')
        
        stats = {
            'total_stamina_spent': 0,
            'stamina_by_agent': defaultdict(int),
            'actions_by_cost': defaultdict(int)
        }
        
        for event in stamina_events:
            change = event['details']['change']
            if change < 0:
                stats['total_stamina_spent'] += abs(change)
                stats['stamina_by_agent'][event['agent']] += abs(change)
        
        action_events = self.get_events_by_type('action')
        for event in action_events:
            cost = event['details'].get('stamina_cost', 0)
            action_type = event['details'].get('action', 'unknown')
            if cost > 0:
                stats['actions_by_cost'][f"{action_type}({cost})"] += 1
        
        return stats
    
    def get_honour_progression(self, agent_name):
        honour_events = [e for e in self.get_agent_events(agent_name) if e['type'] == 'honour_change']
        
        progression = []
        current_honour = 0
        
        for event in honour_events:
            current_honour += event['details']['change']
            progression.append({
                'timestamp': event['timestamp'],
                'honour': current_honour,
                'change': event['details']['change'],
                'reason': event['details']['reason']
            })
        
        return progression
    
    def get_trophy_collection_summary(self):
        trophy_events = self.get_events_by_type('trophy_collected')
        
        summary = {
            'total_trophies': len(trophy_events),
            'trophies_by_agent': defaultdict(list),
            'trophy_types': defaultdict(int),
            'total_honour_value': 0
        }
        
        for event in trophy_events:
            trophy_data = event['details']
            agent = event['agent']
            trophy_type = trophy_data.get('type', 'unknown')
            honour_value = trophy_data.get('honour_value', 0)
            
            summary['trophies_by_agent'][agent].append(trophy_data)
            summary['trophy_types'][trophy_type] += 1
            summary['total_honour_value'] += honour_value
        
        return summary
    
    def export_events_json(self, filename):
        export_data = {
            'metadata': {
                'total_steps': self.step_counter,
                'total_events': len(self.events),
                'export_time': datetime.now().isoformat()
            },
            'statistics': dict(self.statistics),
            'agent_statistics': dict(self.agent_stats),
            'events': self.events
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def get_simulation_summary(self):
        return {
            'total_steps': self.step_counter,
            'total_events': len(self.events),
            'event_breakdown': dict(self.statistics),
            'combat_stats': self.get_combat_statistics(),
            'stamina_stats': self.get_stamina_statistics(),
            'trophy_summary': self.get_trophy_collection_summary()
        }