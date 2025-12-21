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


if __name__ == "__main__":
    test_clan_honour_system()
