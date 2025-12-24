from agent import Agent
import random


class PredatorAgent(Agent):
    
    def __init__(self, name, x=0, y=0, max_health=150, max_stamina=120):
        super().__init__(name, x, y, max_health, max_stamina)
        self.honour = 0
        self.reputation = 0
        self.trophies = []
        self.clan_rank = "Unblooded"
        self.weapons = ["wrist_blades", "shoulder_cannon"]
        self.thermal_vision = True
        self.stealth_active = False
        
    @property
    def symbol(self):
        return 'P'
    
    def add_trophy(self, trophy):
        self.trophies.append(trophy)
        self.honour += trophy.get('value', 1)
    
    def gain_honour(self, amount):
        self.honour += amount
        self.update_rank()
    
    def lose_honour(self, amount):
        self.honour = max(0, self.honour - amount)
        self.update_rank()
    
    def update_rank(self):
        if self.honour >= 100:
            self.clan_rank = "Elder"
        elif self.honour >= 50:
            self.clan_rank = "Blooded"
        elif self.honour >= 10:
            self.clan_rank = "Young Blood"
        else:
            self.clan_rank = "Unblooded"
    
    def activate_stealth(self):
        if self.stamina >= 20:
            self.stealth_active = True
            self.consume_stamina(20)
    
    def deactivate_stealth(self):
        self.stealth_active = False
    
    def hunt_nearby_prey(self):
        if not self.grid:
            return None
        
        nearby_cells = self.grid.get_cells_in_radius(self.x, self.y, 3)
        prey_targets = []
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self:
                if hasattr(cell.occupant, 'is_prey') and cell.occupant.is_prey:
                    prey_targets.append(cell.occupant)
        
        return prey_targets
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if self.stamina < 30:
            return "rest"
        
        prey = self.hunt_nearby_prey()
        if prey:
            return "hunt"
        
        return "patrol"
    
    def patrol_movement(self):
        valid_moves = self.get_valid_moves()
        if valid_moves:
            target_x, target_y = random.choice(valid_moves)
            return self.move_to(target_x, target_y)
        return False
    
    def update(self):
        if self.stealth_active:
            self.consume_stamina(2)
            if self.stamina < 10:
                self.deactivate_stealth()
        
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(10)
        elif action == "patrol":
            self.patrol_movement()
        elif action == "hunt":
            self.hunt_behavior()
    
    def hunt_behavior(self):
        prey = self.hunt_nearby_prey()
        if prey:
            target = min(prey, key=lambda p: self.distance_to(p))
            if self.distance_to(target) == 1:
                self.attack_target(target)
            else:
                self.move_towards(target)
    
    def move_towards(self, target):
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            distance = self.distance_to_position(x, y)
            if distance < best_distance:
                best_distance = distance
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
    
    def attack_target(self, target):
        if self.distance_to(target) == 1:
            damage = random.randint(15, 25)
            target.take_damage(damage)
            if not target.is_alive:
                self.gain_honour(5)
                self.add_trophy({'type': 'kill', 'target': target.name, 'value': 3})


