import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from clan_code import (
    ClanCodeViolation, HonourableAction, ClanCodeRule, HonourReward,
    YautjaClanCode, ClanRelationship, ClanReaction, HonourTracker,
    ClanTrialType, ClanTrial
)
from predator import PredatorAgent


class TestClanCodeViolation(unittest.TestCase):
    
    def test_violation_values(self):
        self.assertEqual(ClanCodeViolation.HUNT_UNWORTHY.value, "hunting_unworthy")
        self.assertEqual(ClanCodeViolation.UNFAIR_ADVANTAGE.value, "unfair_advantage")
        self.assertEqual(ClanCodeViolation.TERRITORY_VIOLATION.value, "territory_violation")
        self.assertEqual(ClanCodeViolation.TROPHY_THEFT.value, "trophy_theft")
        self.assertEqual(ClanCodeViolation.HARM_INNOCENT.value, "harm_innocent")
    
    def test_all_violations_exist(self):
        violations = list(ClanCodeViolation)
        self.assertEqual(len(violations), 10)


class TestHonourableAction(unittest.TestCase):
    
    def test_honourable_action_values(self):
        self.assertEqual(HonourableAction.WORTHY_KILL.value, "worthy_kill")
        self.assertEqual(HonourableAction.PROTECT_ALLY.value, "protect_ally")
        self.assertEqual(HonourableAction.FACE_SUPERIOR_FOE.value, "face_superior_foe")
        self.assertEqual(HonourableAction.DEFEAT_BOSS.value, "defeat_boss")
    
    def test_all_actions_exist(self):
        actions = list(HonourableAction)
        self.assertEqual(len(actions), 10)


class TestClanCodeRule(unittest.TestCase):
    
    def test_rule_creation(self):
        rule = ClanCodeRule(
            ClanCodeViolation.HUNT_UNWORTHY,
            "Only hunt worthy prey",
            15,
            "high"
        )
        
        self.assertEqual(rule.rule_type, ClanCodeViolation.HUNT_UNWORTHY)
        self.assertEqual(rule.description, "Only hunt worthy prey")
        self.assertEqual(rule.honour_penalty, 15)
        self.assertEqual(rule.severity, "high")
    
    def test_apply_penalty(self):
        rule = ClanCodeRule(
            ClanCodeViolation.COWARDICE,
            "Face death with honour",
            12,
            "medium"
        )
        
        predator = PredatorAgent("Hunter")
        predator.honour = 50
        
        message = rule.apply_penalty(predator)
        
        self.assertEqual(predator.honour, 38)
        self.assertIn("cowardice", message.lower())


class TestHonourReward(unittest.TestCase):
    
    def test_reward_creation(self):
        reward = HonourReward(
            HonourableAction.WORTHY_KILL,
            "Defeated a worthy opponent",
            10,
            5
        )
        
        self.assertEqual(reward.action_type, HonourableAction.WORTHY_KILL)
        self.assertEqual(reward.honour_gain, 10)
        self.assertEqual(reward.reputation_gain, 5)
    
    def test_apply_reward(self):
        reward = HonourReward(
            HonourableAction.WORTHY_KILL,
            "Defeated worthy opponent",
            15,
            5
        )
        
        predator = PredatorAgent("Hunter")
        predator.honour = 20
        
        message = reward.apply_reward(predator)
        
        self.assertEqual(predator.honour, 35)
        self.assertIn("worthy_kill", message.lower())


class TestYautjaClanCodeRules(unittest.TestCase):
    
    def test_rules_defined(self):
        self.assertIn(ClanCodeViolation.HUNT_UNWORTHY, YautjaClanCode.RULES)
        self.assertIn(ClanCodeViolation.UNFAIR_ADVANTAGE, YautjaClanCode.RULES)
        self.assertIn(ClanCodeViolation.HARM_INNOCENT, YautjaClanCode.RULES)
    
    def test_hunt_unworthy_penalty(self):
        rule = YautjaClanCode.RULES[ClanCodeViolation.HUNT_UNWORTHY]
        self.assertEqual(rule.honour_penalty, 15)
        self.assertEqual(rule.severity, "high")
    
    def test_harm_innocent_penalty(self):
        rule = YautjaClanCode.RULES[ClanCodeViolation.HARM_INNOCENT]
        self.assertEqual(rule.honour_penalty, 30)
        self.assertEqual(rule.severity, "severe")
    
    def test_trophy_theft_penalty(self):
        rule = YautjaClanCode.RULES[ClanCodeViolation.TROPHY_THEFT]
        self.assertEqual(rule.honour_penalty, 25)
        self.assertEqual(rule.severity, "severe")


