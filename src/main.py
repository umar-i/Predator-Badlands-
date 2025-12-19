import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grid import Grid
from renderer import GridRenderer


def test_dek_actions():
    from predator import Dek, PredatorFather, PredatorBrother
    from creatures import WildlifeAgent
    from actions import ActionType, Direction
    from event_logger import EventLogger
    
    print("=" * 60)
    print("PREDATOR: BADLANDS SIMULATION")
    print("Phase 4: Dek Actions & Family Dynamics Test")
    print("=" * 60)
    
    grid = Grid(25, 25)
    grid.generate_terrain()
    renderer = GridRenderer(grid)
    logger = EventLogger()
    
    dek = Dek(5, 5)
    father = PredatorFather("Elder Kaail", 10, 10)
    brother = PredatorBrother("Cetanu", 8, 8)
    wildlife = WildlifeAgent("Desert Stalker", "predator", 6, 6)
    
    agents = [dek, father, brother, wildlife]
    
    for agent in agents:
        agent.set_grid(grid)
        grid.place_agent(agent, agent.x, agent.y)
    
    print(f"\nInitial Setup:")
    print(f"  {dek}")
    print(f"  {father} - Opinion of Dek: {father.opinion_of_dek}")
    print(f"  {brother} - Rivalry: {brother.rivalry_with_dek}")
    print(f"  {wildlife}")
    
    print(f"\nWorld Map:")
    renderer.render(use_colors=True)
    
    print(f"\n" + "=" * 60)
    print("Testing Dek's Actions")
    print("=" * 60)
    
    test_actions = [
        (ActionType.MOVE, Direction.EAST),
        (ActionType.ATTACK, wildlife),
        (ActionType.REST, None),
        (ActionType.STEALTH, None),
        (ActionType.MOVE, Direction.NORTH)
    ]
    
    for i, (action_type, target) in enumerate(test_actions):
        logger.increment_step()
        
        print(f"\nStep {i+1}: {dek.name} performs {action_type.value}")
        print(f"  Before: Health {dek.health}, Stamina {dek.stamina}, Honour {dek.honour}")
        
        result = dek.perform_action(action_type, target, target)
        logger.log_action(dek, result)
        
        print(f"  Result: {result.message}")
        print(f"  After: Health {dek.health}, Stamina {dek.stamina}, Honour {dek.honour}")
        
        if result.combat_result:
            print(f"  Combat: {result.combat_result.damage_dealt} damage to {result.combat_result.defender.name}")
            if result.combat_result.kill:
                print(f"  KILL! {result.combat_result.defender.name} defeated")
        
        if result.trophy_collected:
            trophy = result.trophy_collected
            print(f"  Trophy: {trophy.name} (+{trophy.get_honour_value()} honour)")
        
        father_reaction = father.judge_dek_action(dek, result)
        logger.log_clan_reaction(father, dek, father_reaction)
        print(f"  Father reaction: {father_reaction.message}")
        
        brother_reaction = brother.react_to_dek_success(dek, result)
        logger.log_clan_reaction(brother, dek, brother_reaction)
        print(f"  Brother reaction: {brother_reaction.message}")
        
        if not wildlife.is_alive and i == 1:
            print(f"  Trophy collection opportunity available!")
    
    print(f"\n" + "=" * 60)
    print("Final Status")
    print("=" * 60)
    
    print(f"\nDek Final Stats:")
    print(f"  {dek}")
    print(f"  Clan Rank: {dek.clan_rank}")
    print(f"  Trophies: {len(dek.trophies)}")
    
    print(f"\nFamily Relationships:")
    print(f"  Father Opinion: {father.opinion_of_dek} - {father.get_relationship_status()}")
    print(f"  Brother Rivalry: {brother.rivalry_with_dek} - {brother.get_relationship_status()}")
    
    print(f"\nSimulation Statistics:")
    summary = logger.get_simulation_summary()
    print(f"  Total Events: {summary['total_events']}")
    print(f"  Combat Events: {summary['event_breakdown'].get('combat', 0)}")
    print(f"  Kills: {summary['combat_stats']['total_kills']}")
    print(f"  Trophies: {summary['trophy_summary']['total_trophies']}")
    
    logger.export_events_json('data/phase4_test.json')
    print(f"\nEvent log exported to: data/phase4_test.json")
    
    print(f"\n" + "=" * 60)
    print("Phase 4 Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_dek_actions()
