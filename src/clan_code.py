from enum import Enum


class ClanCodeViolation(Enum):
    HUNT_UNWORTHY = "hunting_unworthy"
    UNFAIR_ADVANTAGE = "unfair_advantage"
    TERRITORY_VIOLATION = "territory_violation"
    TROPHY_THEFT = "trophy_theft"
    HARM_INNOCENT = "harm_innocent"
    COWARDICE = "cowardice"
    DISHONOUR_CLAN = "dishonour_clan"
    ABANDON_ALLY = "abandon_ally"
    EXCESSIVE_FORCE = "excessive_force"
    RETREAT_FROM_WORTHY = "retreat_from_worthy"


class HonourableAction(Enum):
    WORTHY_KILL = "worthy_kill"
    PROTECT_ALLY = "protect_ally"
    FACE_SUPERIOR_FOE = "face_superior_foe"
    COMPLETE_TRIAL = "complete_trial"
    DEFEAT_BOSS = "defeat_boss"
    SAVE_THIA = "save_thia"
    HONOURABLE_COMBAT = "honourable_combat"
    CLAN_SERVICE = "clan_service"
    TROPHY_OFFERING = "trophy_offering"
    SELF_SACRIFICE = "self_sacrifice"


class ClanCodeRule:
    
    def __init__(self, rule_type, description, honour_penalty, severity="medium"):
        self.rule_type = rule_type
        self.description = description
        self.honour_penalty = honour_penalty
        self.severity = severity
    
    def apply_penalty(self, predator):
        predator.lose_honour(self.honour_penalty)
        return f"Violated {self.rule_type.value}: -{self.honour_penalty} honour"


class HonourReward:
    
    def __init__(self, action_type, description, honour_gain, reputation_gain=0):
        self.action_type = action_type
        self.description = description
        self.honour_gain = honour_gain
        self.reputation_gain = reputation_gain
    
    def apply_reward(self, predator):
        predator.gain_honour(self.honour_gain)
        if hasattr(predator, 'reputation'):
            predator.reputation += self.reputation_gain
        return f"Honourable: {self.action_type.value}: +{self.honour_gain} honour"


