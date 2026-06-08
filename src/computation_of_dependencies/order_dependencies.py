
from collections.abc import Iterable
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction
from utilis.dataclasses_user_story import AtomicUserStoryRecord
from itertools import permutations


class OrderDependencies:
    def __init__(self) -> None:
        # self.equivalence_verb_dependency_mapping: dict[CrudAction, list[CrudAction]] = {
        #     CrudAction.CREATE: [CrudAction.CREATE], # a create action has no dependencies
        #     CrudAction.READ: [CrudAction.CREATE, CrudAction.READ],
        #     CrudAction.UPDATE: [CrudAction.CREATE, CrudAction.READ, CrudAction.UPDATE],
        #     CrudAction.DELETE: [CrudAction.CREATE, CrudAction.READ, CrudAction.UPDATE, CrudAction.DELETE],
        # }
        
        self.equivalence_verb_dependency_mapping: dict[CrudAction, list[CrudAction]] = {
            CrudAction.CREATE: [], # a create action has no dependencies
            CrudAction.READ: [CrudAction.CREATE],
            CrudAction.UPDATE: [CrudAction.CREATE, CrudAction.READ],
            CrudAction.DELETE: [CrudAction.CREATE, CrudAction.READ, CrudAction.UPDATE],
        }
        
        l: list[CrudAction] = [CrudAction.CREATE, CrudAction.READ, CrudAction.UPDATE]
        self.containment_verb_dependency_mapping: dict[CrudAction, list[CrudAction]] = {
            CrudAction.CREATE: l,
            CrudAction.READ: l,
            CrudAction.UPDATE: l,
            CrudAction.DELETE: l,
        }
    
    def order_dependencies(
            self, 
            us_data: list[AtomicUserStoryRecord], 
            equivalence_relations: list[tuple[str, str, bool]]
        ) -> list[tuple[str, str]]:
        
        def check_equivalence_relations(equivalence_relations: list[tuple[str, str, bool]]) -> None:
            temp: tuple[str, str] = "", ""
        
            for equivalence_relation in equivalence_relations:
                temp = (equivalence_relation[1], equivalence_relation[0])
                if temp in equivalence_relations:
                    raise ValueError(
                        "Equivalence relations must be unidirectional. "
                        f"Found both {equivalence_relation} and {temp} in equivalence relations."
                    )
        check_equivalence_relations(equivalence_relations)  
        pairs = permutations(us_data, 2)
        
        vice_versa_equivalence_relations: list[tuple[str, str, bool]] = []
        temp: tuple[str, str, bool] = None
        for _ in equivalence_relations:
            temp = (_[1], _[0], _[2])
            vice_versa_equivalence_relations.append(temp)
        
        equivalence_relations.extend(vice_versa_equivalence_relations)
        
        return OrderDependencies._compute_ordered_dependencies(
            pairs, 
            self.equivalence_verb_dependency_mapping, 
            equivalence_relations
        )
    
    def hierarchical_order_dependencies(self, 
            us_data: list[tuple[AtomicUserStoryRecord, AtomicUserStoryRecord]], 
            containment_relations: list[tuple[str, str, bool]]
        ) -> list[tuple[str, str]]:
        pairs = permutations(us_data, 2)
        
        return OrderDependencies._compute_ordered_dependencies(
            pairs, 
            self.containment_verb_dependency_mapping, 
            containment_relations
        )
    
    @staticmethod
    def _compute_ordered_dependencies(
            us_data_pairs: Iterable[tuple[AtomicUserStoryRecord, AtomicUserStoryRecord]],
            verb_dependency_mapping: dict[CrudAction, list[CrudAction]],
            relations: list[tuple[str, str, bool]]
        ) -> list[tuple[str, str]]:
        
        results: list[tuple[str, str]] = []
        temp: tuple[str, str, bool] = None
                
        action_one: CrudAction = CrudAction.UNKNOWN
        action_two: CrudAction = CrudAction.UNKNOWN
        
        entity_one: str = ""
        entity_two: str = ""
        
        lowercase_relations = [(src.lower().strip(), trg.lower().strip(), flag) for src, trg, flag in relations]
        relations = lowercase_relations   
                
        for us_one, us_two in us_data_pairs:
            if us_one == us_two:
                continue
            action_one = us_one.goal_action_crud
            action_two = us_two.goal_action_crud
            
            entity_one = us_one.goal_target.trg.named_element
            entity_two = us_two.goal_target.trg.named_element
            
            try: 
                if action_one in verb_dependency_mapping.get(action_two):
                    temp = (
                        entity_one.lower().strip(), 
                        entity_two.lower().strip(), 
                        True
                    )
                    if temp in relations:
                        results.append((us_one.story, us_two.story))
            except KeyError:
                raise ValueError(f"Unknown CRUD action found: {action_one} or {action_two}")
            except Exception as e:
                pass
                # print(f"Error processing user stories '{us_one.story}' and '{us_two.story}': {e}")                    
        return results