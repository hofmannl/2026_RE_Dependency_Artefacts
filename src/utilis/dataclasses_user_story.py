from dataclasses import dataclass, field
from abc import ABC
from utilis.util_functions import return_goal_part, remove_pid_from_text
from utilis.keys_us_part import KeyOfUserStoryPart
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction

@dataclass
class Persona:
    named_element: str = ""
    
    def __hash__(self) -> int:
        return hash("persona" +self.named_element)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Persona):
            return False
        return self.named_element == other.named_element
    
    def __str__(self) -> str:
        return self.named_element
    
@dataclass
class Action:
    named_element: str = ""
    
    def __hash__(self) -> int:
        return hash("action" + self.named_element)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Action):
            return False
        return self.named_element == other.named_element
    
    def __str__(self) -> str:
        return self.named_element
    
@dataclass
class Entity:
    named_element: str = ""
    
    def __hash__(self) -> int:
        return hash("entity" + self.named_element)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.named_element == other.named_element
    
    def __str__(self) -> str:
        return self.named_element
    
@dataclass
class Trigger:
    src: Persona = field(default_factory=Persona)
    trg: Action = field(default_factory=Action)
    
    def __hash__(self) -> int:
        return hash("trigger" + self.src.named_element + self.trg.named_element)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Trigger):
            return False
        return self.src == other.src and self.trg == other.trg
    
    def __str__(self) -> str:
        return f"{self.src} -> {self.trg}"
    
@dataclass
class Target:
    src: Action = field(default_factory=Action)
    trg: Entity = field(default_factory=Entity)
    
    def __hash__(self) -> int:
        return hash("target" + self.src.named_element + self.trg.named_element)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Target):
            return False
        return self.src == other.src and self.trg == other.trg
    
    def __str__(self) -> str:
        return f"{self.src} -> {self.trg}"

@dataclass
class Containment:
    src: Entity = field(default_factory=Entity)
    trg: Entity = field(default_factory=Entity)
    
    def __hash__(self) -> int:
        return hash("containment" + self.src.named_element + self.trg.named_element)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Containment):
            return False
        return self.src == other.src and self.trg == other.trg
    
    def __str__(self) -> str:
        return f"{self.src} -> {self.trg}"

@dataclass
class AbstractUserStoryRecord(ABC):
    pid: str = ""
    story: str = ""
    goal: str = ""
    benefit: str = ""
        
    triggers: list[Trigger] = field(default_factory=list)
    