class YautjaClanCode:
    
    RULES = {
        ClanCodeViolation.HUNT_UNWORTHY: ClanCodeRule(
            ClanCodeViolation.HUNT_UNWORTHY,
            "Only hunt creatures capable of defending themselves",
            15,
            "high"
        ),
        ClanCodeViolation.UNFAIR_ADVANTAGE: ClanCodeRule(
            ClanCodeViolation.UNFAIR_ADVANTAGE,
            "Give prey a fighting chance, fight on equal terms",
            10,
            "medium"
        ),
        ClanCodeViolation.TERRITORY_VIOLATION: ClanCodeRule(
            ClanCodeViolation.TERRITORY_VIOLATION,
            "Do not hunt in another's territory without permission",
            20,
            "high"
        ),
        ClanCodeViolation.TROPHY_THEFT: ClanCodeRule(
            ClanCodeViolation.TROPHY_THEFT,
            "Never take another hunter's trophy",
            25,
            "severe"
        ),
        ClanCodeViolation.HARM_INNOCENT: ClanCodeRule(
            ClanCodeViolation.HARM_INNOCENT,
            "Do not harm pregnant, young, sick, or defenseless",
            30,
            "severe"
        ),
        ClanCodeViolation.COWARDICE: ClanCodeRule(
            ClanCodeViolation.COWARDICE,
            "Face death with honour rather than flee",
            12,
            "medium"
        ),
        ClanCodeViolation.DISHONOUR_CLAN: ClanCodeRule(
            ClanCodeViolation.DISHONOUR_CLAN,
            "Actions must reflect honour upon the clan",
            18,
            "high"
        ),
        ClanCodeViolation.ABANDON_ALLY: ClanCodeRule(
            ClanCodeViolation.ABANDON_ALLY,
            "Never abandon an ally in battle",
            22,
            "high"
        ),
        ClanCodeViolation.EXCESSIVE_FORCE: ClanCodeRule(
            ClanCodeViolation.EXCESSIVE_FORCE,
            "Use only necessary force against weaker foes",
            8,
            "low"
        ),
        ClanCodeViolation.RETREAT_FROM_WORTHY: ClanCodeRule(
            ClanCodeViolation.RETREAT_FROM_WORTHY,
            "Never retreat from a worthy opponent",
            15,
            "high"
        )
    }
    
    REWARDS = {
        HonourableAction.WORTHY_KILL: HonourReward(
            HonourableAction.WORTHY_KILL,
            "Defeated a worthy opponent in fair combat",
            10,
            5
        ),
        HonourableAction.PROTECT_ALLY: HonourReward(
            HonourableAction.PROTECT_ALLY,
            "Protected an ally from harm",
            8,
            3
        ),
        HonourableAction.FACE_SUPERIOR_FOE: HonourReward(
            HonourableAction.FACE_SUPERIOR_FOE,
            "Stood against a superior enemy",
            15,
            8
        ),
        HonourableAction.COMPLETE_TRIAL: HonourReward(
            HonourableAction.COMPLETE_TRIAL,
            "Completed a clan trial successfully",
            20,
            10
        ),
        HonourableAction.DEFEAT_BOSS: HonourReward(
            HonourableAction.DEFEAT_BOSS,
            "Defeated the ultimate adversary",
            50,
            30
        ),
        HonourableAction.SAVE_THIA: HonourReward(
            HonourableAction.SAVE_THIA,
            "Protected Thia from danger",
            12,
            5
        ),
        HonourableAction.HONOURABLE_COMBAT: HonourReward(
            HonourableAction.HONOURABLE_COMBAT,
            "Fought with honour and skill",
            5,
            2
        ),
        HonourableAction.CLAN_SERVICE: HonourReward(
            HonourableAction.CLAN_SERVICE,
            "Performed service for the clan",
            7,
            4
        ),
        HonourableAction.TROPHY_OFFERING: HonourReward(
            HonourableAction.TROPHY_OFFERING,
            "Offered worthy trophy to clan elder",
            15,
            8
        ),
        HonourableAction.SELF_SACRIFICE: HonourReward(
            HonourableAction.SELF_SACRIFICE,
            "Risked self for greater good",
            25,
            15
        )
    }
    
    @classmethod
    def evaluate_action(cls, predator, action_result):
        violations = []
        
        if hasattr(action_result, 'combat_result') and action_result.combat_result:
            combat = action_result.combat_result
            target = combat.defender
            
            if hasattr(target, 'is_innocent') and target.is_innocent:
                violations.append(cls.RULES[ClanCodeViolation.HARM_INNOCENT])
            
            if hasattr(target, 'is_worthy_prey') and not target.is_worthy_prey:
                violations.append(cls.RULES[ClanCodeViolation.HUNT_UNWORTHY])
            
            if predator.stealth_active and hasattr(target, 'can_detect_stealth') and not target.can_detect_stealth:
                violations.append(cls.RULES[ClanCodeViolation.UNFAIR_ADVANTAGE])
        
        penalty_messages = []
        for violation in violations:
            message = violation.apply_penalty(predator)
            penalty_messages.append(message)
        
        return penalty_messages
    
    @classmethod
    def evaluate_combat_honour(cls, predator, target, combat_result):
        honour_events = []
        
        if not combat_result:
            return honour_events
        
        target_strength = cls.assess_target_strength(target)
        
        if combat_result.kill:
            if target_strength >= 3:
                reward = cls.REWARDS[HonourableAction.WORTHY_KILL]
                message = reward.apply_reward(predator)
                honour_events.append(('reward', message))
            elif target_strength <= 1:
                violation = cls.RULES[ClanCodeViolation.HUNT_UNWORTHY]
                message = violation.apply_penalty(predator)
                honour_events.append(('violation', message))
        
        if hasattr(target, 'name') and 'Boss' in target.__class__.__name__:
            reward = cls.REWARDS[HonourableAction.FACE_SUPERIOR_FOE]
            message = reward.apply_reward(predator)
            honour_events.append(('reward', message))
        
        return honour_events
    
    @classmethod
    def assess_target_strength(cls, target):
        strength = 0
        
        if hasattr(target, 'max_health'):
            if target.max_health >= 200:
                strength += 3
            elif target.max_health >= 100:
                strength += 2
            else:
                strength += 1
        
        if hasattr(target, 'weapons') and target.weapons:
            strength += len(target.weapons)
        
        if hasattr(target, 'special_abilities') and target.special_abilities:
            strength += 2
        
        if 'Boss' in target.__class__.__name__:
            strength += 5
        
        return strength
    
    @classmethod
    def evaluate_retreat(cls, predator, threat_level, health_percentage):
        if threat_level >= 3 and health_percentage < 20:
            return None
        
        if threat_level >= 4:
            violation = cls.RULES[ClanCodeViolation.RETREAT_FROM_WORTHY]
            return violation.apply_penalty(predator)
        
        if health_percentage > 50:
            violation = cls.RULES[ClanCodeViolation.COWARDICE]
            return violation.apply_penalty(predator)
        
        return None
    
    @classmethod
    def evaluate_ally_protection(cls, predator, ally, protected):
        if protected:
            reward = cls.REWARDS[HonourableAction.PROTECT_ALLY]
            return reward.apply_reward(predator)
        else:
            if hasattr(ally, 'name') and ally.name == "Thia":
                violation = cls.RULES[ClanCodeViolation.ABANDON_ALLY]
                return violation.apply_penalty(predator)
        return None
    
    @classmethod
    def evaluate_thia_assistance(cls, predator, action_type):
        if action_type in ['carry', 'protect', 'heal']:
            reward = cls.REWARDS[HonourableAction.SAVE_THIA]
            return reward.apply_reward(predator)
        return None
    
    @classmethod
    def get_clan_judgment(cls, predator):
        if predator.honour >= 100:
            return "Legendary Hunter - Songs will be sung of your deeds"
        elif predator.honour >= 80:
            return "Elder - Revered by all"
        elif predator.honour >= 60:
            return "Blooded - Respected warrior"
        elif predator.honour >= 40:
            return "Young Blood - Proving worth"
        elif predator.honour >= 20:
            return "Unblooded - Must prove themselves"
        elif predator.honour >= 0:
            return "Dishonoured - Barely tolerated"
        else:
            return "Exile - Cast out from clan"
    
    @classmethod
    def get_honour_tier(cls, honour):
        if honour >= 100:
            return 6
        elif honour >= 80:
            return 5
        elif honour >= 60:
            return 4
        elif honour >= 40:
            return 3
        elif honour >= 20:
            return 2
        elif honour >= 0:
            return 1
        else:
            return 0
    
    @classmethod
    def can_challenge_for_rank(cls, challenger_honour, target_honour):
        challenger_tier = cls.get_honour_tier(challenger_honour)
        target_tier = cls.get_honour_tier(target_honour)
        return challenger_tier >= target_tier - 1