class Dek(PredatorAgent):
    
    def __init__(self, x=0, y=0):
        super().__init__("Dek", x, y, max_health=120, max_stamina=100)
        self.is_exiled = True
        self.carrying_thia = False
        self.thia_partner = None
        self.quest_progress = 0
        
        # Combat statistics tracking
        self.total_damage_dealt = 0
        self.kill_count = 0
        self.items_collected = 0
        
    @property
    def symbol(self):
        return 'D'
    
    def carry_thia(self, thia_agent):
        self.carrying_thia = True
        self.thia_partner = thia_agent
        self.max_stamina -= 20
    
    def drop_thia(self):
        self.carrying_thia = False
        if self.thia_partner:
            self.max_stamina += 20
            self.thia_partner = None
    
    def get_movement_cost(self, x, y):
        base_cost = super().get_movement_cost(x, y)
        if self.carrying_thia:
            base_cost *= 2
        return base_cost
    
    def perform_action(self, action_type, direction=None, target=None):
        from actions import ActionResult, ActionType, Direction, CombatResult, Trophy
        
        if not self.can_act():
            return ActionResult(action_type, False, 0, "Cannot act - not alive")
        
        if action_type == ActionType.MOVE:
            return self.perform_move(direction)
        elif action_type == ActionType.ATTACK:
            return self.perform_attack(target)
        elif action_type == ActionType.REST:
            return self.perform_rest()
        elif action_type == ActionType.COLLECT_TROPHY:
            return self.perform_collect_trophy(target)
        elif action_type == ActionType.STEALTH:
            return self.perform_stealth()
        elif action_type == ActionType.CARRY:
            return self.perform_carry(target)
        elif action_type == ActionType.DROP:
            return self.perform_drop()
        elif action_type == ActionType.SCAN:
            return self.perform_scan()
        elif action_type == ActionType.REQUEST_INFO:
            return self.perform_request_info(target)
        elif action_type == ActionType.SHARE_INFO:
            return self.perform_share_info(target)
        elif action_type == ActionType.FORM_ALLIANCE:
            return self.perform_form_alliance(target)
        
        return ActionResult(action_type, False, 0, "Unknown action type")
    
    def perform_move(self, direction):
        from actions import ActionResult, ActionType, Direction
        
        if direction not in Direction:
            return ActionResult(ActionType.MOVE, False, 0, "Invalid direction")
        
        dx, dy = direction.value
        new_x = self.x + dx
        new_y = self.y + dy
        
        base_cost = 5
        if self.carrying_thia:
            base_cost = 10
        
        if not self.consume_stamina(base_cost):
            return ActionResult(ActionType.MOVE, False, 0, "Insufficient stamina")
        
        if self.move_to(new_x, new_y):
            message = f"Moved {direction.name.lower()}"
            if self.carrying_thia:
                message += " (carrying Thia)"
            return ActionResult(ActionType.MOVE, True, base_cost, message)
        else:
            self.restore_stamina(base_cost)
            return ActionResult(ActionType.MOVE, False, 0, "Path blocked or invalid")
    
    def perform_attack(self, target):
        from actions import ActionResult, ActionType, CombatResult, Trophy
        import random
        
        if not target or not target.is_alive:
            return ActionResult(ActionType.ATTACK, False, 0, "No valid target")
        
        if self.distance_to(target) > 1:
            return ActionResult(ActionType.ATTACK, False, 0, "Target out of range")
        
        if not self.consume_stamina(15):
            return ActionResult(ActionType.ATTACK, False, 0, "Insufficient stamina for attack")
        
        base_damage = random.randint(20, 35)
        if self.stealth_active:
            base_damage = int(base_damage * 1.5)
            self.deactivate_stealth()
        
        target.take_damage(base_damage)
        
        # Track damage dealt
        self.total_damage_dealt += base_damage
        
        kill = not target.is_alive
        combat_result = CombatResult(self, target, base_damage, kill)
        
        result = ActionResult(ActionType.ATTACK, True, 15, f"Attacked {target.name}")
        result.add_combat_result(combat_result)
        
        if kill:
            self.kill_count += 1  # Track kills
            self.gain_honour(5)
            trophy = self.create_trophy_from_kill(target)
            if trophy:
                self.add_trophy(trophy)
                result.add_trophy(trophy)
        
        return result
    
    def perform_rest(self):
        from actions import ActionResult, ActionType
        
        stamina_gained = 20
        health_gained = 5
        
        self.restore_stamina(stamina_gained)
        self.heal(health_gained)
        
        message = f"Rested: +{stamina_gained} stamina, +{health_gained} health"
        return ActionResult(ActionType.REST, True, 0, message)
    
    def perform_collect_trophy(self, target):
        from actions import ActionResult, ActionType, Trophy
        
        if not target or target.is_alive:
            return ActionResult(ActionType.COLLECT_TROPHY, False, 0, "Target must be dead to collect trophy")
        
        if self.distance_to(target) > 1:
            return ActionResult(ActionType.COLLECT_TROPHY, False, 0, "Too far from target")
        
        if not self.consume_stamina(10):
            return ActionResult(ActionType.COLLECT_TROPHY, False, 0, "Insufficient stamina")
        
        trophy = self.create_trophy_from_kill(target)
        if trophy:
            self.add_trophy(trophy)
            result = ActionResult(ActionType.COLLECT_TROPHY, True, 10, f"Collected trophy from {target.name}")
            result.add_trophy(trophy)
            return result
        
        return ActionResult(ActionType.COLLECT_TROPHY, False, 10, "No trophy available")
    
    def perform_stealth(self):
        from actions import ActionResult, ActionType
        
        if self.stealth_active:
            self.deactivate_stealth()
            return ActionResult(ActionType.STEALTH, True, 0, "Stealth deactivated")
        else:
            if self.consume_stamina(25):
                self.activate_stealth()
                return ActionResult(ActionType.STEALTH, True, 25, "Stealth activated")
            else:
                return ActionResult(ActionType.STEALTH, False, 0, "Insufficient stamina for stealth")
    
    def perform_carry(self, target):
        from actions import ActionResult, ActionType
        
        if self.carrying_thia:
            return ActionResult(ActionType.CARRY, False, 0, "Already carrying Thia")
        
        if not hasattr(target, 'model') or target.name != "Thia":
            return ActionResult(ActionType.CARRY, False, 0, "Can only carry Thia")
        
        if self.distance_to(target) > 1:
            return ActionResult(ActionType.CARRY, False, 0, "Too far from Thia")
        
        self.carry_thia(target)
        target.be_carried_by(self)
        return ActionResult(ActionType.CARRY, True, 0, "Now carrying Thia")
    
    def perform_drop(self):
        from actions import ActionResult, ActionType
        
        if not self.carrying_thia:
            return ActionResult(ActionType.DROP, False, 0, "Not carrying anyone")
        
        thia = self.thia_partner
        self.drop_thia()
        thia.be_dropped()
        return ActionResult(ActionType.DROP, True, 0, "Dropped Thia")
    
    def perform_scan(self):
        from actions import ActionResult, ActionType
        
        if hasattr(self, 'thia_partner') and self.thia_partner and self.carrying_thia:
            scan_result = self.thia_partner.perform_reconnaissance_scan()
            if scan_result:
                return ActionResult(ActionType.SCAN, True, 0, f"Thia performed scan: found {len(scan_result['threats'])} threats")
            else:
                return ActionResult(ActionType.SCAN, False, 0, "Thia scan failed")
        
        return ActionResult(ActionType.SCAN, False, 0, "No scanning capability available")
    
    def perform_request_info(self, target):
        from actions import ActionResult, ActionType
        from interaction_protocol import SyntheticInteractionManager, InteractionType
        
        if not target or self.distance_to(target) > 3:
            return ActionResult(ActionType.REQUEST_INFO, False, 0, "Target out of range")
        
        manager = SyntheticInteractionManager()
        result = manager.initiate_interaction(
            self, target, InteractionType.INFO_REQUEST,
            {'topic': 'adversary_weakness'}
        )
        
        if result.success:
            return ActionResult(ActionType.REQUEST_INFO, True, 0, f"Received intel: {result.response}")
        else:
            return ActionResult(ActionType.REQUEST_INFO, False, 0, result.response)
    
    def perform_share_info(self, target):
        from actions import ActionResult, ActionType
        from interaction_protocol import SyntheticInteractionManager, InteractionType
        
        if not target or self.distance_to(target) > 3:
            return ActionResult(ActionType.SHARE_INFO, False, 0, "Target out of range")
        
        manager = SyntheticInteractionManager()
        result = manager.initiate_interaction(
            self, target, InteractionType.INFO_SHARE,
            {'key': 'clan_status', 'value': f'Honour: {self.honour}'}
        )
        
        if result.success:
            return ActionResult(ActionType.SHARE_INFO, True, 0, f"Shared information with {target.name}")
        else:
            return ActionResult(ActionType.SHARE_INFO, False, 0, result.response)
    
    def perform_form_alliance(self, target):
        from actions import ActionResult, ActionType
        from interaction_protocol import SyntheticInteractionManager, InteractionType
        
        if not target or self.distance_to(target) > 3:
            return ActionResult(ActionType.FORM_ALLIANCE, False, 0, "Target out of range")
        
        manager = SyntheticInteractionManager()
        result = manager.initiate_interaction(
            self, target, InteractionType.ALLIANCE_PROPOSAL
        )
        
        if result.success:
            manager.form_alliance(self, target)
            return ActionResult(ActionType.FORM_ALLIANCE, True, 0, f"Alliance formed with {target.name}")
        else:
            return ActionResult(ActionType.FORM_ALLIANCE, False, 0, result.response)
    
    def create_trophy_from_kill(self, target):
        from actions import Trophy
        import random
        
        trophy_types = {
            'WildlifeAgent': [('claw', 2), ('skull', 3)],
            'SyntheticAgent': [('circuit', 1), ('core', 4)],
            'BossAdversary': [('boss_part', 10), ('artifact', 15)]
        }
        
        target_class = target.__class__.__name__
        if target_class in trophy_types:
            trophy_options = trophy_types[target_class]
            trophy_name, trophy_value = random.choice(trophy_options)
            
            return Trophy(
                f"{target.name} {trophy_name}",
                trophy_name,
                trophy_value,
                target.name
            )
        
        return None
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if self.stamina < 20:
            return "rest"
        
        if self.quest_progress < 10:
            return "explore"
        
        return super().decide_action()
    
    def update(self):
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(8)
        elif action == "explore":
            self.exploration_movement()
            self.quest_progress += 1
        else:
            super().update()
    
    def exploration_movement(self):
        unexplored_moves = []
        for x, y in self.get_valid_moves():
            cell = self.grid.get_cell(x, y)
            if cell.terrain.terrain_type.name in ['TELEPORT', 'CANYON', 'ROCKY']:
                unexplored_moves.append((x, y))
        
        if unexplored_moves:
            target_x, target_y = random.choice(unexplored_moves)
            self.move_to(target_x, target_y)
        else:
            self.patrol_movement()


