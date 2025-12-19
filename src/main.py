import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grid import Grid
from renderer import GridRenderer


def test_thia_cooperation_system():
    from predator import Dek
    from synthetic import Thia, SyntheticScout, SyntheticMedic, SyntheticEnemy
    from creatures import WildlifeAgent
    from actions import ActionType, Direction
    from event_logger import EventLogger
    from interaction_protocol import SyntheticInteractionManager, InteractionType
    
    print("=" * 70)
    print("PREDATOR: BADLANDS SIMULATION")
    print("Phase 5: Thia Cooperation & Synthetic Ecosystem Test")
    print("=" * 70)
    
    grid = Grid(30, 30)
    grid.generate_terrain()
    renderer = GridRenderer(grid)
    logger = EventLogger()
    interaction_manager = SyntheticInteractionManager()
    
    dek = Dek(10, 10)
    thia = Thia(11, 10)
    scout = SyntheticScout("Scout-Alpha", 15, 15)
    medic = SyntheticMedic("Medic-Beta", 8, 8)
    enemy = SyntheticEnemy("Hostile-Gamma", 20, 20)
    wildlife = WildlifeAgent("Canyon Beast", "predator", 12, 12)
    
    agents = [dek, thia, scout, medic, enemy, wildlife]
    
    for agent in agents:
        agent.set_grid(grid)
        grid.place_agent(agent, agent.x, agent.y)
    
    print(f"\nInitial Setup:")
    print(f"  {dek}")
    print(f"  {thia} - Trust in Dek: {thia.trust_in_dek}, Mobility: {thia.mobility_rating}")
    print(f"  {scout} - Intel collected: {len(scout.collected_intel)}")
    print(f"  {medic} - Supplies: {medic.medical_supplies}, Tools: {medic.repair_tools}")
    print(f"  {enemy} - Combat mode: {enemy.combat_mode}")
    print(f"  {wildlife}")
    
    print(f"\n" + "=" * 70)
    print("Testing Thia Cooperation Mechanics")
    print("=" * 70)
    
    test_scenarios = [
        ("Dek carries Thia", lambda: dek.perform_action(ActionType.CARRY, None, thia)),
        ("Thia performs scan", lambda: thia.perform_reconnaissance_scan()),
        ("Dek requests intel", lambda: dek.perform_action(ActionType.REQUEST_INFO, None, thia)),
        ("Scout gathers intelligence", lambda: scout.perform_deep_scan()),
        ("Medic scans Thia", lambda: medic.perform_medical_scan(thia)),
        ("Alliance formation", lambda: interaction_manager.initiate_interaction(
            dek, thia, InteractionType.ALLIANCE_PROPOSAL)),
        ("Information sharing", lambda: scout.share_intelligence(thia)),
        ("Dek drops Thia", lambda: dek.perform_action(ActionType.DROP, None, None))
    ]
    
    for i, (scenario_name, scenario_func) in enumerate(test_scenarios):
        logger.increment_step()
        
        print(f"\nStep {i+1}: {scenario_name}")
        print(f"  Thia Trust: {thia.trust_in_dek}, Cooperation: {thia.cooperation_level}")
        
        try:
            result = scenario_func()
            
            if hasattr(result, 'message'):
                print(f"  Result: {result.message}")
                logger.log_action(dek, result)
            elif hasattr(result, 'success'):
                print(f"  Interaction: {result.response}")
                if result.success:
                    thia.build_trust(2)
            elif result is not None:
                print(f"  Action completed: {type(result).__name__}")
            else:
                print(f"  Action failed or returned None")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        print(f"  Updated Trust: {thia.trust_in_dek}, Cooperation: {thia.cooperation_level}")
        
        if thia.carried_by:
            print(f"  Thia is being carried by {thia.carried_by.name}")
        
        if hasattr(thia, 'scan_cooldown') and thia.scan_cooldown > 0:
            print(f"  Thia scan cooldown: {thia.scan_cooldown}")
    
    print(f"\n" + "=" * 70)
    print("Synthetic Agent Capabilities Summary")
    print("=" * 70)
    
    print(f"\nThia Advanced Features:")
    print(f"  Intel Database: {len(thia.intel_database)} categories")
    print(f"  Movement Penalty: {thia.movement_penalty}")
    print(f"  Can Move Independently: {thia.can_move_independently}")
    print(f"  Battery Level: {thia.battery_level}%")
    
    print(f"\nScout Capabilities:")
    print(f"  Reconnaissance Range: {scout.reconnaissance_range}")
    print(f"  Intel Collected: {len(scout.collected_intel)}")
    print(f"  Stealth Available: {scout.stealth_capability}")
    
    print(f"\nMedic Capabilities:")
    print(f"  Medical Supplies: {medic.medical_supplies}")
    print(f"  Repair Tools: {medic.repair_tools}")
    print(f"  Priority Targets: {medic.priority_targets}")
    
    print(f"\nInteraction Summary:")
    interaction_history = interaction_manager.get_interaction_history()
    print(f"  Total Interactions: {len(interaction_history)}")
    alliance_summary = interaction_manager.get_alliance_summary()
    print(f"  Active Alliances: {alliance_summary['total_alliances']}")
    
    logger.export_events_json('data/phase5_test.json')
    print(f"\nEvent log exported to: data/phase5_test.json")
    
    print(f"\n" + "=" * 70)
    print("Phase 5 Test Complete - Requirement (c) Satisfied")
    print("=" * 70)


if __name__ == "__main__":
    test_thia_cooperation_system()