class ClanRelationship(Enum):
    FATHER = "father"
    BROTHER = "brother"
    ELDER = "elder"
    RIVAL = "rival"
    MENTOR = "mentor"
    OUTCAST = "outcast"


class ClanReaction:
    
    def __init__(self, relationship, opinion_change, message, action_required=None):
        self.relationship = relationship
        self.opinion_change = opinion_change
        self.message = message
        self.action_required = action_required
        self.timestamp = 0
    
    def to_dict(self):
        return {
            'relationship': self.relationship.value,
            'opinion_change': self.opinion_change,
            'message': self.message,
            'action_required': self.action_required
        }


class HonourTracker:
    
    def __init__(self, agent):
        self.agent = agent
        self.honour_history = []
        self.violation_count = 0
        self.reward_count = 0
        self.highest_honour = 0
        self.lowest_honour = 0
        self.clan_standing = "neutral"
    
    def record_change(self, change_type, amount, reason):
        entry = {
            'type': change_type,
            'amount': amount,
            'reason': reason,
            'honour_after': self.agent.honour if hasattr(self.agent, 'honour') else 0,
            'timestamp': len(self.honour_history)
        }
        self.honour_history.append(entry)
        
        if change_type == 'violation':
            self.violation_count += 1
        elif change_type == 'reward':
            self.reward_count += 1
        
        current_honour = self.agent.honour if hasattr(self.agent, 'honour') else 0
        self.highest_honour = max(self.highest_honour, current_honour)
        self.lowest_honour = min(self.lowest_honour, current_honour)
        
        self.update_clan_standing()
    
    def update_clan_standing(self):
        if not hasattr(self.agent, 'honour'):
            return
        
        honour = self.agent.honour
        violation_ratio = self.violation_count / max(1, self.reward_count + self.violation_count)
        
        if honour >= 80 and violation_ratio < 0.1:
            self.clan_standing = "exemplary"
        elif honour >= 60 and violation_ratio < 0.2:
            self.clan_standing = "respected"
        elif honour >= 40:
            self.clan_standing = "accepted"
        elif honour >= 20:
            self.clan_standing = "probationary"
        elif honour >= 0:
            self.clan_standing = "shamed"
        else:
            self.clan_standing = "exiled"
    
    def get_summary(self):
        return {
            'current_honour': self.agent.honour if hasattr(self.agent, 'honour') else 0,
            'highest_honour': self.highest_honour,
            'lowest_honour': self.lowest_honour,
            'total_violations': self.violation_count,
            'total_rewards': self.reward_count,
            'clan_standing': self.clan_standing,
            'history_length': len(self.honour_history)
        }
    
    def get_recent_history(self, count=5):
        return self.honour_history[-count:]