class PredatorFather(PredatorAgent):
    
    def __init__(self, name="Elder Kaail", x=0, y=0):
        super().__init__(name, x, y, max_health=180, max_stamina=140)
        self.clan_role = "Elder"
        self.territory_center = (x, y)
        self.patrol_radius = 8
        self.opinion_of_dek = -20
        self.disappointed_in_dek = True
        self.honour = 150
        self.clan_rank = "Elder"
        self.trial_manager = None
        self.last_judgment_turn = 0
        self.judgment_cooldown = 5
        self.approval_threshold = 30
        self.rejection_threshold = -30
        self.witnessed_actions = []
        self.dek_reference = None
        
    @property
    def symbol(self):
        return 'F'
    
    def set_trial_manager(self, manager):
        self.trial_manager = manager
    
    def set_dek_reference(self, dek):
        self.dek_reference = dek
    
    def judge_dek_action(self, dek, action_result):
        from clan_code import YautjaClanCode, ClanReaction, ClanRelationship, HonourableAction
        
        opinion_change = 0
        message = ""
        action_required = None
        
        if hasattr(action_result, 'combat_result') and action_result.combat_result:
            combat = action_result.combat_result
            target_strength = YautjaClanCode.assess_target_strength(combat.defender)
            
            if combat.kill:
                if target_strength >= 4:
                    opinion_change += 8
                    message = f"{self.name} is deeply impressed by Dek's worthy kill"
                elif target_strength >= 2:
                    opinion_change += 4
                    message = f"{self.name} approves of Dek's successful hunt"
                else:
                    opinion_change -= 2
                    message = f"{self.name} is unimpressed - the prey was weak"
            else:
                if target_strength >= 3:
                    opinion_change += 2
                    message = f"{self.name} respects Dek's courage against a strong foe"
                else:
                    opinion_change += 1
                    message = f"{self.name} acknowledges Dek's combat effort"
        
        if hasattr(action_result, 'trophy_collected') and action_result.trophy_collected:
            trophy = action_result.trophy_collected
            trophy_value = trophy.get_honour_value()
            if trophy_value >= 10:
                opinion_change += 10
                message = f"{self.name} is greatly honoured by Dek's trophy: {trophy.name}"
            elif trophy_value >= 5:
                opinion_change += 5
                message = f"{self.name} is impressed by Dek's trophy: {trophy.name}"
            else:
                opinion_change += 2
                message = f"{self.name} notes Dek's trophy collection"
        
        violations = YautjaClanCode.evaluate_action(dek, action_result)
        if violations:
            severity_penalty = len(violations) * 5
            opinion_change -= severity_penalty
            message = f"{self.name} is angered by clan code violations: {len(violations)} infractions"
            if self.opinion_of_dek + opinion_change < self.rejection_threshold:
                action_required = "exile_warning"
        
        if hasattr(dek, 'carrying_thia') and dek.carrying_thia:
            if hasattr(action_result, 'action_type'):
                action_name = action_result.action_type.value if hasattr(action_result.action_type, 'value') else str(action_result.action_type)
                if action_name in ['carry', 'protect']:
                    opinion_change += 3
                    message = f"{self.name} respects Dek's protection of his ally"
        
        self.opinion_of_dek += opinion_change
        self.disappointed_in_dek = self.opinion_of_dek < 0
        
        self.witnessed_actions.append({
            'action': action_result,
            'opinion_change': opinion_change,
            'message': message
        })
        
        if self.opinion_of_dek >= self.approval_threshold and not self.disappointed_in_dek:
            action_required = "approval_ceremony"
        
        return ClanReaction(ClanRelationship.FATHER, opinion_change, message, action_required)
    
    def issue_trial_to_dek(self, dek, trial_type="combat"):
        if not self.trial_manager:
            return None
        
        if trial_type == "combat":
            trial = self.trial_manager.create_combat_trial(self, dek, kill_count=2, time_limit=40)
        elif trial_type == "hunt":
            trial = self.trial_manager.create_hunt_trial(self, dek, trophy_value=8, time_limit=50)
        elif trial_type == "endurance":
            trial = self.trial_manager.create_endurance_trial(self, dek, survival_turns=25)
        elif trial_type == "honour":
            trial = self.trial_manager.create_honour_trial(self, dek, honour_gain=12, time_limit=35)
        else:
            return None
        
        return f"{self.name} issues {trial_type} trial to Dek: {trial.requirements.get('description', 'Complete the trial')}"
    
    def approve_dek(self, dek):
        from clan_code import YautjaClanCode, HonourableAction
        
        if self.opinion_of_dek < self.approval_threshold:
            return None
        
        reward = YautjaClanCode.REWARDS[HonourableAction.CLAN_SERVICE]
        reward.apply_reward(dek)
        
        self.disappointed_in_dek = False
        dek.is_exiled = False
        
        return f"{self.name} officially approves Dek's return to the clan with honour"
    
    def reject_dek(self, dek):
        from clan_code import YautjaClanCode, ClanCodeViolation
        
        if self.opinion_of_dek > self.rejection_threshold:
            return None
        
        violation = YautjaClanCode.RULES[ClanCodeViolation.DISHONOUR_CLAN]
        violation.apply_penalty(dek)
        
        dek.is_exiled = True
        
        return f"{self.name} formally rejects Dek - he remains in exile"
    
    def get_relationship_status(self):
        if self.opinion_of_dek >= 50:
            return "Proud father - Dek has proven worthy"
        elif self.opinion_of_dek >= 30:
            return "Approving - considers welcoming Dek back"
        elif self.opinion_of_dek >= 20:
            return "Cautiously optimistic about Dek"
        elif self.opinion_of_dek >= 0:
            return "Neutral - watching Dek's progress"
        elif self.opinion_of_dek >= -20:
            return "Disappointed but still hopeful"
        elif self.opinion_of_dek >= -30:
            return "Deeply ashamed of Dek's failures"
        else:
            return "Considering permanent exile for Dek"
    
    def challenge_dek(self, dek):
        if self.distance_to(dek) <= 2 and self.opinion_of_dek < -10:
            challenge_types = [
                ("combat", "Prove your worth in single combat"),
                ("hunt", "Bring me the skull of a worthy adversary"),
                ("honour", "Show the clan you understand honour"),
                ("endurance", "Survive the badlands without fleeing")
            ]
            challenge_index = abs(self.opinion_of_dek) % len(challenge_types)
            trial_type, challenge_text = challenge_types[challenge_index]
            
            if self.trial_manager:
                self.issue_trial_to_dek(dek, trial_type)
            
            return f"{self.name} challenges Dek: {challenge_text}"
        return None
    
    def observe_area(self):
        if not self.grid or not self.dek_reference:
            return None
        
        if self.distance_to(self.dek_reference) <= self.patrol_radius:
            return self.dek_reference
        return None
    
    def is_in_territory(self):
        distance = self.distance_to_position(self.territory_center[0], self.territory_center[1])
        return distance <= self.patrol_radius
    
    def return_to_territory(self):
        tx, ty = self.territory_center
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            dist = self.grid.calculate_distance(x, y, tx, ty)
            if dist < best_distance:
                best_distance = dist
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
    
    def aggressive_patrol(self):
        observed_dek = self.observe_area()
        if observed_dek and self.opinion_of_dek < -15:
            challenge = self.challenge_dek(observed_dek)
            if challenge:
                return
        
        self.patrol_movement()
    
    def dignified_patrol(self):
        observed_dek = self.observe_area()
        if observed_dek and self.opinion_of_dek >= self.approval_threshold:
            approval = self.approve_dek(observed_dek)
            if approval:
                return
        
        self.patrol_movement()
    
    def pursue_dek(self):
        if not self.dek_reference or not self.grid:
            return
        
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            dist = self.distance_to_position(x, y)
            if dist < best_distance:
                best_distance = dist
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if self.stamina < 30:
            return "rest"
        
        observed_dek = self.observe_area()
        
        if observed_dek:
            if self.opinion_of_dek < self.rejection_threshold:
                return "confront_dek"
            elif self.opinion_of_dek >= self.approval_threshold:
                return "approve_dek"
        
        if not self.is_in_territory():
            return "return_territory"
        
        if self.disappointed_in_dek:
            return "patrol_disapproving"
        
        return "patrol_elder"
    
    def update(self):
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(15)
        elif action == "return_territory":
            self.return_to_territory()
        elif action == "patrol_disapproving":
            self.aggressive_patrol()
        elif action == "patrol_elder":
            self.dignified_patrol()
        elif action == "confront_dek":
            self.pursue_dek()
        elif action == "approve_dek":
            if self.dek_reference:
                self.approve_dek(self.dek_reference)
        else:
            super().update()