@dataclass
class UserStoryRecord(AbstractUserStoryRecord):
    personas: list[Persona] = field(default_factory=list)
    
    ### -- Goal Part -- ###
    goal_actions: list[Action] = field(default_factory=list)
    goal_entities: list[Entity] = field(default_factory=list)
    
    goal_targets: list[Target] = field(default_factory=list)
    goal_contains: list[Containment] = field(default_factory=list)
    
    goal_action_crud: CrudAction = CrudAction.UNKNOWN 
    
    ### -- Benefit Part -- ###
    benefit_actions: list[Action] = field(default_factory=list)
    benefit_entities: list[Entity] = field(default_factory=list)
    
    benefit_targets: list[Target] = field(default_factory=list)
    benefit_contains: list[Containment] = field(default_factory=list)
    
    @staticmethod
    def factory_import(data: dict) -> 'UserStoryRecord':
        """Create UserStoryRecord from JSON data."""
        # Basic fields
        pid: str = data.get(KeyOfUserStoryPart.pid.value, "")
        story: str = data.get(KeyOfUserStoryPart.text.value, "")
        # remove from the story the pid and any # symbols
        story = remove_pid_from_text(story)
        
        benefit: str = data.get(KeyOfUserStoryPart.benefit_text.value, "")
        goal: str = return_goal_part(story) if benefit == "" else return_goal_part(story, benefit)        
        
        persona_names: list[str] = data.get(KeyOfUserStoryPart.persona.value, [])
        personas = [Persona(named_element=name) for name in persona_names]
                
        # Extract action and entity mappings
        action_data = data.get(KeyOfUserStoryPart.action.value, {})
        goal_action_names = action_data.get(KeyOfUserStoryPart.goal_part.value, [])
        benefit_action_names = action_data.get(KeyOfUserStoryPart.benefit_part.value, [])
        
        goal_action_crud: CrudAction = data.get(KeyOfUserStoryPart.goal_action_crud.value, CrudAction.UNKNOWN)
        if goal_action_crud and isinstance(goal_action_crud, str):
            goal_action_crud = CrudAction.from_string(goal_action_crud)
        
        entity_data = data.get(KeyOfUserStoryPart.entity.value, {})
        goal_entity_names = entity_data.get(KeyOfUserStoryPart.goal_part.value, [])
        benefit_entity_names = entity_data.get(KeyOfUserStoryPart.benefit_part.value, [])
        
        # Create goal and benefit actions/entities with deduplication
        # Build global actions map from goal actions first
        global_actions_map: dict[str, Action] = {}
        goal_actions: list[Action] = []
        for name in goal_action_names:
            action = Action(named_element=name)
            global_actions_map[name] = action
            goal_actions.append(action)
        
        # For benefit actions, reuse from global if exists, else create new
        benefit_actions: list[Action] = []
        for name in benefit_action_names:
            if name in global_actions_map:
                benefit_actions.append(global_actions_map[name])
            else:
                action = Action(named_element=name)
                global_actions_map[name] = action
                benefit_actions.append(action)
        
        # Same for entities
        global_entities_map: dict[str, Entity] = {}
        goal_entities: list[Entity] = []
        for name in goal_entity_names:
            entity = Entity(named_element=name)
            global_entities_map[name] = entity
            goal_entities.append(entity)
        
        benefit_entities: list[Entity] = []
        for name in benefit_entity_names:
            if name in global_entities_map:
                benefit_entities.append(global_entities_map[name])
            else:
                entity = Entity(named_element=name)
                global_entities_map[name] = entity
                benefit_entities.append(entity)
        
        # Create lookup maps for reuse
        goal_action_map = {action.named_element: action for action in goal_actions}
        benefit_action_map = {action.named_element: action for action in benefit_actions}
        goal_entity_map = {entity.named_element: entity for entity in goal_entities}
        benefit_entity_map = {entity.named_element: entity for entity in benefit_entities}
        
        # Create triggers - classify as goal or benefit
        triggers_data: list[tuple[str, str]] = data.get(KeyOfUserStoryPart.triggers.value, [])
        triggers: list[Trigger] = []
        for trigger in triggers_data:
            if len(trigger) != 2:
                continue
            persona_name, action_name = trigger[0], trigger[1]
            action: Action = goal_action_map.get(action_name, Action(named_element=action_name))
            for p in personas:
                if p.named_element == persona_name:
                    persona_trigger = p
                    break
            else:
                persona_trigger = Persona(named_element=persona_name)
            triggers.append(Trigger(src=persona_trigger, trg=action))
        
        # Create target tuples - classify as goal or benefit
        targets: list[tuple[str, str]] = data.get(KeyOfUserStoryPart.targets.value, [])
        goal_targets: list[Target] = []
        benefit_targets: list[Target] = []
        
        t: Target = Target()
        for target in targets:
            if len(target) != 2:
                continue
            action_name, entity_name = target[0], target[1]
            
            # Classify target as goal or benefit and reuse created objects
            if action_name in goal_action_map and entity_name in goal_entity_map:
                t = Target(src=goal_action_map[action_name], trg=goal_entity_map[entity_name])
                goal_targets.append(t)
            elif action_name in benefit_action_map and entity_name in benefit_entity_map:
                t = Target(src=benefit_action_map[action_name], trg=benefit_entity_map[entity_name])
                benefit_targets.append(t)
        
        # Create containment relationships - classify as goal or benefit
        contains: list[tuple[str, str]] = data.get(KeyOfUserStoryPart.contains.value, [])
        goal_contains: list[Containment] = []
        benefit_contains: list[Containment] = []
        
        for containment in contains:
            if len(containment) != 2:
                continue
            entity1_name, entity2_name = containment[0], containment[1]
            
            c: Containment = Containment()
            # Classify containment as goal or benefit and reuse created objects
            if entity1_name in goal_entity_map and entity2_name in goal_entity_map:
                c = Containment(src=goal_entity_map[entity1_name], trg=goal_entity_map[entity2_name])
                goal_contains.append(c)
            elif entity1_name in benefit_entity_map and entity2_name in benefit_entity_map:
                c = Containment(src=benefit_entity_map[entity1_name], trg=benefit_entity_map[entity2_name])
                benefit_contains.append(c)
        
        return UserStoryRecord(
            pid=pid,
            story=story,
            goal=goal,
            benefit=benefit,
            personas=personas,
            goal_actions=goal_actions,
            goal_action_crud=goal_action_crud,
            goal_entities=goal_entities,
            benefit_actions=benefit_actions,
            benefit_entities=benefit_entities,
            triggers=triggers,
            goal_targets=goal_targets,
            goal_contains=goal_contains,
            benefit_targets=benefit_targets,
            benefit_contains=benefit_contains
        )