class ClanTrialType(Enum):
    COMBAT_TRIAL = "combat_trial"
    HUNT_TRIAL = "hunt_trial"
    ENDURANCE_TRIAL = "endurance_trial"
    HONOUR_TRIAL = "honour_trial"
    RETRIEVAL_TRIAL = "retrieval_trial"


class ClanTrial:
    
    def __init__(self, trial_type, issuer, target, requirements):
        self.trial_type = trial_type
        self.issuer = issuer
        self.target = target
        self.requirements = requirements
        self.is_active = True
        self.is_completed = False
        self.is_failed = False
        self.progress = 0
        self.max_progress = requirements.get('target_count', 1)
        self.time_limit = requirements.get('time_limit', 100)
        self.elapsed_time = 0
        self.honour_reward = requirements.get('honour_reward', 20)
        self.honour_penalty = requirements.get('honour_penalty', 15)
    
    def update_progress(self, amount=1):
        if not self.is_active:
            return False
        
        self.progress += amount
        if self.progress >= self.max_progress:
            self.complete_trial()
            return True
        return False
    
    def tick_time(self):
        if not self.is_active:
            return
        
        self.elapsed_time += 1
        if self.elapsed_time >= self.time_limit:
            self.fail_trial()
    
    def complete_trial(self):
        self.is_active = False
        self.is_completed = True
        if hasattr(self.target, 'gain_honour'):
            self.target.gain_honour(self.honour_reward)
        return YautjaClanCode.REWARDS[HonourableAction.COMPLETE_TRIAL]
    
    def fail_trial(self):
        self.is_active = False
        self.is_failed = True
        if hasattr(self.target, 'lose_honour'):
            self.target.lose_honour(self.honour_penalty)
        return YautjaClanCode.RULES[ClanCodeViolation.DISHONOUR_CLAN]
    
    def get_status(self):
        return {
            'trial_type': self.trial_type.value,
            'issuer': self.issuer.name if self.issuer else 'Unknown',
            'progress': f"{self.progress}/{self.max_progress}",
            'time_remaining': self.time_limit - self.elapsed_time,
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'is_failed': self.is_failed
        }


