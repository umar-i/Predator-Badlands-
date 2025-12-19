from enum import Enum


class ClanCodeViolation(Enum):
    HUNT_UNWORTHY = "hunting_unworthy"
    UNFAIR_ADVANTAGE = "unfair_advantage"
    TERRITORY_VIOLATION = "territory_violation"
    TROPHY_THEFT = "trophy_theft"
    HARM_INNOCENT = "harm_innocent"
    COWARDICE = "cowardice"
    DISHONOUR_CLAN = "dishonour_clan"


class ClanCodeRule:
    
    def __init__(self, rule_type, description, honour_penalty, severity="medium"):
        self.rule_type = rule_type
        self.description = description
        self.honour_penalty = honour_penalty
        self.severity = severity
    
    def apply_penalty(self, predator):
        predator.lose_honour(self.honour_penalty)
        return f"Violated {self.rule_type.value}: -{self.honour_penalty} honour"


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
    def get_clan_judgment(cls, predator):
        if predator.honour >= 80:
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


class ClanRelationship(Enum):
    FATHER = "father"
    BROTHER = "brother"
    ELDER = "elder"
    RIVAL = "rival"
    MENTOR = "mentor"


class ClanReaction:
    
    def __init__(self, relationship, opinion_change, message):
        self.relationship = relationship
        self.opinion_change = opinion_change
        self.message = message