class PredatorBrother(PredatorAgent):
    
    def __init__(self, name="Cetanu", x=0, y=0):
        super().__init__(name, x, y, max_health=160, max_stamina=130)
        self.clan_role = "Blooded Warrior"
        self.rivalry_with_dek = 15
        self.jealous_of_dek = False
        self.protective_of_dek = True
        self.honour = 75
        self.clan_rank = "Blooded"
        self.dek_reference = None
        self.recent_dek_kills = 0
        self.own_kills = 0
        self.duel_cooldown = 0
        self.protection_range = 5
        self.last_protection_turn = 0
        
    @property
    def symbol(self):
        return 'R'
    
    def set_dek_reference(self, dek):
        self.dek_reference = dek
    
    def react_to_dek_success(self, dek, action_result):
        from clan_code import ClanReaction, ClanRelationship, YautjaClanCode
        
        opinion_change = 0
        message = ""
        action_required = None
        
        if hasattr(action_result, 'trophy_collected') and action_result.trophy_collected:
            trophy = action_result.trophy_collected
            trophy_value = trophy.get_honour_value()
            
            if trophy_value > 8:
                self.jealous_of_dek = True
                self.rivalry_with_dek += 5
                self.protective_of_dek = False
                opinion_change = -3
                message = f"{self.name} grows intensely jealous of Dek's {trophy.name}"
            elif trophy_value > 5:
                self.rivalry_with_dek += 2
                opinion_change = -1
                message = f"{self.name} is envious of Dek's {trophy.name}"
            else:
                opinion_change = 1
                message = f"{self.name} acknowledges Dek's small victory"
        
        if hasattr(action_result, 'combat_result') and action_result.combat_result:
            combat = action_result.combat_result
            if combat.kill:
                self.recent_dek_kills += 1
                target_strength = YautjaClanCode.assess_target_strength(combat.defender)
                
                if target_strength >= 4:
                    self.rivalry_with_dek += 3
                    if self.protective_of_dek:
                        opinion_change = 3
                        message = f"{self.name} is proud but competitive after Dek's impressive kill"
                    else:
                        opinion_change = -2
                        self.jealous_of_dek = True
                        message = f"{self.name} burns with rivalry after Dek's kill"
                elif target_strength >= 2:
                    if self.protective_of_dek:
                        opinion_change = 2
                        message = f"{self.name} is proud of brother's kill"
                    else:
                        self.rivalry_with_dek += 1
                        message = f"{self.name} notes Dek's progress with mixed feelings"
        
        if self.recent_dek_kills > self.own_kills + 2:
            self.jealous_of_dek = True
            self.protective_of_dek = False
            action_required = "challenge_imminent"
        
        if self.rivalry_with_dek >= 30:
            action_required = "duel_challenge"
        
        return ClanReaction(ClanRelationship.BROTHER, opinion_change, message, action_required)
    
    def record_own_kill(self):
        self.own_kills += 1
        if self.own_kills > self.recent_dek_kills:
            self.jealous_of_dek = False
            if self.rivalry_with_dek > 10:
                self.rivalry_with_dek -= 2
    
    def get_relationship_status(self):
        if self.rivalry_with_dek >= 35:
            return "Bitter enemies - will attack on sight"
        elif self.rivalry_with_dek >= 30:
            return "Intense rivalry - sees Dek as threat"
        elif self.rivalry_with_dek >= 20:
            return "Strong competitive rivalry"
        elif self.rivalry_with_dek >= 15:
            return "Competitive sibling rivalry"
        elif self.rivalry_with_dek >= 5:
            return "Mild competition between brothers"
        else:
            return "Protective older brother"
    
    def challenge_dek_to_duel(self, dek):
        if self.duel_cooldown > 0:
            return None
        
        if self.rivalry_with_dek >= 25 and self.distance_to(dek) <= 3:
            self.duel_cooldown = 20
            
            duel_types = [
                "a hunt competition - first to claim a worthy trophy wins",
                "single combat - prove who is the superior warrior",
                "an endurance trial - last one standing in the badlands"
            ]
            duel_index = self.rivalry_with_dek % len(duel_types)
            
            return f"{self.name} challenges Dek to {duel_types[duel_index]}"
        return None
    
    def protect_dek(self, dek, threat):
        if not self.protective_of_dek:
            return None
        
        if self.distance_to(dek) <= self.protection_range:
            if hasattr(threat, 'is_alive') and threat.is_alive:
                threat_distance = self.distance_to(threat)
                dek_threat_distance = dek.distance_to(threat)
                
                if dek_threat_distance <= 2:
                    return f"{self.name} moves to intercept {threat.name} threatening Dek"
        return None
    
    def intercept_threat(self, threat):
        if not self.grid:
            return False
        
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            dist = self.grid.calculate_distance(x, y, threat.x, threat.y)
            if dist < best_distance:
                best_distance = dist
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
            return True
        return False
    
    def attack_threat(self, threat):
        if self.distance_to(threat) == 1:
            damage = random.randint(20, 35)
            threat.take_damage(damage)
            
            if not threat.is_alive:
                self.record_own_kill()
                self.gain_honour(5)
            return True
        return False
    
    def find_nearby_threats(self):
        if not self.grid or not self.dek_reference:
            return []
        
        threats = []
        nearby_cells = self.grid.get_cells_in_radius(self.dek_reference.x, self.dek_reference.y, self.protection_range)
        
        for cell in nearby_cells:
            if cell.occupant and cell.occupant != self and cell.occupant != self.dek_reference:
                agent = cell.occupant
                if hasattr(agent, 'hostile') and agent.hostile:
                    threats.append(agent)
                elif 'Boss' in agent.__class__.__name__:
                    threats.append(agent)
                elif 'Wildlife' in agent.__class__.__name__ and hasattr(agent, 'aggression_level'):
                    if agent.aggression_level > 0.5:
                        threats.append(agent)
        
        return threats
    
    def competitive_hunting(self):
        prey = self.hunt_nearby_prey()
        if prey:
            target = min(prey, key=lambda p: self.distance_to(p))
            if self.distance_to(target) == 1:
                self.attack_target(target)
                if not target.is_alive:
                    self.record_own_kill()
            else:
                self.move_towards(target)
        else:
            self.patrol_movement()
    
    def protective_patrol(self):
        if not self.dek_reference:
            self.patrol_movement()
            return
        
        threats = self.find_nearby_threats()
        
        if threats:
            nearest_threat = min(threats, key=lambda t: self.dek_reference.distance_to(t))
            
            if self.distance_to(nearest_threat) == 1:
                self.attack_threat(nearest_threat)
            else:
                self.intercept_threat(nearest_threat)
            return
        
        if self.distance_to(self.dek_reference) > self.protection_range:
            self.move_towards(self.dek_reference)
        else:
            self.patrol_movement()
    
    def pursue_dek_aggressively(self):
        if not self.dek_reference:
            return
        
        if self.distance_to(self.dek_reference) == 1:
            damage = random.randint(15, 25)
            self.dek_reference.take_damage(damage)
            self.rivalry_with_dek -= 5
        else:
            self.move_towards(self.dek_reference)
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if self.stamina < 25:
            return "rest"
        
        if self.duel_cooldown > 0:
            self.duel_cooldown -= 1
        
        if self.dek_reference and self.rivalry_with_dek >= 35:
            if self.distance_to(self.dek_reference) <= 5:
                return "attack_dek"
        
        if self.dek_reference and self.rivalry_with_dek >= 25:
            if self.distance_to(self.dek_reference) <= 3:
                challenge = self.challenge_dek_to_duel(self.dek_reference)
                if challenge:
                    return "challenge_dek"
        
        if self.jealous_of_dek:
            return "compete_with_dek"
        elif self.protective_of_dek:
            return "guard_dek"
        
        return "hunt_prey"
    
    def update(self):
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(12)
        elif action == "compete_with_dek":
            self.competitive_hunting()
        elif action == "guard_dek":
            self.protective_patrol()
        elif action == "hunt_prey":
            self.hunt_behavior()
        elif action == "attack_dek":
            self.pursue_dek_aggressively()
        elif action == "challenge_dek":
            pass
        else:
            super().update()


