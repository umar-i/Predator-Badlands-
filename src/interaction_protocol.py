from enum import Enum


class InteractionType(Enum):
    INFO_REQUEST = "info_request"
    INFO_SHARE = "info_share"
    ALLIANCE_PROPOSAL = "alliance_proposal"
    THREAT_WARNING = "threat_warning"
    RESOURCE_TRADE = "resource_trade"
    ASSISTANCE_REQUEST = "assistance_request"
    HOSTILE_CHALLENGE = "hostile_challenge"


class InteractionProtocol:
    
    def __init__(self, initiator, target, interaction_type, data=None):
        self.initiator = initiator
        self.target = target
        self.interaction_type = interaction_type
        self.data = data or {}
        self.success = False
        self.response = None
        self.trust_change = 0
    
    def execute(self):
        if not self.can_interact():
            self.response = "Interaction blocked - insufficient trust or hostile relationship"
            return self
        
        if self.interaction_type == InteractionType.INFO_REQUEST:
            return self.handle_info_request()
        elif self.interaction_type == InteractionType.INFO_SHARE:
            return self.handle_info_share()
        elif self.interaction_type == InteractionType.ALLIANCE_PROPOSAL:
            return self.handle_alliance_proposal()
        elif self.interaction_type == InteractionType.THREAT_WARNING:
            return self.handle_threat_warning()
        elif self.interaction_type == InteractionType.ASSISTANCE_REQUEST:
            return self.handle_assistance_request()
        elif self.interaction_type == InteractionType.HOSTILE_CHALLENGE:
            return self.handle_hostile_challenge()
        
        self.response = "Unknown interaction type"
        return self
    
    def can_interact(self):
        distance = self.initiator.distance_to(self.target)
        if distance > 3:
            return False
        
        if hasattr(self.initiator, 'trust_in_dek') and hasattr(self.target, 'name'):
            if self.target.name == "Dek" and self.initiator.trust_in_dek < 20:
                return False
        
        if hasattr(self.target, 'hostile') and self.target.hostile:
            return self.interaction_type == InteractionType.HOSTILE_CHALLENGE
        
        return True
    
    def handle_info_request(self):
        topic = self.data.get('topic', '')
        
        if hasattr(self.target, 'provide_intel'):
            intel = self.target.provide_intel(topic, self.initiator)
            if intel:
                self.success = True
                self.response = intel
                self.trust_change = 1
            else:
                self.response = "Information not available or access denied"
        else:
            self.response = "Target cannot provide information"
        
        return self
    
    def handle_info_share(self):
        if not hasattr(self.target, 'add_knowledge'):
            self.response = "Target cannot receive information"
            return self
        
        info_key = self.data.get('key', '')
        info_value = self.data.get('value', '')
        
        self.target.add_knowledge(info_key, info_value)
        self.success = True
        self.response = f"Shared information: {info_key}"
        self.trust_change = 2
        
        return self
    
    def handle_alliance_proposal(self):
        if hasattr(self.target, 'trust_in_dek'):
            if self.target.trust_in_dek >= 50:
                self.success = True
                self.response = "Alliance accepted"
                self.trust_change = 5
            else:
                self.response = "Alliance rejected - insufficient trust"
                self.trust_change = -2
        else:
            self.response = "Target cannot form alliances"
        
        return self
    
    def handle_threat_warning(self):
        threat_data = self.data.get('threat', {})
        
        if hasattr(self.target, 'build_trust'):
            self.target.build_trust(3)
            self.success = True
            self.response = f"Warning acknowledged: {threat_data.get('description', 'Unknown threat')}"
            self.trust_change = 3
        else:
            self.response = "Warning noted"
            self.success = True
        
        return self
    
    def handle_assistance_request(self):
        assistance_type = self.data.get('type', 'general')
        
        if hasattr(self.target, 'cooperation_level'):
            if self.target.cooperation_level >= 3:
                self.success = True
                self.response = f"Assistance provided: {assistance_type}"
                self.trust_change = 2
            else:
                self.response = "Assistance denied - insufficient cooperation"
        else:
            self.response = "Target cannot provide assistance"
        
        return self
    
    def handle_hostile_challenge(self):
        self.success = True
        self.response = "Challenge accepted - prepare for combat"
        self.trust_change = -5
        return self


class SyntheticInteractionManager:
    
    def __init__(self):
        self.active_alliances = {}
        self.information_exchanges = []
        self.trust_network = {}
    
    def initiate_interaction(self, initiator, target, interaction_type, data=None):
        protocol = InteractionProtocol(initiator, target, interaction_type, data)
        result = protocol.execute()
        
        if result.success and result.trust_change != 0:
            self.update_trust_network(initiator, target, result.trust_change)
        
        self.information_exchanges.append({
            'initiator': initiator.name,
            'target': target.name,
            'type': interaction_type.value,
            'success': result.success,
            'response': result.response
        })
        
        return result
    
    def update_trust_network(self, agent1, agent2, trust_change):
        key1 = f"{agent1.name}->{agent2.name}"
        key2 = f"{agent2.name}->{agent1.name}"
        
        self.trust_network[key1] = self.trust_network.get(key1, 0) + trust_change
        
        if hasattr(agent1, 'build_trust') and trust_change > 0:
            agent1.build_trust(abs(trust_change))
        elif hasattr(agent1, 'lose_trust') and trust_change < 0:
            agent1.lose_trust(abs(trust_change))
        
        if hasattr(agent2, 'build_trust') and trust_change > 0:
            agent2.build_trust(abs(trust_change))
        elif hasattr(agent2, 'lose_trust') and trust_change < 0:
            agent2.lose_trust(abs(trust_change))
    
    def form_alliance(self, agent1, agent2):
        alliance_key = tuple(sorted([agent1.name, agent2.name]))
        
        if alliance_key not in self.active_alliances:
            self.active_alliances[alliance_key] = {
                'members': [agent1.name, agent2.name],
                'formed_at': 0,
                'strength': 1
            }
            return True
        
        return False
    
    def check_alliance(self, agent1, agent2):
        alliance_key = tuple(sorted([agent1.name, agent2.name]))
        return alliance_key in self.active_alliances
    
    def get_trust_level(self, agent1, agent2):
        key = f"{agent1.name}->{agent2.name}"
        return self.trust_network.get(key, 0)
    
    def broadcast_information(self, broadcaster, info_key, info_value, max_range=5):
        if not hasattr(broadcaster, 'grid') or not broadcaster.grid:
            return []
        
        recipients = []
        nearby_cells = broadcaster.grid.get_cells_in_radius(
            broadcaster.x, broadcaster.y, max_range
        )
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != broadcaster:
                target = cell.occupant
                if hasattr(target, 'add_knowledge'):
                    result = self.initiate_interaction(
                        broadcaster, target, 
                        InteractionType.INFO_SHARE,
                        {'key': info_key, 'value': info_value}
                    )
                    recipients.append((target.name, result.success))
        
        return recipients
    
    def get_interaction_history(self, agent_name=None):
        if agent_name:
            return [
                exchange for exchange in self.information_exchanges
                if exchange['initiator'] == agent_name or exchange['target'] == agent_name
            ]
        return self.information_exchanges
    
    def get_alliance_summary(self):
        return {
            'total_alliances': len(self.active_alliances),
            'alliances': list(self.active_alliances.keys()),
            'trust_relationships': len(self.trust_network)
        }