@dataclass
class AtomicUserStoryRecord(AbstractUserStoryRecord):
    persona: Persona = field(default_factory=Persona)
    
    ### -- Goal Part -- ###
    goal_action: Action = field(default_factory=Action)
    goal_entities: list[Entity] = field(default_factory=list)
    
    goal_target: Target = field(default_factory=Target)
    goal_contains: list[Containment] = field(default_factory=list)
    
    goal_action_crud: CrudAction = CrudAction.UNKNOWN 
        
    ### -- Benefit Part -- ###
    benefit_action: Action = field(default_factory=Action)
    benefit_entities: list[Entity] = field(default_factory=list)
    
    benefit_target: Target = field(default_factory=Target)
    benefit_contains: list[Containment] = field(default_factory=list)
    
    @staticmethod
    def factory_import(data: UserStoryRecord) -> 'AtomicUserStoryRecord':
        return AtomicUserStoryRecord(
            pid=                data.pid,
            persona=            data.personas[0] if data.personas and len(data.personas) > 0 else Persona(),
            story=              data.story,
            goal=               data.goal,
            benefit=            data.benefit,
            triggers=           data.triggers,
            goal_action=        data.goal_actions[0] if data.goal_actions and len(data.goal_actions) > 0 else Action(),
            goal_action_crud=   data.goal_action_crud,
            goal_entities=      data.goal_entities,
            goal_target=        data.goal_targets[0] if data.goal_targets and len(data.goal_targets) > 0 else Target(),
            goal_contains=      data.goal_contains,
            benefit_action=     data.benefit_actions[0] if data.benefit_actions and len(data.benefit_actions) > 0 else Action(),
            benefit_entities=   data.benefit_entities,
            benefit_target=     data.benefit_targets[0] if data.benefit_targets and len(data.benefit_targets) > 0 else Target(),
            benefit_contains=   data.benefit_contains
        )
    
    @staticmethod
    def factory_bulk_import(data: list[UserStoryRecord]) -> list['AtomicUserStoryRecord']:
        return [AtomicUserStoryRecord.factory_import(us_record) for us_record in data]
    
    @staticmethod
    def factory_direct_import(data: dict) -> 'AtomicUserStoryRecord':
        us_record: UserStoryRecord = UserStoryRecord.factory_import(data)
        atomic_record: AtomicUserStoryRecord = AtomicUserStoryRecord.factory_import(us_record)
        return atomic_record
    
    @staticmethod
    def factory_bulk_direct_import(data: list[dict]) -> list['AtomicUserStoryRecord']:
        us_records: list[UserStoryRecord] = [UserStoryRecord.factory_import(item) for item in data]
        atomic_records: list[AtomicUserStoryRecord] = AtomicUserStoryRecord.factory_bulk_import(us_records)
        return atomic_records