class PredatorClan(PredatorAgent):
    
    def __init__(self, name, x=0, y=0, clan_role="warrior"):
        super().__init__(name, x, y, max_health=140, max_stamina=110)
        self.clan_role = clan_role
        self.territory_center = (x, y)
        self.patrol_radius = 5
        self.loyalty_to_elder = 80
        self.opinion_of_dek = 0
        self.follows_father_judgment = True
        
    @property
    def symbol(self):
        return 'C'
    
    def follow_elder_judgment(self, father):
        if self.follows_father_judgment and hasattr(father, 'opinion_of_dek'):
            opinion_shift = (father.opinion_of_dek - self.opinion_of_dek) * 0.3
            self.opinion_of_dek += int(opinion_shift)
    
    def react_to_dek(self, dek):
        from clan_code import ClanReaction, ClanRelationship
        
        if self.opinion_of_dek >= 20:
            return ClanReaction(
                ClanRelationship.ELDER,
                1,
                f"{self.name} nods respectfully at Dek"
            )
        elif self.opinion_of_dek <= -20:
            return ClanReaction(
                ClanRelationship.RIVAL,
                -1,
                f"{self.name} turns away from the dishonoured Dek"
            )
        else:
            return ClanReaction(
                ClanRelationship.ELDER,
                0,
                f"{self.name} watches Dek silently"
            )
    
    def is_in_territory(self):
        distance = self.distance_to_position(self.territory_center[0], self.territory_center[1])
        return distance <= self.patrol_radius
    
    def return_to_territory(self):
        tx, ty = self.territory_center
        best_move = None
        best_distance = float('inf')
        
        for x, y in self.get_valid_moves():
            dist = self.grid.calculate_distance(x, y, tx, ty) if self.grid else float('inf')
            if dist < best_distance:
                best_distance = dist
                best_move = (x, y)
        
        if best_move:
            self.move_to(best_move[0], best_move[1])
    
    def aggressive_patrol(self):
        self.patrol_movement()
        if random.random() < 0.3:
            self.gain_honour(1)
    
    def dignified_patrol(self):
        self.patrol_movement()
    
    def decide_action(self):
        if not self.can_act():
            return "rest"
        
        if self.stamina < 20:
            return "rest"
        
        if not self.is_in_territory():
            return "return_territory"
        
        return super().decide_action()
    
    def update(self):
        action = self.decide_action()
        
        if action == "rest":
            self.restore_stamina(10)
        elif action == "return_territory":
            self.return_to_territory()
        else:
            super().update()