class ClanTrialManager:
    
    def __init__(self):
        self.active_trials = []
        self.completed_trials = []
        self.failed_trials = []
    
    def create_combat_trial(self, issuer, target, kill_count=3, time_limit=50):
        requirements = {
            'target_count': kill_count,
            'time_limit': time_limit,
            'honour_reward': 25,
            'honour_penalty': 15,
            'description': f"Defeat {kill_count} worthy opponents"
        }
        trial = ClanTrial(ClanTrialType.COMBAT_TRIAL, issuer, target, requirements)
        self.active_trials.append(trial)
        return trial
    
    def create_hunt_trial(self, issuer, target, trophy_value=10, time_limit=60):
        requirements = {
            'target_count': trophy_value,
            'time_limit': time_limit,
            'honour_reward': 30,
            'honour_penalty': 20,
            'description': f"Collect trophies worth {trophy_value} honour"
        }
        trial = ClanTrial(ClanTrialType.HUNT_TRIAL, issuer, target, requirements)
        self.active_trials.append(trial)
        return trial
    
    def create_endurance_trial(self, issuer, target, survival_turns=30):
        requirements = {
            'target_count': survival_turns,
            'time_limit': survival_turns + 10,
            'honour_reward': 20,
            'honour_penalty': 10,
            'description': f"Survive {survival_turns} turns in hostile territory"
        }
        trial = ClanTrial(ClanTrialType.ENDURANCE_TRIAL, issuer, target, requirements)
        self.active_trials.append(trial)
        return trial
    
    def create_honour_trial(self, issuer, target, honour_gain=15, time_limit=40):
        requirements = {
            'target_count': honour_gain,
            'time_limit': time_limit,
            'honour_reward': 35,
            'honour_penalty': 25,
            'description': f"Gain {honour_gain} honour through worthy deeds"
        }
        trial = ClanTrial(ClanTrialType.HONOUR_TRIAL, issuer, target, requirements)
        self.active_trials.append(trial)
        return trial
    
    def create_retrieval_trial(self, issuer, target, target_x, target_y, time_limit=45):
        requirements = {
            'target_count': 1,
            'time_limit': time_limit,
            'honour_reward': 25,
            'honour_penalty': 15,
            'target_location': (target_x, target_y),
            'description': f"Reach location ({target_x}, {target_y}) and return"
        }
        trial = ClanTrial(ClanTrialType.RETRIEVAL_TRIAL, issuer, target, requirements)
        self.active_trials.append(trial)
        return trial
    
    def update_trials(self):
        for trial in self.active_trials[:]:
            trial.tick_time()
            if trial.is_completed:
                self.active_trials.remove(trial)
                self.completed_trials.append(trial)
            elif trial.is_failed:
                self.active_trials.remove(trial)
                self.failed_trials.append(trial)
    
    def notify_kill(self, agent, target):
        for trial in self.active_trials:
            if trial.target == agent and trial.trial_type == ClanTrialType.COMBAT_TRIAL:
                if YautjaClanCode.assess_target_strength(target) >= 2:
                    trial.update_progress(1)
    
    def notify_trophy(self, agent, trophy):
        for trial in self.active_trials:
            if trial.target == agent and trial.trial_type == ClanTrialType.HUNT_TRIAL:
                trophy_value = trophy.get_honour_value() if hasattr(trophy, 'get_honour_value') else trophy.get('value', 1)
                trial.update_progress(trophy_value)
    
    def notify_survival(self, agent):
        for trial in self.active_trials:
            if trial.target == agent and trial.trial_type == ClanTrialType.ENDURANCE_TRIAL:
                trial.update_progress(1)
    
    def notify_honour_change(self, agent, amount):
        if amount > 0:
            for trial in self.active_trials:
                if trial.target == agent and trial.trial_type == ClanTrialType.HONOUR_TRIAL:
                    trial.update_progress(amount)
    
    def notify_location_reached(self, agent, x, y):
        for trial in self.active_trials:
            if trial.target == agent and trial.trial_type == ClanTrialType.RETRIEVAL_TRIAL:
                target_loc = trial.requirements.get('target_location')
                if target_loc and target_loc == (x, y):
                    trial.update_progress(1)
    
    def get_active_trials_for(self, agent):
        return [t for t in self.active_trials if t.target == agent]
    
    def get_trial_summary(self):
        return {
            'active': len(self.active_trials),
            'completed': len(self.completed_trials),
            'failed': len(self.failed_trials),
            'total': len(self.active_trials) + len(self.completed_trials) + len(self.failed_trials)
        }