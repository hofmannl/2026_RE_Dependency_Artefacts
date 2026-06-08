import unittest
import json
from computation_of_dependencies.order_dependencies import OrderDependencies
from utilis.dataclasses_user_story import AtomicUserStoryRecord

class OrderDependenciesTest(unittest.TestCase):
    def setUp(self):
        self.order_dependencies_computer = OrderDependencies()
        
        self.equivalence_relations: list[tuple[str, str, bool]] = [
            ("resource", "material", True),
            ("resource page", "page", True),
            ("resource page", "resource page", True),
            ("page", "resource page", False)
        ]
        
        self.containment_relations: list[tuple[str, str, bool]] = [
            ("resource", "material", False),
            ("material", "resource", False),
            ("resource page", "resource page", False),
            ("page", "resource page", True),
            ("resource page", "page", False)
        ]
        
        self.data_us_1 = AtomicUserStoryRecord.factory_direct_import(json.loads(
"""
    {
        "PID": "#G02#",
        "Text": "#G02# (First) As a UI designer, I want to design the resource page, so that it matches the new Broker design styles.",
        "Benefit": "it matches the new Broker design styles",
        "Persona": [
            "UI designer"
        ],
        "GoalActionCrud": "CREATE",
        "Action": {
            "Goal": [
                "design"
            ],
            "Benefit": [
                "matches"
            ]
        },
        "Entity": {
            "Goal": [
                "Resource page"
            ],
            "Benefit": [
                "new Broker design styles"
            ]
        },
        "Triggers": [
            [
                "UI designer",
                "design"
            ]
        ],
        "Targets": [
            [
                "design",
                "Resource page"
            ],
            [
                "matches",
                "new Broker design styles"
            ]
        ],
        "Contains": [
            [
                "Resource page",
                "new Broker design styles"
            ]
        ]
    }
"""))
        
        self.data_us_2 = AtomicUserStoryRecord.factory_direct_import(json.loads(
"""
    {
        "PID": "#G02#",
        "Text": "#G02# (Second) As a UI designer, I want to redesign the resource page, so that it matches the new Broker design styles.",
        "Benefit": "it matches the new Broker design styles",
        "Persona": [
            "UI designer"
        ],
        "GoalActionCrud": "UPDATE",
        "Action": {
            "Goal": [
                "redesign"
            ],
            "Benefit": [
                "matches"
            ]
        },
        "Entity": {
            "Goal": [
                "Resource page"
            ],
            "Benefit": [
                "new Broker design styles"
            ]
        },
        "Triggers": [
            [
                "UI designer",
                "redesign"
            ]
        ],
        "Targets": [
            [
                "redesign",
                "Resource page"
            ],
            [
                "matches",
                "new Broker design styles"
            ]
        ],
        "Contains": [
            [
                "Resource page",
                "new Broker design styles"
            ]
        ]
    }
"""))    
    
        self.data_us_3 = AtomicUserStoryRecord.factory_direct_import(json.loads(
"""
    {
        "PID": "#G02#",
        "Text": "#G02# (Third) As a UI designer, I want to redesign the page, so that it matches the new Broker design styles.",
        "Benefit": "it matches the new Broker design styles",
        "Persona": [
            "UI designer"
        ],
        "GoalActionCrud": "UPDATE",
        "Action": {
            "Goal": [
                "redesign"
            ],
            "Benefit": [
                "matches"
            ]
        },
        "Entity": {
            "Goal": [
                "page"
            ],
            "Benefit": [
                "new Broker design styles"
            ]
        },
        "Triggers": [
            [
                "UI designer",
                "redesign"
            ]
        ],
        "Targets": [
            [
                "redesign",
                "page"
            ],
            [
                "matches",
                "new Broker design styles"
            ]
        ],
        "Contains": [
            [
                "page",
                "new Broker design styles"
            ]
        ]
    }
"""))  
    
    def test_order_dependency(self):
        result = self.order_dependencies_computer.order_dependencies(
            [self.data_us_1, self.data_us_2],
            self.equivalence_relations
        )
        # The second US (redesign) depends on the first US (design)
        expected: tuple[str, str] = (
            "(First) As a UI designer, I want to design the resource page, so that it matches the new Broker design styles.", 
            "(Second) As a UI designer, I want to redesign the resource page, so that it matches the new Broker design styles."
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected)
        
    def test_negativ_order_dependency(self):
        result = self.order_dependencies_computer.order_dependencies(
            [self.data_us_2, self.data_us_1],
            self.equivalence_relations
        )
        # The first US (design (create)) should not depend on the second US (redesign (update))
        not_expected: tuple[str, str] = (
            "(Second) As a UI designer, I want to redesign the resource page, so that it matches the new Broker design styles.",
            "(First) As a UI designer, I want to design the resource page, so that it matches the new Broker design styles."
        )
        
        self.assertEqual(len(result), 1)
        self.assertNotEqual(result[0], not_expected)
        
    def test_hierarchical_order_dependency(self):
        result = self.order_dependencies_computer.hierarchical_order_dependencies(
            [self.data_us_2, self.data_us_3],
            self.containment_relations
        )
        
        expected: tuple[str, str] = (
            "(Third) As a UI designer, I want to redesign the page, so that it matches the new Broker design styles.", 
            "(Second) As a UI designer, I want to redesign the resource page, so that it matches the new Broker design styles."
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected)
        
    def test_negativ_hierarchical_order_dependency(self):
        result = self.order_dependencies_computer.hierarchical_order_dependencies(
            [self.data_us_2, self.data_us_3],
            self.containment_relations
        )
        
        not_expected: tuple[str, str] = (
            "(Second) As a UI designer, I want to redesign the resource page, so that it matches the new Broker design styles."
            "(Third) As a UI designer, I want to redesign the page, so that it matches the new Broker design styles.", 
        )
        
        self.assertEqual(len(result), 1)
        self.assertNotEqual(result[0], not_expected)