class TestYautjaClanCodeRewards(unittest.TestCase):
    
    def test_rewards_defined(self):
        self.assertIn(HonourableAction.WORTHY_KILL, YautjaClanCode.REWARDS)
        self.assertIn(HonourableAction.PROTECT_ALLY, YautjaClanCode.REWARDS)
        self.assertIn(HonourableAction.DEFEAT_BOSS, YautjaClanCode.REWARDS)
    
    def test_worthy_kill_reward(self):
        reward = YautjaClanCode.REWARDS[HonourableAction.WORTHY_KILL]
        self.assertEqual(reward.honour_gain, 10)
        self.assertEqual(reward.reputation_gain, 5)
    
    def test_defeat_boss_reward(self):
        reward = YautjaClanCode.REWARDS[HonourableAction.DEFEAT_BOSS]
        self.assertEqual(reward.honour_gain, 50)
        self.assertEqual(reward.reputation_gain, 30)
    
    def test_self_sacrifice_reward(self):
        reward = YautjaClanCode.REWARDS[HonourableAction.SELF_SACRIFICE]
        self.assertEqual(reward.honour_gain, 25)


class TestYautjaClanCodeMethods(unittest.TestCase):
    
    def test_assess_target_strength_weak(self):
        class WeakTarget:
            max_health = 50
            weapons = []
        
        strength = YautjaClanCode.assess_target_strength(WeakTarget())
        self.assertEqual(strength, 1)
    
    def test_assess_target_strength_medium(self):
        class MediumTarget:
            max_health = 120
            weapons = ["claws"]
        
        strength = YautjaClanCode.assess_target_strength(MediumTarget())
        self.assertEqual(strength, 3)
    
    def test_assess_target_strength_boss(self):
        class BossAdversary:
            max_health = 500
            weapons = []
            special_abilities = ["earthquake", "blast"]
        
        strength = YautjaClanCode.assess_target_strength(BossAdversary())
        self.assertEqual(strength, 10)
    
    def test_get_clan_judgment_legendary(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 120
        
        judgment = YautjaClanCode.get_clan_judgment(predator)
        self.assertIn("Legendary", judgment)
    
    def test_get_clan_judgment_elder(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 85
        
        judgment = YautjaClanCode.get_clan_judgment(predator)
        self.assertIn("Elder", judgment)
    
    def test_get_clan_judgment_blooded(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 65
        
        judgment = YautjaClanCode.get_clan_judgment(predator)
        self.assertIn("Blooded", judgment)
    
    def test_get_clan_judgment_dishonoured(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 5
        
        judgment = YautjaClanCode.get_clan_judgment(predator)
        self.assertIn("Dishonoured", judgment)
    
    def test_get_honour_tier(self):
        self.assertEqual(YautjaClanCode.get_honour_tier(120), 6)
        self.assertEqual(YautjaClanCode.get_honour_tier(85), 5)
        self.assertEqual(YautjaClanCode.get_honour_tier(65), 4)
        self.assertEqual(YautjaClanCode.get_honour_tier(45), 3)
        self.assertEqual(YautjaClanCode.get_honour_tier(25), 2)
        self.assertEqual(YautjaClanCode.get_honour_tier(10), 1)
        self.assertEqual(YautjaClanCode.get_honour_tier(-10), 0)
    
    def test_can_challenge_for_rank_same_tier(self):
        result = YautjaClanCode.can_challenge_for_rank(65, 65)
        self.assertTrue(result)
    
    def test_can_challenge_for_rank_one_below(self):
        result = YautjaClanCode.can_challenge_for_rank(45, 65)
        self.assertTrue(result)
    
    def test_cannot_challenge_two_tiers_below(self):
        result = YautjaClanCode.can_challenge_for_rank(25, 85)
        self.assertFalse(result)


class TestClanRelationship(unittest.TestCase):
    
    def test_relationship_values(self):
        self.assertEqual(ClanRelationship.FATHER.value, "father")
        self.assertEqual(ClanRelationship.BROTHER.value, "brother")
        self.assertEqual(ClanRelationship.ELDER.value, "elder")
        self.assertEqual(ClanRelationship.RIVAL.value, "rival")
        self.assertEqual(ClanRelationship.MENTOR.value, "mentor")
        self.assertEqual(ClanRelationship.OUTCAST.value, "outcast")


class TestClanReaction(unittest.TestCase):
    
    def test_reaction_creation(self):
        reaction = ClanReaction(
            ClanRelationship.FATHER,
            10,
            "Father approves of your actions",
            "promote"
        )
        
        self.assertEqual(reaction.relationship, ClanRelationship.FATHER)
        self.assertEqual(reaction.opinion_change, 10)
        self.assertEqual(reaction.message, "Father approves of your actions")
        self.assertEqual(reaction.action_required, "promote")
    
    def test_reaction_to_dict(self):
        reaction = ClanReaction(
            ClanRelationship.BROTHER,
            -5,
            "Brother is disappointed"
        )
        
        data = reaction.to_dict()
        
        self.assertEqual(data['relationship'], "brother")
        self.assertEqual(data['opinion_change'], -5)
        self.assertEqual(data['message'], "Brother is disappointed")


class TestHonourTracker(unittest.TestCase):
    
    def setUp(self):
        self.predator = PredatorAgent("Hunter")
        self.tracker = HonourTracker(self.predator)
    
    def test_tracker_creation(self):
        self.assertEqual(self.tracker.agent, self.predator)
        self.assertEqual(self.tracker.honour_history, [])
        self.assertEqual(self.tracker.violation_count, 0)
        self.assertEqual(self.tracker.reward_count, 0)
    
    def test_record_violation(self):
        self.tracker.record_change('violation', -15, "Hunted unworthy prey")
        
        self.assertEqual(self.tracker.violation_count, 1)
        self.assertEqual(len(self.tracker.honour_history), 1)
    
    def test_record_reward(self):
        self.tracker.record_change('reward', 10, "Worthy kill")
        
        self.assertEqual(self.tracker.reward_count, 1)
        self.assertEqual(len(self.tracker.honour_history), 1)
    
    def test_highest_honour_tracking(self):
        self.predator.honour = 50
        self.tracker.record_change('reward', 10, "Action")
        self.predator.honour = 30
        self.tracker.record_change('violation', -20, "Action")
        
        self.assertEqual(self.tracker.highest_honour, 50)
    
    def test_clan_standing_update(self):
        self.predator.honour = 85
        self.tracker.record_change('reward', 10, "Action")
        
        self.assertEqual(self.tracker.clan_standing, "exemplary")
    
    def test_get_summary(self):
        self.predator.honour = 40
        self.tracker.record_change('reward', 10, "Action")
        self.tracker.record_change('violation', -5, "Action")
        
        summary = self.tracker.get_summary()
        
        self.assertEqual(summary['current_honour'], 40)
        self.assertEqual(summary['total_violations'], 1)
        self.assertEqual(summary['total_rewards'], 1)
    
    def test_get_recent_history(self):
        for i in range(10):
            self.tracker.record_change('reward', 5, f"Action {i}")
        
        recent = self.tracker.get_recent_history(3)
        self.assertEqual(len(recent), 3)


class TestClanTrialType(unittest.TestCase):
    
    def test_trial_type_values(self):
        self.assertEqual(ClanTrialType.COMBAT_TRIAL.value, "combat_trial")
        self.assertEqual(ClanTrialType.HUNT_TRIAL.value, "hunt_trial")
        self.assertEqual(ClanTrialType.ENDURANCE_TRIAL.value, "endurance_trial")
        self.assertEqual(ClanTrialType.HONOUR_TRIAL.value, "honour_trial")
        self.assertEqual(ClanTrialType.RETRIEVAL_TRIAL.value, "retrieval_trial")


class TestClanTrial(unittest.TestCase):
    
    def setUp(self):
        self.issuer = PredatorAgent("Elder")
        self.target = PredatorAgent("Hunter")
        self.requirements = {
            'target_count': 3,
            'time_limit': 50,
            'honour_reward': 25,
            'honour_penalty': 10
        }
        self.trial = ClanTrial(
            ClanTrialType.HUNT_TRIAL,
            self.issuer,
            self.target,
            self.requirements
        )
    
    def test_trial_creation(self):
        self.assertEqual(self.trial.trial_type, ClanTrialType.HUNT_TRIAL)
        self.assertEqual(self.trial.issuer, self.issuer)
        self.assertEqual(self.trial.target, self.target)
        self.assertTrue(self.trial.is_active)
        self.assertFalse(self.trial.is_completed)
        self.assertFalse(self.trial.is_failed)
    
    def test_trial_requirements(self):
        self.assertEqual(self.trial.max_progress, 3)
        self.assertEqual(self.trial.time_limit, 50)
        self.assertEqual(self.trial.honour_reward, 25)
        self.assertEqual(self.trial.honour_penalty, 10)
    
    def test_update_progress(self):
        result = self.trial.update_progress(1)
        
        self.assertFalse(result)
        self.assertEqual(self.trial.progress, 1)
        self.assertTrue(self.trial.is_active)
    
    def test_update_progress_complete(self):
        self.target.honour = 0
        self.trial.update_progress(3)
        
        self.assertTrue(self.trial.is_completed)
        self.assertFalse(self.trial.is_active)
        self.assertEqual(self.target.honour, 25)
    
    def test_tick_time(self):
        self.trial.tick_time()
        self.assertEqual(self.trial.elapsed_time, 1)
    
    def test_tick_time_expires(self):
        self.target.honour = 50
        for _ in range(50):
            self.trial.tick_time()
        
        self.assertTrue(self.trial.is_failed)
        self.assertFalse(self.trial.is_active)
        self.assertEqual(self.target.honour, 40)
    
    def test_get_status(self):
        self.trial.update_progress(1)
        self.trial.tick_time()
        
        status = self.trial.get_status()
        
        self.assertEqual(status['trial_type'], "hunt_trial")
        self.assertEqual(status['issuer'], "Elder")
        self.assertEqual(status['progress'], "1/3")
        self.assertEqual(status['time_remaining'], 49)
        self.assertTrue(status['is_active'])


class TestYautjaClanCodeRetreat(unittest.TestCase):
    
    def test_retreat_allowed_low_health_high_threat(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 50
        
        result = YautjaClanCode.evaluate_retreat(predator, 4, 15)
        self.assertIsNone(result)
    
    def test_retreat_penalized_high_health(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 50
        
        result = YautjaClanCode.evaluate_retreat(predator, 2, 80)
        self.assertIsNotNone(result)
        self.assertLess(predator.honour, 50)


class TestYautjaClanCodeAllyProtection(unittest.TestCase):
    
    def test_protect_ally_reward(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 20
        
        class MockAlly:
            name = "Warrior"
        
        result = YautjaClanCode.evaluate_ally_protection(predator, MockAlly(), True)
        self.assertIsNotNone(result)
        self.assertGreater(predator.honour, 20)
    
    def test_abandon_thia_penalty(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 30
        
        class MockThia:
            name = "Thia"
        
        result = YautjaClanCode.evaluate_ally_protection(predator, MockThia(), False)
        self.assertIsNotNone(result)
        self.assertLess(predator.honour, 30)


class TestYautjaClanCodeThiaAssistance(unittest.TestCase):
    
    def test_carry_thia_reward(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 10
        
        result = YautjaClanCode.evaluate_thia_assistance(predator, 'carry')
        self.assertIsNotNone(result)
        self.assertGreater(predator.honour, 10)
    
    def test_protect_thia_reward(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 10
        
        result = YautjaClanCode.evaluate_thia_assistance(predator, 'protect')
        self.assertIsNotNone(result)
        self.assertGreater(predator.honour, 10)
    
    def test_other_action_no_reward(self):
        predator = PredatorAgent("Hunter")
        predator.honour = 10
        
        result = YautjaClanCode.evaluate_thia_assistance(predator, 'attack')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
